#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the CUHK MCP tool server module."""

from __future__ import annotations

from pathlib import Path

from scinoephile.lang.yue.dictionaries import DictionaryDefinition, DictionaryEntry
from scinoephile.mcp import cuhk_dictionary_server


class _FakeService:
    """Test double for CuhkDictionaryService."""

    init_calls: list[bool] = []
    build_calls: list[bool] = []
    lookup_calls: list[tuple[str, str, int, bool]] = []

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

    def build(self, force_rebuild: bool = False) -> Path:
        """Track build calls.

        Arguments:
            force_rebuild: whether force rebuild was requested
        Returns:
            fake database path
        """
        type(self).build_calls.append(force_rebuild)
        return self.database_path

    def lookup(self, query: str, direction, limit: int = 10) -> list[DictionaryEntry]:
        """Track lookup calls and return deterministic payload.

        Arguments:
            query: lookup query
            direction: lookup direction enum
            limit: max number of entries
        Returns:
            list containing one deterministic entry
        """
        type(self).lookup_calls.append(
            (query, direction.value, limit, self.auto_build_missing)
        )
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
    """Reset fake service call logs."""
    _FakeService.init_calls.clear()
    _FakeService.build_calls.clear()
    _FakeService.lookup_calls.clear()


def test_lookup_tool_defaults_auto_build_missing_false(monkeypatch):
    """Test lookup tool defaults to not auto-building missing data."""
    _reset_fake_service_calls()
    monkeypatch.setattr(cuhk_dictionary_server, "CuhkDictionaryService", _FakeService)

    response = cuhk_dictionary_server.lookup_cuhk_dictionary(query="巴士")

    assert response["query"] == "巴士"
    assert response["direction"] == "mandarin_to_cantonese"
    assert response["result_count"] == 1
    assert _FakeService.lookup_calls[0] == ("巴士", "mandarin_to_cantonese", 10, False)


def test_lookup_tool_passes_auto_build_and_direction(monkeypatch):
    """Test lookup tool forwards explicit auto-build and direction options."""
    _reset_fake_service_calls()
    monkeypatch.setattr(cuhk_dictionary_server, "CuhkDictionaryService", _FakeService)

    response = cuhk_dictionary_server.lookup_cuhk_dictionary(
        query="baa1 si6",
        direction="cantonese_to_mandarin",
        limit=3,
        auto_build_missing=True,
    )

    assert response["direction"] == "cantonese_to_mandarin"
    assert _FakeService.lookup_calls[0] == (
        "baa1 si6",
        "cantonese_to_mandarin",
        3,
        True,
    )


def test_build_tool_calls_service_build(monkeypatch):
    """Test build tool calls underlying service build method."""
    _reset_fake_service_calls()
    monkeypatch.setattr(cuhk_dictionary_server, "CuhkDictionaryService", _FakeService)

    response = cuhk_dictionary_server.build_cuhk_dictionary_data(force_rebuild=True)

    assert response["rebuilt"] is True
    assert response["database_path"] == "/tmp/fake_cuhk.db"
    assert _FakeService.build_calls == [True]
