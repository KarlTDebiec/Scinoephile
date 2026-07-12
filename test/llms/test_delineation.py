#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for static delineation LLM models."""

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
from scinoephile.llms.delineation import (
    DelineationManager,
    DelineationPrompt,
    DelineationTestCase,
)
from scinoephile.multilang.yue_zho.transcription.delineation import (
    YueDelineationVsZhoPromptYueHans,
)
from scinoephile.optimization.persistence.test_cases import PersistedTestCase
from test.helpers import test_data_root

_LOCALIZED_PROMPT = DelineationPrompt(
    language=Language.zho_hant,
    src_1_sub_1="cankao_yi",
    src_1_sub_1_desc="第一條參考字幕",
    src_1_sub_2="cankao_er",
    src_1_sub_2_desc="第二條參考字幕",
    src_2_sub_1="mubiao_yi",
    src_2_sub_1_desc="第一條初始目標字幕",
    src_2_sub_2="mubiao_er",
    src_2_sub_2_desc="第二條初始目標字幕",
    src_2_sub_1_sub_2_missing_err="查詢至少要有一條目標字幕。",
    src_2_sub_1_shifted="shuchu_yi",
    src_2_sub_1_shifted_desc="第一條調整後目標字幕",
    src_2_sub_2_shifted="shuchu_er",
    src_2_sub_2_shifted_desc="第二條調整後目標字幕",
    src_2_sub_1_sub_2_unchanged_err="調整後目標字幕不可原樣重複。",
    src_2_chars_changed_err_tpl=(
        "調整後目標字幕字元不一致：\n期望：{expected}\n收到：{received}"
    ),
)
"""Delineation prompt with localized correspondence field names."""

_DELINEATION_PATHS = tuple(
    sorted(
        test_data_root.glob(
            "*/output/*/multilang/yue_zho/transcription/delineation/*.json"
        )
    )
)
"""Tracked delineation test-case JSON paths."""


def test_prompt_aliases_are_used_for_llm_correspondence():
    """Generated schemas and JSON should use prompt-specific aliases."""
    test_case_cls = DelineationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "cankao_yi": "參考一",
                "cankao_er": "參考二",
                "mubiao_yi": "甲",
                "mubiao_er": "乙",
            },
            "answer": {"shuchu_yi": "甲乙"},
        }
    )

    assert test_case.query.model_dump() == {
        "reference_one": "參考一",
        "reference_two": "參考二",
        "target_one": "甲",
        "target_two": "乙",
    }
    assert test_case.query.model_dump(by_alias=True) == {
        "cankao_yi": "參考一",
        "cankao_er": "參考二",
        "mubiao_yi": "甲",
        "mubiao_er": "乙",
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump() == {
        "output_one": "甲乙",
        "output_two": "",
    }
    assert test_case.answer.model_dump(by_alias=True) == {
        "shuchu_yi": "甲乙",
        "shuchu_er": "",
    }

    query_schema = test_case_cls.query_cls.model_json_schema(by_alias=True)
    answer_schema = test_case_cls.answer_cls.model_json_schema(by_alias=True)
    test_case_schema = test_case_cls.model_json_schema(by_alias=True)
    assert query_schema["title"] == f"DelineationQuery_{_LOCALIZED_PROMPT.name}"
    assert list(query_schema["properties"]) == [
        "cankao_yi",
        "cankao_er",
        "mubiao_yi",
        "mubiao_er",
    ]
    assert query_schema["required"] == ["cankao_yi", "cankao_er"]
    assert query_schema["properties"]["cankao_yi"]["description"] == ("第一條參考字幕")
    assert query_schema["properties"]["mubiao_er"]["default"] == ""
    assert answer_schema["title"] == f"DelineationAnswer_{_LOCALIZED_PROMPT.name}"
    assert list(answer_schema["properties"]) == ["shuchu_yi", "shuchu_er"]
    assert answer_schema["properties"]["shuchu_er"]["description"] == (
        "第二條調整後目標字幕"
    )
    assert answer_schema["properties"]["shuchu_yi"]["default"] == ""
    assert test_case_schema["title"] == (
        f"DelineationTestCase_{_LOCALIZED_PROMPT.name}"
    )


def test_queryer_corresponds_using_prompt_aliases():
    """Queryer should send aliased queries and request aliased answers."""
    test_case_cls = DelineationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "reference_one": "參考一",
                "reference_two": "參考二",
                "target_one": "甲",
                "target_two": "乙",
            }
        }
    )
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = json.dumps(
        {"shuchu_yi": "甲乙"},
        ensure_ascii=False,
    )
    queryer = Queryer(test_case_cls, provider=provider, max_attempts=1)

    result = queryer(test_case)

    assert result.answer is not None
    assert result.answer.model_dump() == {
        "output_one": "甲乙",
        "output_two": "",
    }
    messages, answer_cls, _ = provider.chat_completion.call_args.args
    assert answer_cls is test_case_cls.answer_cls
    assert json.loads(messages[1]["content"]) == {
        "cankao_yi": "參考一",
        "cankao_er": "參考二",
        "mubiao_yi": "甲",
        "mubiao_er": "乙",
    }


@mark.parametrize(
    "answer",
    [
        {"output_one": "甲乙"},
        {"shuchu_yii": "甲乙"},
    ],
    ids=["semantic-name", "misspelled-alias"],
)
def test_queryer_rejects_noncanonical_answer_fields(answer: dict[str, str]):
    """LLM answers should contain only the localized schema's field aliases."""
    test_case_cls = DelineationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "reference_one": "參考一",
                "reference_two": "參考二",
                "target_one": "甲",
                "target_two": "乙",
            }
        }
    )
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = json.dumps(answer, ensure_ascii=False)
    queryer = Queryer(test_case_cls, provider=provider, max_attempts=1)

    with raises(ValidationError):
        queryer(test_case)


def test_static_models_validate_target_presence_and_boundary_shifts():
    """Static models should validate targets, shifts, characters, and difficulty."""
    query = {
        "reference_one": "reference one",
        "reference_two": "reference two",
        "target_one": "ab",
        "target_two": "cd",
    }
    no_shift = DelineationTestCase.model_validate({"query": query, "answer": {}})
    shifted = DelineationTestCase.model_validate(
        {
            "query": query,
            "answer": {"output_one": "abc", "output_two": "d"},
        }
    )
    explicitly_difficult = DelineationTestCase.model_validate(
        {"query": query, "difficulty": 3}
    )

    assert no_shift.difficulty == 0
    assert shifted.difficulty == 1
    assert explicitly_difficult.difficulty == 3
    with raises(
        ValidationError,
        match=DelineationManager.base_prompt.src_2_sub_1_sub_2_missing_err,
    ):
        DelineationTestCase.model_validate(
            {
                "query": {
                    "reference_one": "reference one",
                    "reference_two": "reference two",
                }
            }
        )
    with raises(
        ValidationError,
        match=DelineationManager.base_prompt.src_2_sub_1_sub_2_unchanged_err,
    ):
        DelineationTestCase.model_validate(
            {
                "query": query,
                "answer": {"output_one": "ab", "output_two": "cd"},
            }
        )
    with raises(ValidationError, match="Expected: abcd"):
        DelineationTestCase.model_validate(
            {
                "query": query,
                "answer": {"output_one": "ab", "output_two": "changed"},
            }
        )


def test_generated_models_use_prompt_specific_validation_errors():
    """Generated model validation should report errors from its prompt."""
    test_case_cls = DelineationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    query = {
        "reference_one": "參考一",
        "reference_two": "參考二",
        "target_one": "甲",
        "target_two": "乙",
    }

    with raises(
        ValidationError,
        match=_LOCALIZED_PROMPT.src_2_sub_1_sub_2_missing_err,
    ):
        test_case_cls.model_validate(
            {
                "query": {
                    "reference_one": "參考一",
                    "reference_two": "參考二",
                }
            }
        )
    with raises(
        ValidationError,
        match=_LOCALIZED_PROMPT.src_2_sub_1_sub_2_unchanged_err,
    ):
        test_case_cls.model_validate(
            {
                "query": query,
                "answer": {"output_one": "甲", "output_two": "乙"},
            }
        )
    with raises(ValidationError, match="調整後目標字幕字元不一致"):
        test_case_cls.model_validate(
            {
                "query": query,
                "answer": {"output_one": "甲", "output_two": "丙"},
            }
        )


def test_persistence_uses_base_prompt_aliases_and_omits_defaults(tmp_path: Path):
    """Persisted JSON should use base aliases and omit default-valued fields."""
    test_case_cls = DelineationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "reference_one": "參考一",
                "reference_two": "參考二",
                "target_one": "甲",
            },
            "answer": {"output_two": "甲"},
            "verified": True,
        }
    )
    output_path = tmp_path / "delineation.json"

    save_test_cases_to_json(output_path, [test_case], DelineationManager)

    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        {
            "query": {
                "src_1_sub_1": "參考一",
                "src_1_sub_2": "參考二",
                "src_2_sub_1": "甲",
            },
            "answer": {"src_2_sub_2_shifted": "甲"},
            "difficulty": 1,
            "verified": True,
        }
    ]
    persisted = PersistedTestCase.from_test_case(test_case, DelineationManager)
    assert persisted.query == {
        "src_1_sub_1": "參考一",
        "src_1_sub_2": "參考二",
        "src_2_sub_1": "甲",
        "src_2_sub_2": "",
    }
    assert persisted.answer == {
        "src_2_sub_1_shifted": "",
        "src_2_sub_2_shifted": "甲",
    }

    loaded = load_test_cases_from_json(
        output_path,
        DelineationManager,
        _LOCALIZED_PROMPT,
    )
    assert loaded[0].model_dump() == test_case.model_dump()


def test_tracked_fixture_count():
    """All four tracked delineation files should contain 4,252 test cases."""
    counts = [
        len(json.loads(input_path.read_text(encoding="utf-8")))
        for input_path in _DELINEATION_PATHS
    ]

    assert len(_DELINEATION_PATHS) == 4
    assert sum(counts) == 4252


@mark.parametrize(
    "input_path",
    _DELINEATION_PATHS,
    ids=[
        input_path.relative_to(test_data_root).as_posix()
        for input_path in _DELINEATION_PATHS
    ],
)
def test_tracked_fixture_round_trips_without_migration(
    input_path: Path,
    tmp_path: Path,
):
    """Tracked JSON should round-trip exactly and to equivalent static models."""
    raw_data = json.loads(input_path.read_text(encoding="utf-8"))
    test_cases = load_test_cases_from_json(
        input_path,
        DelineationManager,
        YueDelineationVsZhoPromptYueHans,
    )
    output_path = tmp_path / input_path.name

    save_test_cases_to_json(output_path, test_cases, DelineationManager)
    reloaded = load_test_cases_from_json(
        output_path,
        DelineationManager,
        YueDelineationVsZhoPromptYueHans,
    )

    assert json.loads(output_path.read_text(encoding="utf-8")) == raw_data
    assert [test_case.model_dump() for test_case in reloaded] == [
        test_case.model_dump() for test_case in test_cases
    ]
