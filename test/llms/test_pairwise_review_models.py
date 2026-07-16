#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for static pairwise-review LLM models and prompt aliases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast
from unittest.mock import Mock

from pydantic import ValidationError
from pytest import mark, raises

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, Queryer
from scinoephile.core.llms.models import get_model_name
from scinoephile.core.llms.utils import (
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.pairwise_review import (
    PairwiseReviewAnswer,
    PairwiseReviewManager,
    PairwiseReviewProcessor,
    PairwiseReviewPrompt,
    PairwiseReviewQuery,
    PairwiseReviewTestCase,
)
from test.helpers import test_data_root

_LOCALIZED_PROMPT = PairwiseReviewPrompt(
    language=Language.zho_hant,
    target="mubiao",
    target_desc="要校對的字幕",
    reference="cankao",
    reference_desc="對應的參考字幕",
    output="shuchu",
    output_desc="修改後的字幕，沒有修改時為空字串",
    note="beizhu",
    note_desc="修改說明，沒有修改時為空字串",
    note_missing_err="本地化答案缺少修改說明。",
    output_missing_err="本地化答案缺少修改字幕。",
)
"""Pairwise-review prompt with localized correspondence field names."""

_FIXTURES = [
    (
        "mlamd/output/yue-Hans_transcribe/lang/yue_zho/pairwise_review/cuda.json",
        808,
        516,
    ),
    (
        "mlamd/output/yue-Hans_transcribe/lang/yue_zho/pairwise_review/mps.json",
        802,
        511,
    ),
]
"""Tracked pairwise-review fixture paths, case counts, and unchanged counts."""


def test_static_models_use_semantic_fields():
    """Public static models should be usable without a manager factory."""
    query = PairwiseReviewQuery(target="original", reference="reference")
    answer = PairwiseReviewAnswer(output="corrected", note="typo")
    test_case = PairwiseReviewTestCase(query=query, answer=answer)

    assert PairwiseReviewTestCase.query_cls is PairwiseReviewQuery
    assert PairwiseReviewTestCase.answer_cls is PairwiseReviewAnswer
    assert test_case.model_dump() == {
        "query": {"target": "original", "reference": "reference"},
        "answer": {"output": "corrected", "note": "typo"},
        "difficulty": 1,
        "few_shot": False,
        "verified": False,
    }


def test_manager_generates_aliases_without_changing_semantic_fields_or_schema():
    """Generated models should retain stable fields and prompt-specific schemas."""
    test_case_cls = PairwiseReviewManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = cast(
        PairwiseReviewTestCase,
        test_case_cls.model_validate(
            {
                "query": {"mubiao": "原文", "cankao": "參考"},
                "answer": {"shuchu": "修改", "beizhu": "修正錯字"},
            }
        ),
    )

    assert issubclass(test_case_cls, PairwiseReviewTestCase)
    assert list(test_case_cls.query_cls.model_fields) == ["target", "reference"]
    assert list(test_case_cls.answer_cls.model_fields) == ["output", "note"]
    assert test_case.query.target == "原文"
    assert test_case.query.reference == "參考"
    assert test_case.query.model_dump(by_alias=True) == {
        "mubiao": "原文",
        "cankao": "參考",
    }
    assert test_case.answer is not None
    assert test_case.answer.output == "修改"
    assert test_case.answer.note == "修正錯字"
    assert test_case.answer.model_dump(by_alias=True) == {
        "shuchu": "修改",
        "beizhu": "修正錯字",
    }

    query_schema = test_case_cls.query_cls.model_json_schema(by_alias=True)
    answer_schema = test_case_cls.answer_cls.model_json_schema(by_alias=True)
    assert query_schema["title"] == get_model_name(
        "PairwiseReviewQuery", _LOCALIZED_PROMPT.name
    )
    assert answer_schema["title"] == get_model_name(
        "PairwiseReviewAnswer", _LOCALIZED_PROMPT.name
    )
    assert list(query_schema["properties"]) == ["mubiao", "cankao"]
    assert query_schema["required"] == ["mubiao", "cankao"]
    assert query_schema["properties"]["mubiao"]["description"] == (
        _LOCALIZED_PROMPT.target_desc
    )
    assert query_schema["properties"]["cankao"]["description"] == (
        _LOCALIZED_PROMPT.reference_desc
    )
    assert query_schema["properties"]["mubiao"]["maxLength"] == 1000
    assert query_schema["properties"]["cankao"]["maxLength"] == 1000
    assert list(answer_schema["properties"]) == ["shuchu", "beizhu"]
    assert "required" not in answer_schema
    assert answer_schema["properties"]["shuchu"]["description"] == (
        _LOCALIZED_PROMPT.output_desc
    )
    assert answer_schema["properties"]["beizhu"]["description"] == (
        _LOCALIZED_PROMPT.note_desc
    )
    assert answer_schema["properties"]["shuchu"]["default"] == ""
    assert answer_schema["properties"]["beizhu"]["default"] == ""
    assert answer_schema["properties"]["shuchu"]["maxLength"] == 1000
    assert answer_schema["properties"]["beizhu"]["maxLength"] == 1000


def test_queryer_corresponds_using_prompt_aliases():
    """Queryer should send aliased queries and request aliased answers."""
    test_case_cls = PairwiseReviewManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = cast(
        PairwiseReviewTestCase,
        test_case_cls.model_validate(
            {"query": {"target": "原文", "reference": "參考"}}
        ),
    )
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = '{"shuchu": "修改", "beizhu": "修正錯字"}'
    queryer = Queryer(test_case_cls, provider=provider, max_attempts=1)

    result = cast(PairwiseReviewTestCase, queryer(test_case))

    assert result.answer is not None
    assert result.answer.output == "修改"
    assert result.answer.note == "修正錯字"
    messages, answer_cls, _ = provider.chat_completion.call_args.args
    assert answer_cls is test_case_cls.answer_cls
    assert json.loads(messages[1]["content"]) == {
        "mubiao": "原文",
        "cankao": "參考",
    }


@mark.parametrize(
    "test_case_cls",
    [
        PairwiseReviewTestCase,
        PairwiseReviewManager.get_test_case_cls(PairwiseReviewManager.base_prompt),
    ],
    ids=["static", "generated"],
)
def test_unchanged_full_output_is_normalized(
    test_case_cls: type[PairwiseReviewTestCase],
):
    """Legacy unchanged full-text outputs and notes should become empty strings."""
    test_case = test_case_cls.model_validate(
        {
            "query": {"target": "original", "reference": "reference"},
            "answer": {"output": "original", "note": "legacy note"},
        }
    )

    assert test_case.answer is not None
    assert test_case.answer.model_dump() == {"output": "", "note": ""}
    assert test_case.difficulty == 0


@mark.parametrize(
    "test_case_cls",
    [
        PairwiseReviewTestCase,
        PairwiseReviewManager.get_test_case_cls(PairwiseReviewManager.base_prompt),
    ],
    ids=["static", "generated"],
)
def test_output_and_note_must_be_provided_together(
    test_case_cls: type[PairwiseReviewTestCase],
):
    """A changed or removal output should have a note, and vice versa."""
    query = {"target": "original", "reference": "reference"}

    with raises(ValidationError, match="target is revised, but no note is provided"):
        test_case_cls.model_validate(
            {
                "query": query,
                "answer": {"output": "corrected", "note": ""},
            }
        )
    with raises(ValidationError, match="target is unchanged, but a note is provided"):
        test_case_cls.model_validate(
            {
                "query": query,
                "answer": {"output": "", "note": "typo"},
            }
        )


@mark.parametrize(
    ("answer", "difficulty"),
    [
        (None, 0),
        ({}, 0),
        ({"output": "", "note": ""}, 0),
        ({"output": "original", "note": "legacy note"}, 0),
        ({"output": "corrected", "note": "typo"}, 1),
        ({"output": "�", "note": "no corresponding content"}, 1),
    ],
    ids=[
        "unanswered",
        "defaults",
        "unchanged",
        "legacy-unchanged",
        "revised",
        "removed",
    ],
)
@mark.parametrize(
    "test_case_cls",
    [
        PairwiseReviewTestCase,
        PairwiseReviewManager.get_test_case_cls(PairwiseReviewManager.base_prompt),
    ],
    ids=["static", "generated"],
)
def test_minimum_difficulty_covers_every_answer_state(
    answer: dict[str, str] | None,
    difficulty: int,
    test_case_cls: type[PairwiseReviewTestCase],
):
    """Only a changed or removal output should require difficulty one."""
    data: dict[str, object] = {
        "query": {"target": "original", "reference": "reference"}
    }
    if answer is not None:
        data["answer"] = answer

    test_case = test_case_cls.model_validate(data)

    assert test_case.difficulty == difficulty


@mark.parametrize(
    "test_case_cls",
    [
        PairwiseReviewTestCase,
        PairwiseReviewManager.get_test_case_cls(PairwiseReviewManager.base_prompt),
    ],
    ids=["static", "generated"],
)
def test_existing_difficulty_and_text_length_bounds_are_preserved(
    test_case_cls: type[PairwiseReviewTestCase],
):
    """Explicit higher difficulty and every legacy 1000-character bound should hold."""
    long_text = "x" * 1001
    test_case = test_case_cls.model_validate(
        {
            "query": {"target": "original", "reference": "reference"},
            "answer": {"output": "corrected", "note": "typo"},
            "difficulty": 2,
        }
    )
    assert test_case.difficulty == 2

    with raises(ValidationError, match="at most 1000 characters"):
        test_case_cls.model_validate(
            {"query": {"target": long_text, "reference": "reference"}}
        )
    with raises(ValidationError, match="at most 1000 characters"):
        test_case_cls.model_validate(
            {"query": {"target": "original", "reference": long_text}}
        )
    with raises(ValidationError, match="at most 1000 characters"):
        test_case_cls.model_validate(
            {
                "query": {"target": "original", "reference": "reference"},
                "answer": {"output": long_text, "note": "note"},
            }
        )
    with raises(ValidationError, match="at most 1000 characters"):
        test_case_cls.model_validate(
            {
                "query": {"target": "original", "reference": "reference"},
                "answer": {"output": "corrected", "note": long_text},
            }
        )


def test_generated_test_case_uses_prompt_specific_validation_errors():
    """Static validators should read errors from each generated model's prompt."""
    test_case_cls = PairwiseReviewManager.get_test_case_cls(_LOCALIZED_PROMPT)
    query = {"target": "原文", "reference": "參考"}

    with raises(ValidationError, match=_LOCALIZED_PROMPT.note_missing_err):
        test_case_cls.model_validate(
            {"query": query, "answer": {"output": "修改", "note": ""}}
        )
    with raises(ValidationError, match=_LOCALIZED_PROMPT.output_missing_err):
        test_case_cls.model_validate(
            {"query": query, "answer": {"output": "", "note": "修改說明"}}
        )


def test_json_persistence_uses_base_fields_and_loads_localized_aliases(
    tmp_path: Path,
):
    """JSON should persist base fields and reload prompt-specific aliases."""
    test_case_cls = PairwiseReviewManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {"mubiao": "原文", "cankao": "參考"},
            "answer": {"shuchu": "修改", "beizhu": "修正錯字"},
            "verified": True,
        }
    )
    output_path = tmp_path / "pairwise_review.json"

    save_test_cases_to_json(output_path, [test_case], PairwiseReviewManager)

    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        {
            "query": {"target": "原文", "reference": "參考"},
            "answer": {"output": "修改", "note": "修正錯字"},
            "difficulty": 1,
            "verified": True,
        }
    ]
    loaded = load_test_cases_from_json(
        output_path,
        PairwiseReviewManager,
        _LOCALIZED_PROMPT,
    )
    assert loaded[0].query.model_dump(by_alias=True) == {
        "mubiao": "原文",
        "cankao": "參考",
    }
    assert loaded[0].answer is not None
    assert loaded[0].answer.model_dump(by_alias=True) == {
        "shuchu": "修改",
        "beizhu": "修正錯字",
    }


def test_processor_builds_and_consumes_semantic_fields():
    """Processor should use stable attributes while corresponding with aliases."""
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = '{"shuchu": "修改", "beizhu": "修正錯字"}'
    processor = PairwiseReviewProcessor(_LOCALIZED_PROMPT, provider=provider)
    processor.queryer.cache_dir_path = None
    target = Series(events=[Subtitle(start=0, end=1000, text="原文")])
    reference = Series(events=[Subtitle(start=0, end=1000, text="參考")])

    output = processor.process(target, reference)

    assert [subtitle.text for subtitle in output] == ["修改"]
    messages = provider.chat_completion.call_args.args[0]
    assert json.loads(messages[1]["content"]) == {
        "mubiao": "原文",
        "cankao": "參考",
    }


@mark.parametrize(
    ("relative_path", "expected_count", "expected_unchanged_count"),
    _FIXTURES,
    ids=[relative_path for relative_path, _, _ in _FIXTURES],
)
def test_tracked_fixtures_round_trip_model_equivalently(
    relative_path: str,
    expected_count: int,
    expected_unchanged_count: int,
    tmp_path: Path,
):
    """All tracked files should save and reload after legacy normalization."""
    input_path = test_data_root / relative_path
    raw_test_cases = json.loads(input_path.read_text(encoding="utf-8"))
    test_cases = load_test_cases_from_json(
        input_path,
        PairwiseReviewManager,
        PairwiseReviewManager.base_prompt,
    )

    unchanged_count = 0
    for raw_test_case, test_case in zip(raw_test_cases, test_cases, strict=True):
        if raw_test_case["answer"]["output"] != raw_test_case["query"]["target"]:
            continue
        unchanged_count += 1
        assert test_case.answer is not None
        answer = cast(PairwiseReviewAnswer, test_case.answer)
        assert answer.output == ""
        assert answer.note == ""

    assert len(test_cases) == expected_count
    assert unchanged_count == expected_unchanged_count

    output_path = tmp_path / Path(relative_path).name
    save_test_cases_to_json(output_path, test_cases, PairwiseReviewManager)
    reloaded = load_test_cases_from_json(
        output_path,
        PairwiseReviewManager,
        PairwiseReviewManager.base_prompt,
    )

    assert [test_case.model_dump(mode="json") for test_case in reloaded] == [
        test_case.model_dump(mode="json") for test_case in test_cases
    ]
