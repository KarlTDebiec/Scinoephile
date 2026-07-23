#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for static OCR-fusion LLM models and prompt aliases."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock

from pydantic import ValidationError
from pytest import mark, raises

from scinoephile.core import Language
from scinoephile.core.llms import Answer, LLMProvider, Query, Queryer
from scinoephile.core.llms.models import get_model_name
from scinoephile.core.llms.utils import (
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.ocr_fusion import (
    OcrFusionAnswer,
    OcrFusionManager,
    OcrFusionProcessor,
    OcrFusionPrompt,
    OcrFusionQuery,
    OcrFusionTestCase,
)
from scinoephile.optimization.persistence.test_cases import (
    PersistedTestCase,
    TestCaseSqliteStore,
)
from test.helpers import test_data_root

_LOCALIZED_PROMPT = OcrFusionPrompt(
    language=Language.zho_hant,
    src_1="yilai",
    src_1_desc="來源一字幕",
    src_2="erlai",
    src_2_desc="來源二字幕",
    src_1_missing_err="必須提供來源一字幕。",
    src_2_missing_err="必須提供來源二字幕。",
    src_1_src_2_equal_err="兩個來源字幕必須不同。",
    output="jieguo",
    output_desc="融合後字幕",
    note="shuoming",
    note_desc="融合說明",
    output_missing_err="必須提供融合後字幕。",
    note_missing_err="必須提供融合說明。",
)
"""OCR-fusion prompt with localized correspondence field names and errors."""


def test_static_models_use_semantic_fields():
    """Public static models should use prompt-independent semantic fields."""
    query = OcrFusionQuery(source_one="source one", source_two="source two")
    answer = OcrFusionAnswer(output="source one", note="selected source one")
    test_case = OcrFusionTestCase(query=query, answer=answer)

    assert query.model_dump() == {
        "source_one": "source one",
        "source_two": "source two",
    }
    assert answer.model_dump() == {
        "output": "source one",
        "note": "selected source one",
    }
    assert test_case.query is query
    assert test_case.answer is answer


def test_generated_models_preserve_aliases_and_llm_schemas():
    """Generated models should preserve localized aliases and legacy schemas."""
    query_cls = OcrFusionManager.get_query_cls(_LOCALIZED_PROMPT)
    answer_cls = OcrFusionManager.get_answer_cls(_LOCALIZED_PROMPT)

    query = query_cls.model_validate({"source_one": "來源一", "source_two": "來源二"})
    answer = answer_cls.model_validate({"output": "融合結果", "note": "融合說明"})

    assert tuple(query_cls.model_fields) == ("source_one", "source_two")
    assert tuple(answer_cls.model_fields) == ("output", "note")
    assert query.model_dump() == {"source_one": "來源一", "source_two": "來源二"}
    assert query.model_dump(by_alias=True) == {"yilai": "來源一", "erlai": "來源二"}
    assert answer.model_dump(by_alias=True) == {
        "jieguo": "融合結果",
        "shuoming": "融合說明",
    }

    query_schema = query_cls.model_json_schema(by_alias=True)
    answer_schema = answer_cls.model_json_schema(by_alias=True)
    assert query_schema == {
        "additionalProperties": False,
        "properties": {
            "yilai": {
                "description": "來源一字幕",
                "title": "Yilai",
                "type": "string",
            },
            "erlai": {
                "description": "來源二字幕",
                "title": "Erlai",
                "type": "string",
            },
        },
        "required": ["yilai", "erlai"],
        "title": get_model_name(Query.__name__, _LOCALIZED_PROMPT.name),
        "type": "object",
    }
    assert answer_schema == {
        "additionalProperties": False,
        "properties": {
            "jieguo": {
                "description": "融合後字幕",
                "title": "Jieguo",
                "type": "string",
            },
            "shuoming": {
                "description": "融合說明",
                "title": "Shuoming",
                "type": "string",
            },
        },
        "required": ["jieguo", "shuoming"],
        "title": get_model_name(Answer.__name__, _LOCALIZED_PROMPT.name),
        "type": "object",
    }


def test_static_models_use_prompt_aware_validation_errors():
    """Static models should reject absent, empty, or equal content."""
    with raises(ValidationError, match="source one is required"):
        OcrFusionQuery.model_validate({"source_two": "source two"})
    with raises(ValidationError, match="source two is required"):
        OcrFusionQuery.model_validate({"source_one": "source one"})
    with raises(ValidationError, match="source one is required"):
        OcrFusionQuery(source_one="", source_two="source two")
    with raises(ValidationError, match="two sources must differ"):
        OcrFusionQuery(source_one="same", source_two="same")
    with raises(ValidationError, match="Output subtitle text is required"):
        OcrFusionAnswer.model_validate({"note": "explanation"})
    with raises(ValidationError, match="Explanation of output is required"):
        OcrFusionAnswer.model_validate({"output": "fused"})
    with raises(ValidationError, match="Output subtitle text is required"):
        OcrFusionAnswer(output="", note="explanation")
    with raises(ValidationError, match="Explanation of output is required"):
        OcrFusionAnswer(output="fused", note="")


def test_generated_models_use_localized_validation_errors():
    """Generated models should validate aliases using their localized prompt."""
    query_cls = OcrFusionManager.get_query_cls(_LOCALIZED_PROMPT)
    answer_cls = OcrFusionManager.get_answer_cls(_LOCALIZED_PROMPT)

    with raises(ValidationError, match="必須提供來源一字幕"):
        query_cls.model_validate({"erlai": "來源二"})
    with raises(ValidationError, match="必須提供來源二字幕"):
        query_cls.model_validate({"yilai": "來源一"})
    with raises(ValidationError, match="兩個來源字幕必須不同"):
        query_cls.model_validate({"yilai": "相同", "erlai": "相同"})
    with raises(ValidationError, match="必須提供融合後字幕"):
        answer_cls.model_validate({"shuoming": "說明"})
    with raises(ValidationError, match="必須提供融合說明"):
        answer_cls.model_validate({"jieguo": "結果"})


@mark.parametrize(
    "test_case_cls",
    [
        OcrFusionTestCase,
        OcrFusionManager.get_test_case_cls(OcrFusionManager.base_prompt),
    ],
    ids=["static", "generated"],
)
@mark.parametrize(
    ("source_one", "source_two", "output", "expected_difficulty", "auto_verified"),
    [
        ("source one", "source two", None, 1, False),
        ("source one", "source two", "source one", 1, True),
        ("source one", "source two", "source two", 1, True),
        ("source one", "source two", "fused", 1, False),
        ("source\none", "source two", "source\none", 1, False),
        ("source one", "source\ntwo", "source\ntwo", 1, False),
        ("source-one", "source two", "source-one", 2, False),
        ('source "one"', "source two", 'source "one"', 2, False),
        ("“source one”", "source two", "“source one”", 2, False),
    ],
    ids=[
        "no-answer",
        "source-one",
        "source-two",
        "fused",
        "source-one-multiline",
        "source-two-multiline",
        "hyphen",
        "straight-quote",
        "curly-quotes",
    ],
)
def test_difficulty_and_auto_verification_matrix(
    test_case_cls: type[OcrFusionTestCase],
    source_one: str,
    source_two: str,
    output: str | None,
    expected_difficulty: int,
    auto_verified: bool,
):
    """Difficulty and auto-verification should retain legacy behavior."""
    data: dict[str, object] = {
        "query": {"source_one": source_one, "source_two": source_two}
    }
    if output is not None:
        data["answer"] = {"output": output, "note": "explanation"}

    test_case = test_case_cls.model_validate(data)

    assert test_case.difficulty == expected_difficulty
    assert test_case.get_auto_verified() is auto_verified


def test_queryer_corresponds_using_prompt_aliases():
    """Queryer should send and request localized correspondence fields."""
    test_case_cls = OcrFusionManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {"query": {"source_one": "來源一", "source_two": "來源二"}}
    )
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = (
        '{"jieguo": "來源一", "shuoming": "採用來源一"}'
    )
    queryer = Queryer(test_case_cls, provider=provider, max_attempts=1)

    result = queryer(test_case)

    assert result.answer is not None
    assert result.answer.model_dump() == {
        "output": "來源一",
        "note": "採用來源一",
    }
    messages, answer_cls, _ = provider.chat_completion.call_args.args
    assert answer_cls is test_case_cls.answer_cls
    assert json.loads(messages[1]["content"]) == {
        "yilai": "來源一",
        "erlai": "來源二",
    }


def test_processor_uses_semantic_fields_at_runtime():
    """Processor should build and consume the static semantic model shape."""
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = (
        '{"jieguo": "融合結果", "shuoming": "融合兩個來源"}'
    )
    processor = OcrFusionProcessor(_LOCALIZED_PROMPT, provider=provider)
    processor.queryer.cache_dir_path = None
    source_one = Series([Subtitle(start=0, end=1000, text="來源一")])
    source_two = Series([Subtitle(start=0, end=1000, text="來源二")])

    result = processor.process(source_one, source_two)

    assert [subtitle.text for subtitle in result] == ["融合結果"]
    messages = provider.chat_completion.call_args.args[0]
    assert json.loads(messages[1]["content"]) == {
        "yilai": "來源一",
        "erlai": "來源二",
    }


def test_processor_honors_zero_stop_index():
    """A zero stop index should process no OCR-fusion subtitles."""
    provider = Mock(spec=LLMProvider)
    processor = OcrFusionProcessor(_LOCALIZED_PROMPT, provider=provider)
    source_one = Series([Subtitle(start=0, end=1000, text="來源一")])
    source_two = Series([Subtitle(start=0, end=1000, text="來源二")])

    output = processor.process(source_one, source_two, stop_at_idx=0)

    assert len(output) == 0
    provider.chat_completion.assert_not_called()


def test_processor_rejects_negative_stop_index():
    """A negative stop index should be rejected."""
    processor = OcrFusionProcessor(
        _LOCALIZED_PROMPT,
        provider=Mock(spec=LLMProvider),
    )
    source = Series([Subtitle(start=0, end=1000, text="subtitle")])

    with raises(ValueError, match="greater than or equal to 0"):
        processor.process(source, source, stop_at_idx=-1)


def test_json_persistence_uses_base_prompt_aliases(tmp_path: Path):
    """JSON should retain base one/two fields across localized round trips."""
    test_case_cls = OcrFusionManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {"yilai": "來源一", "erlai": "來源二"},
            "answer": {"jieguo": "來源一", "shuoming": "採用來源一"},
            "verified": True,
        }
    )
    output_path = tmp_path / "ocr_fusion.json"

    save_test_cases_to_json(output_path, [test_case], OcrFusionManager)

    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        {
            "query": {"one": "來源一", "two": "來源二"},
            "answer": {"output": "來源一", "note": "採用來源一"},
            "difficulty": 1,
            "verified": True,
        }
    ]
    loaded = load_test_cases_from_json(
        output_path,
        OcrFusionManager,
        _LOCALIZED_PROMPT,
    )
    assert loaded[0].query.model_dump(by_alias=True) == {
        "yilai": "來源一",
        "erlai": "來源二",
    }
    assert loaded[0].answer is not None
    assert loaded[0].answer.model_dump(by_alias=True) == {
        "jieguo": "來源一",
        "shuoming": "採用來源一",
    }


def test_persisted_test_case_and_sqlite_use_base_prompt_aliases(tmp_path: Path):
    """Normalized persistence should store base one/two query fields."""
    test_case_cls = OcrFusionManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {"source_one": "來源一", "source_two": "來源二"},
            "answer": {"output": "來源一", "note": "採用來源一"},
        }
    )

    persisted = PersistedTestCase.from_test_case(test_case, OcrFusionManager)

    assert persisted.query == {"one": "來源一", "two": "來源二"}
    assert persisted.answer == {"output": "來源一", "note": "採用來源一"}

    store = TestCaseSqliteStore(tmp_path / "test_cases.sqlite")
    store.sync_source_paths(
        {"ocr_fusion.json": [persisted]},
        manager_cls=OcrFusionManager,
        dry_run=False,
    )
    loaded = store.get_test_case(persisted.test_case_id)
    assert loaded is not None
    assert loaded.query == {"one": "來源一", "two": "來源二"}
    assert loaded.answer == {"output": "來源一", "note": "採用來源一"}


def test_repository_json_fixtures_round_trip_without_rewrite():
    """All tracked OCR-fusion cases should survive localized model round trips."""
    input_paths = sorted(test_data_root.glob("*/output/*/lang/*/ocr_fusion.json"))
    base_test_case_cls = OcrFusionManager.get_test_case_cls(
        OcrFusionManager.base_prompt
    )
    total_test_cases = 0

    for input_path in input_paths:
        raw_test_cases = json.loads(input_path.read_text(encoding="utf-8"))
        localized_test_cases = load_test_cases_from_json(
            input_path,
            OcrFusionManager,
            _LOCALIZED_PROMPT,
        )
        assert len(localized_test_cases) == len(raw_test_cases)
        total_test_cases += len(localized_test_cases)

        for raw_test_case, localized_test_case in zip(
            raw_test_cases,
            localized_test_cases,
            strict=True,
        ):
            base_test_case = base_test_case_cls.model_validate(
                localized_test_case.model_dump(mode="json")
            )
            assert (
                base_test_case.model_dump(
                    mode="json",
                    by_alias=True,
                    exclude_defaults=True,
                )
                == raw_test_case
            )

    assert len(input_paths) == 26
    assert total_test_cases == 10_580
