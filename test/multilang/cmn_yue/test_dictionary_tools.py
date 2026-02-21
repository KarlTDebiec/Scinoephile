#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for in-process CUHK dictionary tool helpers."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from scinoephile.multilang.cmn_yue import dictionary_tools
from scinoephile.multilang.cmn_yue.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
)


class _FakeService:
    """Test double for CuhkDictionaryService."""

    init_calls: list[bool] = []
    lookup_calls: list[tuple[str, str, int]] = []

    def __init__(self, auto_build_missing: bool = False, **kwargs):
        """Initialize fake service.

        Arguments:
            auto_build_missing: whether missing data should be auto-built
            **kwargs: ignored keyword arguments
        """
        _ = kwargs
        self.auto_build_missing = auto_build_missing
        self.database_path = Path("/tmp/fake_cuhk.db")
        type(self).init_calls.append(auto_build_missing)

    def lookup(self, query: str, direction, limit: int = 10) -> list[DictionaryEntry]:
        """Track lookup calls and return deterministic payload.

        Arguments:
            query: lookup query
            direction: lookup direction enum
            limit: max entries
        Returns:
            deterministic one-entry payload
        """
        type(self).lookup_calls.append((query, direction.value, limit))
        return [
            DictionaryEntry(
                traditional="巴士",
                simplified="巴士",
                pinyin="ba1 shi4",
                jyutping="baa1 si6",
                frequency=0.0,
                definitions=[DictionaryDefinition(text="bus", label="名詞")],
            )
        ]


def _reset_fake_service_calls():
    """Reset fake-service call logs."""
    _FakeService.init_calls.clear()
    _FakeService.lookup_calls.clear()


def test_lookup_cuhk_dictionary_auto_builds_when_missing(monkeypatch):
    """Test lookup helper enables auto-build when creating service."""
    _reset_fake_service_calls()
    monkeypatch.setattr(dictionary_tools, "CuhkDictionaryService", _FakeService)

    response = dictionary_tools.lookup_cuhk_dictionary(
        query="巴士",
        direction="mandarin_to_cantonese",
        limit=5,
    )

    assert _FakeService.init_calls == [True]
    assert _FakeService.lookup_calls == [("巴士", "mandarin_to_cantonese", 5)]
    assert response["result_count"] == 1
    entries = response["entries"]
    assert isinstance(entries, list)
    first_entry = cast("dict[str, object]", entries[0])
    assert isinstance(first_entry, dict)
    assert first_entry["traditional"] == "巴士"


def test_lookup_cuhk_dictionary_rejects_invalid_direction(monkeypatch):
    """Test lookup helper returns error for unsupported direction."""
    _reset_fake_service_calls()
    monkeypatch.setattr(dictionary_tools, "CuhkDictionaryService", _FakeService)

    response = dictionary_tools.lookup_cuhk_dictionary(
        query="巴士",
        direction="invalid",
    )

    assert response["result_count"] == 0
    assert "error" in response
    assert _FakeService.lookup_calls == []


def test_get_cuhk_dictionary_tooling_exposes_handler(monkeypatch):
    """Test tooling factory returns callable handler and tool definition."""
    _reset_fake_service_calls()
    monkeypatch.setattr(dictionary_tools, "CuhkDictionaryService", _FakeService)

    tools, handlers = dictionary_tools.get_cuhk_dictionary_tooling()

    assert len(tools) == 1
    assert tools[0]["name"] == dictionary_tools.CUHK_LOOKUP_TOOL_NAME
    handler = handlers[dictionary_tools.CUHK_LOOKUP_TOOL_NAME]
    response = handler(
        {
            "query": "baa1 si6",
            "direction": "cantonese_to_mandarin",
            "limit": "3",
        }
    )
    typed_response = cast("dict[str, object]", response)
    assert isinstance(typed_response, dict)

    assert _FakeService.lookup_calls == [("baa1 si6", "cantonese_to_mandarin", 3)]
    assert typed_response["direction"] == "cantonese_to_mandarin"
    assert typed_response["result_count"] == 1
