#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for list-shaped guided-translation LLM models."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock

from pydantic import ValidationError
from pytest import mark, raises

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider
from scinoephile.core.llms.utils import (
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.guided_translation import (
    GuidedTranslationManager,
    GuidedTranslationProcessor,
    GuidedTranslationPrompt,
    GuidedTranslationTestCase,
)

_LOCALIZED_PROMPT = GuidedTranslationPrompt(
    language=Language.zho_hant,
    subtitles="zimu",
    guides="cankao",
    outputs="shuchu",
    index="xuhao",
    text="wenben",
)
"""Guided-translation prompt with Chinese correspondence field names."""


def test_prompt_aliases_are_used_for_llm_correspondence():
    """Generated schemas and JSON should use prompt-specific aliases."""
    test_case_cls = GuidedTranslationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "zimu": [{"xuhao": 1, "wenben": "原文"}],
                "cankao": [{"xuhao": 1, "wenben": "參考"}],
            },
            "answer": {
                "shuchu": [{"xuhao": 1, "wenben": "譯文"}],
            },
        }
    )

    assert test_case.query.model_dump(by_alias=True) == {
        "zimu": [{"xuhao": 1, "wenben": "原文"}],
        "cankao": [{"xuhao": 1, "wenben": "參考"}],
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump(by_alias=True) == {
        "shuchu": [{"xuhao": 1, "wenben": "譯文"}],
    }
    assert set(test_case_cls.query_cls.model_json_schema()["properties"]) == {
        "zimu",
        "cankao",
    }
    assert set(test_case_cls.answer_cls.model_json_schema()["properties"]) == {"shuchu"}


def test_query_and_answer_require_consecutive_ordered_indexes():
    """Subtitle, guide, and output indexes should be consecutive and ordered."""
    query_cls = GuidedTranslationManager.get_query_cls(
        GuidedTranslationManager.base_prompt
    )
    answer_cls = GuidedTranslationManager.get_answer_cls(
        GuidedTranslationManager.base_prompt
    )

    with raises(ValidationError, match="subtitle indexes must be consecutive"):
        query_cls.model_validate(
            {
                "subtitles": [
                    {"index": 1, "text": "one"},
                    {"index": 3, "text": "three"},
                ],
                "guides": [],
            }
        )
    with raises(ValidationError, match="guide indexes must be consecutive"):
        query_cls.model_validate(
            {
                "subtitles": [{"index": 1, "text": "one"}],
                "guides": [{"index": 2, "text": "two"}],
            }
        )
    with raises(ValidationError, match="output indexes must be consecutive"):
        answer_cls.model_validate({"outputs": [{"index": 2, "text": "two"}]})

    long_text = "x" * 1001
    query_cls.model_validate(
        {
            "subtitles": [{"index": 1, "text": long_text}],
            "guides": [{"index": 1, "text": long_text}],
        }
    )
    answer_cls.model_validate({"outputs": [{"index": 1, "text": long_text}]})


@mark.parametrize(
    "test_case_cls",
    [
        GuidedTranslationTestCase,
        GuidedTranslationManager.get_test_case_cls(
            GuidedTranslationManager.base_prompt
        ),
    ],
    ids=["static", "generated"],
)
def test_outputs_must_correspond_to_query_subtitles(
    test_case_cls: type[GuidedTranslationTestCase],
):
    """Every query subtitle should have exactly one same-index output."""
    with raises(ValidationError, match="correspond exactly"):
        test_case_cls.model_validate(
            {
                "query": {
                    "subtitles": [
                        {"index": 1, "text": "one"},
                        {"index": 2, "text": "two"},
                    ],
                    "guides": [],
                },
                "answer": {"outputs": [{"index": 1, "text": "translated"}]},
            }
        )


def test_processor_maps_indexed_outputs_to_subtitle_timing():
    """Processor outputs should preserve source-subtitle ordering and timing."""
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = json.dumps(
        {
            "shuchu": [
                {"xuhao": 1, "wenben": "譯文一"},
                {"xuhao": 2, "wenben": "譯文二"},
            ]
        },
        ensure_ascii=False,
    )
    processor = GuidedTranslationProcessor(_LOCALIZED_PROMPT, provider=provider)
    processor.queryer.cache_dir_path = None
    source = Series(
        events=[
            Subtitle(start=0, end=1000, text="原文一"),
            Subtitle(start=1000, end=2000, text="原文二"),
        ]
    )
    guide = Series(events=[Subtitle(start=0, end=2000, text="參考")])

    output = processor.process(source, guide)

    assert output == Series(
        events=[
            Subtitle(start=0, end=1000, text="譯文一"),
            Subtitle(start=1000, end=2000, text="譯文二"),
        ]
    )
    messages, answer_cls, _ = provider.chat_completion.call_args.args
    assert answer_cls is processor.queryer.test_case_cls.answer_cls
    assert json.loads(messages[1]["content"]) == {
        "zimu": [
            {"xuhao": 1, "wenben": "原文一"},
            {"xuhao": 2, "wenben": "原文二"},
        ],
        "cankao": [{"xuhao": 1, "wenben": "參考"}],
    }


def test_processor_honors_start_index():
    """An inclusive start index should skip earlier guided-translation blocks."""
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = json.dumps(
        {"shuchu": [{"xuhao": 1, "wenben": "譯文二"}]},
        ensure_ascii=False,
    )
    processor = GuidedTranslationProcessor(_LOCALIZED_PROMPT, provider=provider)
    processor.queryer.cache_dir_path = None
    source = Series(
        events=[
            Subtitle(start=0, end=1000, text="原文一"),
            Subtitle(start=5000, end=6000, text="原文二"),
        ]
    )
    guide = Series(
        events=[
            Subtitle(start=0, end=1000, text="參考一"),
            Subtitle(start=5000, end=6000, text="參考二"),
        ]
    )

    output = processor.process(source, guide, start_at_idx=1)

    assert [subtitle.text for subtitle in output] == ["譯文二"]
    provider.chat_completion.assert_called_once()


def test_persistence_uses_base_prompt_field_names(tmp_path: Path):
    """Persistence should use canonical names and reload localized aliases."""
    test_case_cls = GuidedTranslationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "subtitles": [{"index": 1, "text": "原文"}],
                "guides": [],
            },
            "answer": {"outputs": [{"index": 1, "text": "譯文"}]},
        }
    )
    output_path = tmp_path / "guided_translation.json"

    save_test_cases_to_json(
        output_path,
        [test_case],
        GuidedTranslationManager,
    )

    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        {
            "query": {
                "subtitles": [{"index": 1, "text": "原文"}],
                "guides": [],
            },
            "answer": {"outputs": [{"index": 1, "text": "譯文"}]},
        }
    ]
    loaded = load_test_cases_from_json(
        output_path,
        GuidedTranslationManager,
        _LOCALIZED_PROMPT,
    )
    assert loaded[0].query.model_dump(by_alias=True) == {
        "zimu": [{"xuhao": 1, "wenben": "原文"}],
        "cankao": [],
    }
