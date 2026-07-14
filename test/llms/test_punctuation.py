#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for static punctuation LLM models."""

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
from scinoephile.llms.punctuation import (
    PunctuationManager,
    PunctuationPrompt,
    PunctuationTestCase,
)
from scinoephile.multilang.yue_zho.transcription import (
    YuePunctuationVsZhoPromptYueHans,
)
from scinoephile.optimization.persistence.test_cases import PersistedTestCase
from test.helpers import test_data_root

_LOCALIZED_PROMPT = PunctuationPrompt(
    language=Language.zho_hant,
    src_1="zimu",
    src_1_desc="要加標點嘅字幕行",
    src_2="cankao",
    src_2_desc="標點參考字幕",
    output="jieguo",
    output_desc="加標點後嘅字幕",
)
"""Punctuation prompt with Chinese correspondence field names."""

_PUNCTUATION_PATHS = tuple(
    sorted(
        test_data_root.glob(
            "*/output/*/multilang/yue_zho/transcription/punctuation/*.json"
        )
    )
)
"""Tracked punctuation test-case JSON paths."""


def test_prompt_aliases_are_used_for_llm_correspondence():
    """Generated schemas and JSON should use prompt-specific aliases."""
    test_case_cls = PunctuationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {"zimu": ["原文一", "原文二"], "cankao": "參考"},
            "answer": {"jieguo": "原文一原文二"},
        }
    )

    assert test_case.query.model_dump() == {
        "subtitles": ["原文一", "原文二"],
        "guide": "參考",
    }
    assert test_case.query.model_dump(by_alias=True) == {
        "zimu": ["原文一", "原文二"],
        "cankao": "參考",
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump() == {"output": "原文一原文二"}
    assert test_case.answer.model_dump(by_alias=True) == {"jieguo": "原文一原文二"}

    query_schema = test_case_cls.query_cls.model_json_schema(by_alias=True)
    answer_schema = test_case_cls.answer_cls.model_json_schema(by_alias=True)
    assert query_schema["title"] == f"PunctuationQuery_{_LOCALIZED_PROMPT.name}"
    assert list(query_schema["properties"]) == ["zimu", "cankao"]
    assert query_schema["properties"]["zimu"]["description"] == "要加標點嘅字幕行"
    assert query_schema["properties"]["cankao"]["description"] == "標點參考字幕"
    assert answer_schema["title"] == f"PunctuationAnswer_{_LOCALIZED_PROMPT.name}"
    assert list(answer_schema["properties"]) == ["jieguo"]
    assert answer_schema["properties"]["jieguo"]["description"] == "加標點後嘅字幕"


def test_queryer_corresponds_using_prompt_aliases():
    """Queryer should send aliased queries and request aliased answers."""
    test_case_cls = PunctuationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {"query": {"subtitles": ["原文"], "guide": "參考"}}
    )
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = '{"jieguo": "原文"}'
    queryer = Queryer(test_case_cls, provider=provider, max_attempts=1)

    result = queryer(test_case)

    assert result.answer is not None
    assert result.answer.model_dump() == {"output": "原文"}
    messages, answer_cls, _ = provider.chat_completion.call_args.args
    assert answer_cls is test_case_cls.answer_cls
    assert json.loads(messages[1]["content"]) == {
        "zimu": ["原文"],
        "cankao": "參考",
    }


def test_query_and_answer_require_nonempty_fields():
    """Punctuation queries and answers should reject empty required fields."""
    query_cls = PunctuationManager.get_query_cls(_LOCALIZED_PROMPT)
    answer_cls = PunctuationManager.get_answer_cls(_LOCALIZED_PROMPT)

    with raises(ValidationError, match=_LOCALIZED_PROMPT.src_1_missing_err):
        query_cls.model_validate({"subtitles": [], "guide": "參考"})
    with raises(ValidationError, match=_LOCALIZED_PROMPT.src_2_missing_err):
        query_cls.model_validate({"subtitles": ["原文"], "guide": ""})
    with raises(ValidationError, match=_LOCALIZED_PROMPT.output_missing_err):
        answer_cls.model_validate({"output": ""})


def test_validation_and_minimum_difficulty_are_static():
    """Punctuation semantics should live on the static test-case model."""
    test_case_cls = PunctuationManager.get_test_case_cls(
        YuePunctuationVsZhoPromptYueHans
    )
    plain = test_case_cls.model_validate(
        {
            "query": {"subtitles": ["你好"], "guide": "你好"},
            "answer": {"output": "你好"},
        }
    )
    matching_punctuation = test_case_cls.model_validate(
        {
            "query": {"subtitles": ["你好"], "guide": "你，好"},
            "answer": {"output": "你，好"},
        }
    )
    different_punctuation = test_case_cls.model_validate(
        {
            "query": {"subtitles": ["你好"], "guide": "你好"},
            "answer": {"output": "你，好"},
        }
    )
    direct = PunctuationTestCase.model_validate(
        {
            "query": {"subtitles": ["你好"], "guide": "你好"},
            "answer": {"output": "你，好"},
        }
    )

    assert plain.difficulty == 0
    assert matching_punctuation.difficulty == 1
    assert different_punctuation.difficulty == 2
    assert direct.difficulty == 2
    with raises(ValidationError, match="does not match"):
        test_case_cls.model_validate(
            {
                "query": {"subtitles": ["你好"], "guide": "你好"},
                "answer": {"output": "你壞"},
            }
        )


def test_persistence_uses_base_prompt_aliases(tmp_path: Path):
    """JSON and normalized persistence should use base prompt field aliases."""
    test_case_cls = PunctuationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {"zimu": ["原文"], "cankao": "參考"},
            "answer": {"jieguo": "原文"},
            "verified": True,
        }
    )
    output_path = tmp_path / "punctuation.json"

    save_test_cases_to_json(output_path, [test_case], PunctuationManager)

    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        {
            "query": {"one": ["原文"], "two": "參考"},
            "answer": {"output": "原文"},
            "verified": True,
        }
    ]
    persisted = PersistedTestCase.from_test_case(test_case, PunctuationManager)
    assert persisted.query == {"one": ["原文"], "two": "參考"}
    assert persisted.answer == {"output": "原文"}

    loaded = load_test_cases_from_json(
        output_path,
        PunctuationManager,
        _LOCALIZED_PROMPT,
    )
    assert loaded[0].query.model_dump(by_alias=True) == {
        "zimu": ["原文"],
        "cankao": "參考",
    }
    assert loaded[0].answer is not None
    assert loaded[0].answer.model_dump(by_alias=True) == {"jieguo": "原文"}


def test_tracked_fixture_count():
    """All four tracked punctuation files should contain 2,973 test cases."""
    counts = [
        len(json.loads(input_path.read_text(encoding="utf-8")))
        for input_path in _PUNCTUATION_PATHS
    ]

    assert len(_PUNCTUATION_PATHS) == 4
    assert sum(counts) == 2973


@mark.parametrize(
    "input_path",
    _PUNCTUATION_PATHS,
    ids=[
        input_path.relative_to(test_data_root).as_posix()
        for input_path in _PUNCTUATION_PATHS
    ],
)
def test_tracked_fixture_round_trips_without_migration(
    input_path: Path,
    tmp_path: Path,
):
    """Tracked punctuation JSON should round-trip without schema changes."""
    raw_data = json.loads(input_path.read_text(encoding="utf-8"))
    test_cases = load_test_cases_from_json(
        input_path,
        PunctuationManager,
        YuePunctuationVsZhoPromptYueHans,
    )
    output_path = tmp_path / input_path.name

    save_test_cases_to_json(
        output_path,
        test_cases,
        PunctuationManager,
    )

    assert json.loads(output_path.read_text(encoding="utf-8")) == raw_data
