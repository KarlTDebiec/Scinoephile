#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of prompt-derived dictionary tool specifications."""

from __future__ import annotations

from typing import ClassVar, cast

from scinoephile.multilang.dictionaries import DictionaryDefinition, DictionaryEntry
from scinoephile.multilang.dictionaries.dictionary_tool_prompt import (
    DictionaryToolPrompt,
)
from scinoephile.multilang.dictionaries.dictionary_tools import get_dictionary_tools
from scinoephile.multilang.dictionaries.serialization import (
    dictionary_definition_to_dict,
    dictionary_entry_to_dict,
)
from scinoephile.multilang.yue_zho.proofreading import (
    YueZhoHansProofreadingPrompt,
    get_yue_vs_zho_proofreader,
)
from scinoephile.multilang.yue_zho.review import (
    YueHansReviewPrompt,
    get_yue_vs_zho_reviewer,
)
from scinoephile.multilang.yue_zho.translation import (
    YueHansFromZhoTranslationPrompt,
    get_yue_from_zho_translator,
)


class StubDictionaryToolPrompt(DictionaryToolPrompt):
    """Prompt stub providing custom dictionary tool specification text."""

    dictionary_tool_name: ClassVar[str] = "lookup_stub_dictionary"
    """Name of the dictionary lookup tool."""

    dictionary_tool_description: ClassVar[str] = "Custom dictionary lookup tool."
    """Description of the dictionary lookup tool."""

    dictionary_tool_query_description: ClassVar[str] = "Custom query description."
    """Description of the dictionary lookup query parameter."""


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
    tools, handlers = get_dictionary_tools(StubDictionaryToolPrompt)

    assert [tool["name"] for tool in tools] == [
        StubDictionaryToolPrompt.dictionary_tool_name
    ]
    assert sorted(handlers) == [StubDictionaryToolPrompt.dictionary_tool_name]

    parameters = tools[0]["parameters"]
    properties = cast(dict[str, object], parameters["properties"])
    query_schema = cast(dict[str, object], properties["query"])

    assert (
        tools[0]["description"] == StubDictionaryToolPrompt.dictionary_tool_description
    )
    assert query_schema["description"] == (
        StubDictionaryToolPrompt.dictionary_tool_query_description
    )


def test_translation_processor_uses_prompt_dictionary_tooling():
    """Wire translation tooling from the selected prompt class."""
    processor = get_yue_from_zho_translator(
        prompt_cls=YueHansFromZhoTranslationPrompt, test_cases=[]
    )

    assert [tool["name"] for tool in processor.queryer.tools] == [
        YueHansFromZhoTranslationPrompt.dictionary_tool_name
    ]
    assert sorted(processor.queryer.tool_handlers) == [
        YueHansFromZhoTranslationPrompt.dictionary_tool_name
    ]


def test_review_processor_uses_prompt_dictionary_tooling():
    """Wire review tooling from the selected prompt class."""
    processor = get_yue_vs_zho_reviewer(prompt_cls=YueHansReviewPrompt, test_cases=[])

    assert [tool["name"] for tool in processor.queryer.tools] == [
        YueHansReviewPrompt.dictionary_tool_name
    ]
    assert sorted(processor.queryer.tool_handlers) == [
        YueHansReviewPrompt.dictionary_tool_name
    ]


def test_proofreading_processor_uses_prompt_dictionary_tooling():
    """Wire proofreading tooling from the selected prompt class."""
    processor = get_yue_vs_zho_proofreader(
        prompt_cls=YueZhoHansProofreadingPrompt, test_cases=[]
    )

    assert [tool["name"] for tool in processor.queryer.tools] == [
        YueZhoHansProofreadingPrompt.dictionary_tool_name
    ]
    assert sorted(processor.queryer.tool_handlers) == [
        YueZhoHansProofreadingPrompt.dictionary_tool_name
    ]
