#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for list-shaped translation LLM models."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock

from pydantic import ValidationError
from pytest import mark, raises

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, Queryer
from scinoephile.core.llms.utils import (
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.translation import (
    TranslationManager,
    TranslationProcessor,
    TranslationPrompt,
    TranslationTestCase,
)

_LOCALIZED_PROMPT = TranslationPrompt(
    language=Language.zho_hant,
    subtitles="zimu",
    outputs="fanyi",
    index="xuhao",
    text="wenben",
)
"""Translation prompt with Chinese correspondence field names."""


def test_prompt_aliases_are_used_for_llm_correspondence():
    """Generated schemas and JSON should use prompt-specific aliases."""
    test_case_cls = TranslationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "zimu": [
                    {"xuhao": 1, "wenben": "原文一"},
                    {"xuhao": 2, "wenben": "原文二"},
                ]
            },
            "answer": {
                "fanyi": [
                    {"xuhao": 1, "wenben": "譯文一"},
                    {"xuhao": 2, "wenben": "譯文二"},
                ]
            },
        }
    )

    assert test_case.query.model_dump(by_alias=True) == {
        "zimu": [
            {"xuhao": 1, "wenben": "原文一"},
            {"xuhao": 2, "wenben": "原文二"},
        ]
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump(by_alias=True) == {
        "fanyi": [
            {"xuhao": 1, "wenben": "譯文一"},
            {"xuhao": 2, "wenben": "譯文二"},
        ]
    }
    assert set(test_case_cls.query_cls.model_json_schema()["properties"]) == {"zimu"}
    assert set(test_case_cls.answer_cls.model_json_schema()["properties"]) == {"fanyi"}


def test_queryer_corresponds_using_prompt_aliases():
    """Queryer should send aliased queries and request aliased answers."""
    test_case_cls = TranslationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {"query": {"subtitles": [{"index": 1, "text": "原文"}]}}
    )
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = (
        '{"fanyi": [{"xuhao": 1, "wenben": "譯文"}]}'
    )
    queryer = Queryer(test_case_cls, provider=provider, max_attempts=1)

    result = queryer(test_case)

    assert result.answer is not None
    messages = provider.chat_completion.call_args.args[0]
    assert json.loads(messages[1]["content"]) == {
        "zimu": [{"xuhao": 1, "wenben": "原文"}]
    }
    assert '"fanyi"' in messages[0]["content"]
    assert '"xuhao"' in messages[0]["content"]
    assert '"wenben"' in messages[0]["content"]


def test_query_and_answer_require_nonempty_consecutive_indexes():
    """Translation lists should be nonempty, consecutive, ordered, and one-based."""
    query_cls = TranslationManager.get_query_cls(TranslationManager.base_prompt)
    answer_cls = TranslationManager.get_answer_cls(TranslationManager.base_prompt)

    with raises(ValidationError, match="at least 1 item"):
        query_cls.model_validate({"subtitles": []})
    with raises(ValidationError, match="consecutive, ordered, and begin at 1"):
        query_cls.model_validate(
            {
                "subtitles": [
                    {"index": 1, "text": "one"},
                    {"index": 3, "text": "three"},
                ]
            }
        )
    with raises(ValidationError, match="at least 1 item"):
        answer_cls.model_validate({"outputs": []})
    with raises(ValidationError, match="consecutive, ordered, and begin at 1"):
        answer_cls.model_validate(
            {
                "outputs": [
                    {"index": 2, "text": "two"},
                    {"index": 1, "text": "one"},
                ]
            }
        )


@mark.parametrize(
    "test_case_cls",
    [
        TranslationTestCase,
        TranslationManager.get_test_case_cls(TranslationManager.base_prompt),
    ],
    ids=["static", "generated"],
)
def test_answer_indexes_must_correspond_to_query_indexes(
    test_case_cls: type[TranslationTestCase],
):
    """Every query subtitle should have exactly one corresponding output."""
    with raises(ValidationError, match="correspond exactly"):
        test_case_cls.model_validate(
            {
                "query": {
                    "subtitles": [
                        {"index": 1, "text": "one"},
                        {"index": 2, "text": "two"},
                    ]
                },
                "answer": {"outputs": [{"index": 1, "text": "translated"}]},
            }
        )


def test_translation_preserves_text_length_bounds():
    """Input text should remain bounded while output text remains unbounded."""
    query_cls = TranslationManager.get_query_cls(TranslationManager.base_prompt)
    answer_cls = TranslationManager.get_answer_cls(TranslationManager.base_prompt)
    long_text = "x" * 1001

    with raises(ValidationError, match="at most 1000 characters"):
        query_cls.model_validate({"subtitles": [{"index": 1, "text": long_text}]})
    answer = answer_cls.model_validate({"outputs": [{"index": 1, "text": long_text}]})

    assert answer.model_dump()["outputs"][0]["text"] == long_text


def test_json_uses_base_prompt_fields(tmp_path: Path):
    """JSON should persist base fields and load them into a concrete prompt."""
    test_case_cls = TranslationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {"zimu": [{"xuhao": 1, "wenben": "原文"}]},
            "answer": {"fanyi": [{"xuhao": 1, "wenben": "譯文"}]},
            "verified": True,
        }
    )
    output_path = tmp_path / "test_cases.json"

    save_test_cases_to_json(output_path, [test_case], TranslationManager)

    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        {
            "query": {"subtitles": [{"index": 1, "text": "原文"}]},
            "answer": {"outputs": [{"index": 1, "text": "譯文"}]},
            "verified": True,
        }
    ]
    loaded = load_test_cases_from_json(
        output_path,
        TranslationManager,
        _LOCALIZED_PROMPT,
    )
    assert loaded[0].query.model_dump(by_alias=True) == {
        "zimu": [{"xuhao": 1, "wenben": "原文"}]
    }
    assert loaded[0].answer is not None
    assert loaded[0].answer.model_dump(by_alias=True) == {
        "fanyi": [{"xuhao": 1, "wenben": "譯文"}]
    }


def test_processor_uses_indexed_subtitles_and_outputs():
    """Translation processor should build and consume the indexed list shape."""
    test_case_cls = TranslationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "subtitles": [
                    {"index": 1, "text": "original one"},
                    {"index": 2, "text": "original two"},
                ]
            },
            "answer": {
                "outputs": [
                    {"index": 1, "text": "translated one"},
                    {"index": 2, "text": "translated two"},
                ]
            },
            "verified": True,
        }
    )
    block = Series(
        [
            Subtitle(start=0, end=1000, text="original one"),
            Subtitle(start=1000, end=2000, text="original two"),
        ]
    )
    series = Series(list(block.events))
    series.blocks = [block]
    provider = Mock(spec=LLMProvider)
    processor = TranslationProcessor(
        _LOCALIZED_PROMPT,
        [test_case],
        provider=provider,
    )

    output = processor.process(series)

    assert [subtitle.text for subtitle in output] == [
        "translated one",
        "translated two",
    ]
    provider.chat_completion.assert_not_called()
