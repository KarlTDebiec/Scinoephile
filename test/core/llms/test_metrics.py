#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for LLM completion metrics, reporting, and persistence."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from pytest import MonkeyPatch, raises

from scinoephile.core.llms import ChatCompletionMetrics
from scinoephile.core.llms import metrics as metrics_module
from scinoephile.core.llms.metrics import (
    format_chat_completion_metrics_report,
    get_chat_completion_metrics_summary,
    save_chat_completion_metrics_to_json,
)


def test_completion_metrics_persistence_is_atomic(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Test a failed JSON write preserves the prior output and removes its temporary.

    Arguments:
        tmp_path: temporary directory path
        monkeypatch: pytest monkeypatch fixture
    """
    output_path = tmp_path / "llm_usage.json"
    output_path.write_text("original", encoding="utf-8")

    def fail_dump(*args: object, **kwargs: object):
        """Fail while serializing the replacement JSON.

        Arguments:
            *args: ignored positional arguments
            **kwargs: ignored keyword arguments
        Raises:
            RuntimeError: always
        """
        _ = (args, kwargs)
        raise RuntimeError("serialization failed")

    monkeypatch.setattr(metrics_module.json, "dump", fail_dump)

    with raises(RuntimeError, match="serialization failed"):
        save_chat_completion_metrics_to_json(output_path, [_get_metrics()])

    assert output_path.read_text(encoding="utf-8") == "original"
    assert not list(tmp_path.glob(".llm_usage.json.*.tmp"))


def test_completion_metrics_persistence_includes_summary_and_details(tmp_path: Path):
    """Persist overall, per-operation, and raw completion metrics.

    Arguments:
        tmp_path: temporary directory path
    """
    metrics = (
        _get_metrics(query_attempt=1, cached_input_tokens=60),
        _get_metrics(query_attempt=2, cached_input_tokens=80),
    )
    output_path = tmp_path / "json" / "llm_usage.json"

    save_chat_completion_metrics_to_json(output_path, metrics)

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["summary"]["queries"] == 1
    assert data["summary"]["validation_retries"] == 1
    assert data["by_operation"]["multi_review"]["total_tokens"] == 220
    assert data["completions"][0]["query_key_sha256"] == "abc"
    report = format_chat_completion_metrics_report(metrics)
    assert "all: queries=1, completions=2" in report
    assert "multi_review: queries=1, completions=2" in report


def test_completion_metrics_summary_groups_retries_and_tokens():
    """Aggregate query attempts, transport retries, tokens, and latency."""
    metrics = (
        _get_metrics(query_attempt=1, cached_input_tokens=60),
        _get_metrics(query_attempt=2, cached_input_tokens=80, transport_retries=1),
        _get_metrics(
            operation="gap_translation", query_key_sha256="def", cached_input_tokens=0
        ),
    )

    summary = get_chat_completion_metrics_summary(metrics)

    assert summary == {
        "queries": 2,
        "completions": 3,
        "validation_retries": 1,
        "transport_retries": 1,
        "input_tokens": 300,
        "cached_input_tokens": 140,
        "uncached_input_tokens": 160,
        "cache_write_tokens": 0,
        "output_tokens": 30,
        "reasoning_tokens": 6,
        "total_tokens": 330,
        "latency_seconds": 3.75,
    }


def test_completion_metrics_summary_preserves_unknown_values():
    """Test one missing completion value makes its aggregate unavailable."""
    missing = replace(
        _get_metrics(),
        input_tokens=None,
        cached_input_tokens=None,
        cache_write_tokens=None,
        output_tokens=None,
        reasoning_tokens=None,
        total_tokens=None,
        transport_retries=None,
    )

    summary = get_chat_completion_metrics_summary((_get_metrics(), missing))

    assert summary["transport_retries"] is None
    assert summary["input_tokens"] is None
    assert summary["cached_input_tokens"] is None
    assert summary["uncached_input_tokens"] is None
    assert summary["cache_write_tokens"] is None
    assert summary["output_tokens"] is None
    assert summary["reasoning_tokens"] is None
    assert summary["total_tokens"] is None
    assert "transport_retries=n/a" in format_chat_completion_metrics_report(
        (_get_metrics(), missing)
    )


def _get_metrics(
    *,
    operation: str = "multi_review",
    query_key_sha256: str = "abc",
    query_attempt: int = 1,
    cached_input_tokens: int = 0,
    transport_retries: int = 0,
) -> ChatCompletionMetrics:
    """Construct completion metrics for tests.

    Arguments:
        operation: stable operation identifier
        query_key_sha256: semantic query digest
        query_attempt: one-based query attempt
        cached_input_tokens: prompt tokens served from cache
        transport_retries: provider SDK transport retries
    Returns:
        completion metrics fixture
    """
    return ChatCompletionMetrics(
        operation=operation,
        query_key_sha256=query_key_sha256,
        model="test-model",
        query_attempt=query_attempt,
        tool_round=1,
        input_tokens=100,
        cached_input_tokens=cached_input_tokens,
        cache_write_tokens=0,
        output_tokens=10,
        reasoning_tokens=2,
        total_tokens=110,
        transport_retries=transport_retries,
        latency_seconds=1.25,
        prompt_cache_key="cache-key",
    )
