#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of prompt-derived dictionary tool specifications."""

from __future__ import annotations

from collections.abc import Generator
from os import environ
from pathlib import Path
from typing import Any, ClassVar, cast
from unittest.mock import patch

import pytest

from scinoephile.common.file import get_temp_directory_path
from scinoephile.core.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
    DictionaryToolPrompt,
)
from scinoephile.core.dictionaries.serialization import (
    dictionary_definition_to_dict,
    dictionary_entry_to_dict,
)
from scinoephile.core.dictionaries.sqlite_store import DictionarySqliteStore
from scinoephile.dictionaries.dictionary_tools import (
    get_dictionary_tools,
    lookup_dictionary,
)
from scinoephile.multilang.yue_zho.block_review import (
    YueVsZhoYueHansBlockReviewPrompt,
    get_yue_vs_zho_block_reviewer,
)
from scinoephile.multilang.yue_zho.line_review import (
    YueVsZhoYueHansLineReviewPrompt,
    get_yue_vs_zho_line_reviewer,
)
from scinoephile.multilang.yue_zho.translation import (
    YueVsZhoYueHansTranslationPrompt,
    get_yue_vs_zho_translator,
)


class StubDictionaryToolPrompt(DictionaryToolPrompt):
    """Prompt stub providing custom dictionary tool specification text."""

    dictionary_tool_name: ClassVar[str] = "lookup_stub_dictionary"
    """Name of the dictionary lookup tool."""

    dictionary_tool_description: ClassVar[str] = "Custom dictionary lookup tool."
    """Description of the dictionary lookup tool."""

    dictionary_tool_query_description: ClassVar[str] = "Custom query description."
    """Description of the dictionary lookup query parameter."""


@pytest.fixture
def dictionary_cache_dir_path() -> Generator[Path]:
    """Provide deterministic CUHK and GZZJ cache databases."""
    with get_temp_directory_path() as temp_dir_path:
        cache_dir_path = temp_dir_path / "scinoephile" / "dictionaries"
        cuhk_database_path = cache_dir_path / "cuhk" / "cuhk.db"
        gzzj_database_path = cache_dir_path / "gzzj" / "gzzj.db"

        DictionarySqliteStore(database_path=cuhk_database_path).persist(
            (
                DictionarySource(
                    name="Test CUHK",
                    shortname="cuhk",
                    version="2026.04",
                    description="CUHK source used for dictionary tool tests.",
                    legal="BSD",
                    link="https://example.com/cuhk",
                    update_url="https://example.com/cuhk/update",
                    other="fixture",
                ),
                [
                    DictionaryEntry(
                        traditional="共享",
                        simplified="共享",
                        pinyin="gong4 xiang3",
                        jyutping="gung6 hoeng2",
                        frequency=3.0,
                        definitions=[DictionaryDefinition(text="cuhk definition")],
                    ),
                    DictionaryEntry(
                        traditional="山坑",
                        simplified="山坑",
                        pinyin="shan1 keng1",
                        jyutping="saan1 haang1",
                        frequency=2.0,
                        definitions=[DictionaryDefinition(text="gully")],
                    ),
                ],
            )
        )
        DictionarySqliteStore(database_path=gzzj_database_path).persist(
            (
                DictionarySource(
                    name="Test GZZJ",
                    shortname="gzzj",
                    version="2026.04",
                    description="GZZJ source used for dictionary tool tests.",
                    legal="BSD",
                    link="https://example.com/gzzj",
                    update_url="https://example.com/gzzj/update",
                    other="fixture",
                ),
                [
                    DictionaryEntry(
                        traditional="共享",
                        simplified="共享",
                        pinyin="gong4 xiang3",
                        jyutping="gung6 hoeng2",
                        frequency=1.0,
                        definitions=[DictionaryDefinition(text="gzzj definition")],
                    ),
                    DictionaryEntry(
                        traditional="仇",
                        simplified="仇",
                        pinyin="qiu2",
                        jyutping="kau4",
                        frequency=1.0,
                        definitions=[DictionaryDefinition(text="surname")],
                    ),
                ],
            )
        )
        yield temp_dir_path


def test_dictionary_definition_to_dict():
    """Serialize one dictionary definition payload."""
    assert dictionary_definition_to_dict(
        DictionaryDefinition(label="noun", text="stream water")
    ) == {
        "label": "noun",
        "text": "stream water",
    }


def test_dictionary_entry_to_dict():
    """Serialize one dictionary entry payload."""
    assert dictionary_entry_to_dict(
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
        )
    ) == {
        "traditional": "山坑",
        "simplified": "山坑",
        "pinyin": "shan1 keng1",
        "jyutping": "saan1 haang1",
        "frequency": 2.0,
        "definitions": [
            {
                "label": "",
                "text": "gully",
            },
            {
                "label": "noun",
                "text": "mountain stream",
            },
        ],
    }


def test_get_dictionary_tools_uses_prompt_text():
    """Build the tool spec from the prompt-provided text."""
    tool_box = get_dictionary_tools(StubDictionaryToolPrompt)

    assert [tool["name"] for tool in tool_box.specs] == [
        StubDictionaryToolPrompt.dictionary_tool_name
    ]
    assert tool_box.handler_names == [StubDictionaryToolPrompt.dictionary_tool_name]

    parameters = tool_box.specs[0]["parameters"]
    properties = cast(dict[str, object], parameters["properties"])
    query_schema = cast(dict[str, object], properties["query"])

    assert (
        tool_box.specs[0]["description"]
        == StubDictionaryToolPrompt.dictionary_tool_description
    )
    assert query_schema["description"] == (
        StubDictionaryToolPrompt.dictionary_tool_query_description
    )


def test_lookup_dictionary_defaults_to_all_dictionaries(
    dictionary_cache_dir_path: Path,
):
    """Search all available local dictionaries by default."""
    with patch.dict(environ, {"SCINOEPHILE_CACHE_DIR": str(dictionary_cache_dir_path)}):
        response = lookup_dictionary(query="共享")

    entry = cast(dict[str, Any], response["entries"][0])
    definitions = cast(list[dict[str, str]], entry["definitions"])
    assert response["result_count"] == 1
    assert entry["traditional"] == "共享"
    assert [definition["text"] for definition in definitions] == [
        "cuhk definition",
        "gzzj definition",
    ]


def test_lookup_dictionary_returns_compact_error_for_no_available_dictionaries(
    dictionary_cache_dir_path: Path,
):
    """Return an error when no local dictionaries are available."""
    for database_path in (
        dictionary_cache_dir_path / "scinoephile" / "dictionaries" / "cuhk" / "cuhk.db",
        dictionary_cache_dir_path / "scinoephile" / "dictionaries" / "gzzj" / "gzzj.db",
    ):
        database_path.unlink()

    with patch.dict(environ, {"SCINOEPHILE_CACHE_DIR": str(dictionary_cache_dir_path)}):
        response = lookup_dictionary(query="仇")

    assert response["result_count"] == 0
    assert response["entries"] == []
    assert "No searchable dictionary databases were found." in response["error"]
    assert "cuhk" in response["error"]
    assert "gzzj" in response["error"]


@pytest.mark.parametrize(
    ("prompt_cls", "factory"),
    [
        (YueVsZhoYueHansTranslationPrompt, get_yue_vs_zho_translator),
        (YueVsZhoYueHansBlockReviewPrompt, get_yue_vs_zho_block_reviewer),
        (YueVsZhoYueHansLineReviewPrompt, get_yue_vs_zho_line_reviewer),
    ],
)
def test_processors_use_prompt_dictionary_tooling(
    prompt_cls: type[DictionaryToolPrompt],
    factory,
):
    """Wire dictionary tooling from the selected prompt class."""
    processor = factory(prompt_cls=prompt_cls, test_cases=[])

    assert [tool["name"] for tool in processor.queryer.tool_box.specs] == [
        prompt_cls.dictionary_tool_name
    ]
    assert processor.queryer.tool_box.handler_names == [prompt_cls.dictionary_tool_name]
