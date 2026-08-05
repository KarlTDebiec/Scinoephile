#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Metrics, reporting, and persistence for LLM completions."""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TypedDict

from scinoephile.common.file import open_atomic_text_file

__all__ = [
    "ChatCompletionMetrics",
    "ChatCompletionMetricsSummary",
    "format_chat_completion_metrics_report",
    "get_chat_completion_metrics_summary",
    "save_chat_completion_metrics_to_json",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class ChatCompletionMetrics:
    """Usage and timing recorded for one provider completion."""

    operation: str | None
    """Stable LLM operation identifier, if supplied by the queryer."""
    query_key_sha256: str | None
    """SHA-256 digest of the semantic query key, if supplied by the queryer."""
    model: str
    """Model identifier."""
    query_attempt: int
    """One-based answer-validation attempt."""
    tool_round: int
    """One-based tool-calling round within the query attempt."""
    input_tokens: int | None
    """Total input tokens, if reported by the provider."""
    cached_input_tokens: int | None
    """Input tokens read from the provider prompt cache, if reported."""
    cache_write_tokens: int | None
    """Input tokens written to the provider prompt cache, if reported."""
    output_tokens: int | None
    """Total output tokens, if reported by the provider."""
    reasoning_tokens: int | None
    """Output tokens used for reasoning, if reported by the provider."""
    total_tokens: int | None
    """Total input and output tokens, if reported by the provider."""
    transport_retries: int | None
    """Transport retries taken by the provider SDK, if reported."""
    latency_seconds: float
    """Wall-clock completion latency in seconds."""
    prompt_cache_key: str | None
    """Provider prompt-cache routing key, if used."""


class ChatCompletionMetricsSummary(TypedDict):
    """Aggregate LLM completion metrics suitable for JSON serialization."""

    queries: int
    """Number of unique semantic queries sent to a provider."""
    completions: int
    """Number of successful provider completions, including tool rounds."""
    validation_retries: int
    """Number of additional answer-validation attempts after the first."""
    transport_retries: int | None
    """Total provider SDK transport retries, or None when unavailable."""
    input_tokens: int | None
    """Total input tokens, or None when unavailable."""
    cached_input_tokens: int | None
    """Total input tokens read from provider prompt caches, or None."""
    uncached_input_tokens: int | None
    """Total input tokens not read from provider prompt caches, or None."""
    cache_write_tokens: int | None
    """Total input tokens written to provider prompt caches, or None."""
    output_tokens: int | None
    """Total output tokens, or None when unavailable."""
    reasoning_tokens: int | None
    """Total output tokens used for reasoning, or None when unavailable."""
    total_tokens: int | None
    """Total input and output tokens, or None when unavailable."""
    latency_seconds: float
    """Total provider latency in seconds."""


def format_chat_completion_metrics_report(
    metrics: Iterable[ChatCompletionMetrics],
) -> str:
    """Format detailed completion metrics as a readable aggregate report.

    Arguments:
        metrics: completion metrics to summarize
    Returns:
        readable overall and per-operation report
    """
    metrics = tuple(metrics)
    summary = get_chat_completion_metrics_summary(metrics)
    lines = ["LLM query performance:", _format_summary_line("all", summary)]

    metrics_by_operation: dict[str, list[ChatCompletionMetrics]] = defaultdict(list)
    for completion_metrics in metrics:
        operation = completion_metrics.operation or "unknown"
        metrics_by_operation[operation].append(completion_metrics)
    for operation in sorted(metrics_by_operation):
        operation_summary = get_chat_completion_metrics_summary(
            metrics_by_operation[operation]
        )
        lines.append(_format_summary_line(operation, operation_summary))
    return "\n".join(lines)


def get_chat_completion_metrics_summary(
    metrics: Iterable[ChatCompletionMetrics],
) -> ChatCompletionMetricsSummary:
    """Aggregate completion metrics.

    Arguments:
        metrics: completion metrics to aggregate
    Returns:
        aggregate query, token, retry, and latency metrics
    """
    metrics = tuple(metrics)
    query_attempts_by_key: dict[tuple[str, str], int] = {}
    anonymous_queries = 0
    for completion_metrics in metrics:
        operation = completion_metrics.operation or "unknown"
        if completion_metrics.query_key_sha256 is None:
            anonymous_queries += 1
            continue
        query_key = (operation, completion_metrics.query_key_sha256)
        query_attempts_by_key[query_key] = max(
            query_attempts_by_key.get(query_key, 0), completion_metrics.query_attempt
        )

    input_tokens = _sum_optional(
        completion_metrics.input_tokens for completion_metrics in metrics
    )
    cached_input_tokens = _sum_optional(
        completion_metrics.cached_input_tokens for completion_metrics in metrics
    )
    uncached_input_tokens = None
    if input_tokens is not None and cached_input_tokens is not None:
        uncached_input_tokens = input_tokens - cached_input_tokens

    return {
        "queries": len(query_attempts_by_key) + anonymous_queries,
        "completions": len(metrics),
        "validation_retries": sum(
            max(query_attempts - 1, 0)
            for query_attempts in query_attempts_by_key.values()
        ),
        "transport_retries": _sum_optional(
            completion_metrics.transport_retries for completion_metrics in metrics
        ),
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "uncached_input_tokens": uncached_input_tokens,
        "cache_write_tokens": _sum_optional(
            completion_metrics.cache_write_tokens for completion_metrics in metrics
        ),
        "output_tokens": _sum_optional(
            completion_metrics.output_tokens for completion_metrics in metrics
        ),
        "reasoning_tokens": _sum_optional(
            completion_metrics.reasoning_tokens for completion_metrics in metrics
        ),
        "total_tokens": _sum_optional(
            completion_metrics.total_tokens for completion_metrics in metrics
        ),
        "latency_seconds": sum(
            completion_metrics.latency_seconds for completion_metrics in metrics
        ),
    }


def save_chat_completion_metrics_to_json(
    output_path: Path, metrics: Iterable[ChatCompletionMetrics]
):
    """Persist raw and aggregate completion metrics atomically.

    Arguments:
        output_path: JSON path to which to save
        metrics: completion metrics to persist
    """
    metrics = tuple(metrics)
    metrics_by_operation: dict[str, list[ChatCompletionMetrics]] = defaultdict(list)
    for completion_metrics in metrics:
        operation = completion_metrics.operation or "unknown"
        metrics_by_operation[operation].append(completion_metrics)
    data = {
        "summary": get_chat_completion_metrics_summary(metrics),
        "by_operation": {
            operation: get_chat_completion_metrics_summary(operation_metrics)
            for operation, operation_metrics in sorted(metrics_by_operation.items())
        },
        "completions": [asdict(completion_metrics) for completion_metrics in metrics],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open_atomic_text_file(output_path) as temp_file:
        json.dump(data, temp_file, ensure_ascii=False, indent=2)


def _format_optional(value: int | None) -> str:
    """Format an optional integer metric.

    Arguments:
        value: optional integer
    Returns:
        decimal integer or n/a
    """
    if value is None:
        return "n/a"
    return str(value)


def _format_summary_line(label: str, summary: ChatCompletionMetricsSummary) -> str:
    """Format one aggregate summary line.

    Arguments:
        label: overall or operation label
        summary: aggregate completion metrics
    Returns:
        formatted summary line
    """
    return (
        f"{label}: queries={summary['queries']}, "
        f"completions={summary['completions']}, "
        f"validation_retries={summary['validation_retries']}, "
        f"transport_retries={_format_optional(summary['transport_retries'])}, "
        f"input_tokens={_format_optional(summary['input_tokens'])}, "
        f"cached_input_tokens={_format_optional(summary['cached_input_tokens'])}, "
        f"uncached_input_tokens={_format_optional(summary['uncached_input_tokens'])}, "
        f"cache_write_tokens={_format_optional(summary['cache_write_tokens'])}, "
        f"output_tokens={_format_optional(summary['output_tokens'])}, "
        f"reasoning_tokens={_format_optional(summary['reasoning_tokens'])}, "
        f"total_tokens={_format_optional(summary['total_tokens'])}, "
        f"latency_seconds={summary['latency_seconds']:.2f}"
    )


def _sum_optional(values: Iterable[int | None]) -> int | None:
    """Sum optional integers only when every value is present.

    Arguments:
        values: optional integers to aggregate
    Returns:
        sum when all values are available, otherwise None
    """
    values_to_sum: list[int] = []
    for value in values:
        if value is None:
            return None
        values_to_sum.append(value)
    return sum(values_to_sum)
