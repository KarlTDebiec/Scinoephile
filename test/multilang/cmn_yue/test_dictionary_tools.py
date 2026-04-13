#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.multilang.cmn_yue.dictionary_tools."""

from __future__ import annotations

from typing import cast

import pytest

from scinoephile.multilang.cmn_yue import dictionary_tools
from scinoephile.multilang.dictionaries import DictionaryDefinition, DictionaryEntry


@pytest.fixture
def sample_entries() -> list[DictionaryEntry]:
    """Provide deterministic dictionary entries for tool tests."""
    return [
        DictionaryEntry(
            traditional="山坑",
            simplified="山坑",
            pinyin="shan1 keng1",
            jyutping="saan1 haang1",
            frequency=2.0,
            definitions=[
                DictionaryDefinition(text="gully"),
                DictionaryDefinition(text="mountain stream", label="noun"),
            ],
        ),
        DictionaryEntry(
            traditional="山坑水",
            simplified="山坑水",
            pinyin="shan1 keng1 shui3",
            jyutping="saan1 haang1 seoi2",
            frequency=1.0,
            definitions=[DictionaryDefinition(text="stream water")],
        ),
    ]


def test_lookup_cuhk_dictionary_requires_nonempty_query():
    """Reject empty dictionary tool queries."""
    assert dictionary_tools.lookup_cuhk_dictionary("   ") == {
        "query": "",
        "result_count": 0,
        "entries": [],
        "error": "query must be non-empty",
    }


@pytest.mark.parametrize(
    "query",
    [
        "山坑",
        "shān kēng",
        "saan1 haang1",
    ],
)
def test_lookup_cuhk_dictionary_uses_inferred_lookup(
    monkeypatch: pytest.MonkeyPatch,
    sample_entries: list[DictionaryEntry],
    query: str,
):
    """Lookup tool delegates to inferred-format dictionary search."""

    class FakeService:
        """Stub CUHK service for tool tests."""

        def __init__(self, *, auto_build_missing: bool = False):
            self.auto_build_missing = auto_build_missing

        def lookup_inferred(self, query: str, limit: int = 10) -> list[DictionaryEntry]:
            assert query
            assert limit == 10
            return sample_entries

    monkeypatch.setattr(dictionary_tools, "CuhkDictionaryService", FakeService)

    result = dictionary_tools.lookup_cuhk_dictionary(query)

    assert result == {
        "query": query,
        "result_count": 2,
        "entries": [
            {
                "traditional": "山坑",
                "simplified": "山坑",
                "pinyin": "shan1 keng1",
                "jyutping": "saan1 haang1",
                "frequency": 2.0,
                "definitions": [
                    {"label": "", "text": "gully"},
                    {"label": "noun", "text": "mountain stream"},
                ],
            },
            {
                "traditional": "山坑水",
                "simplified": "山坑水",
                "pinyin": "shan1 keng1 shui3",
                "jyutping": "saan1 haang1 seoi2",
                "frequency": 1.0,
                "definitions": [
                    {"label": "", "text": "stream water"},
                ],
            },
        ],
    }


@pytest.mark.parametrize(
    ("exception", "expected_error"),
    [
        (
            FileNotFoundError("CUHK dictionary database not found."),
            "CUHK dictionary database not found.",
        ),
        (
            ValueError("Could not infer a supported lookup format for query 'gully'"),
            "Could not infer a supported lookup format for query 'gully'",
        ),
    ],
)
def test_lookup_cuhk_dictionary_returns_structured_errors(
    monkeypatch: pytest.MonkeyPatch,
    exception: Exception,
    expected_error: str,
):
    """Convert service failures into structured tool responses."""

    class FakeService:
        """Stub CUHK service for tool tests."""

        def __init__(self, *, auto_build_missing: bool = False):
            self.auto_build_missing = auto_build_missing

        def lookup_inferred(self, query: str, limit: int = 10) -> list[DictionaryEntry]:
            raise exception

    monkeypatch.setattr(dictionary_tools, "CuhkDictionaryService", FakeService)

    assert dictionary_tools.lookup_cuhk_dictionary("gully") == {
        "query": "gully",
        "result_count": 0,
        "entries": [],
        "error": expected_error,
    }


def test_lookup_cuhk_dictionary_from_args_rejects_unexpected_arguments():
    """Reject tool arguments outside the simplified schema."""
    assert dictionary_tools._lookup_cuhk_dictionary_from_args(
        {"query": "山坑", "limit": 2, "direction": "cmn_to_yue"}
    ) == {
        "query": "山坑",
        "result_count": 0,
        "entries": [],
        "error": "unexpected arguments: direction, limit",
    }


def test_get_cuhk_dictionary_tooling_schema_drops_direction():
    """Publish a schema that only accepts inferred-lookups inputs."""
    tools, handlers = dictionary_tools.get_cuhk_dictionary_tooling()

    assert [tool["name"] for tool in tools] == [dictionary_tools.CUHK_LOOKUP_TOOL_NAME]
    assert sorted(handlers) == [dictionary_tools.CUHK_LOOKUP_TOOL_NAME]

    parameters = tools[0]["parameters"]
    properties = cast(dict[str, object], parameters["properties"])
    assert parameters["additionalProperties"] is False
    assert parameters["required"] == ["query"]
    assert set(properties) == {"query"}


def test_get_cuhk_dictionary_tooling_description_mentions_inference():
    """Describe the inferred query formats in the exported tool metadata."""
    tools, _ = dictionary_tools.get_cuhk_dictionary_tooling()
    parameters = tools[0]["parameters"]
    properties = cast(dict[str, object], parameters["properties"])
    query_schema = cast(dict[str, object], properties["query"])
    query_description = str(query_schema["description"])

    assert "automatically infers" in tools[0]["description"]
    assert "pinyin" in query_description
    assert "jyutping" in query_description
