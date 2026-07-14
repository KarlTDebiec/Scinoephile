#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for list-shaped gap-translation LLM models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast
from unittest.mock import Mock

from pydantic import ValidationError
from pytest import mark, raises

from scinoephile import common
from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, Queryer
from scinoephile.core.llms.utils import (
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.gap_translation import (
    GapTranslationAnswer,
    GapTranslationManager,
    GapTranslationProcessor,
    GapTranslationPrompt,
    GapTranslationTestCase,
)
from test.helpers import assert_series_equal

_LOCALIZED_PROMPT = GapTranslationPrompt(
    language=Language.zho_hant,
    targets="mubiao",
    guides="cankao",
    outputs="shuchu",
    index="xuhao",
    text="wenben",
)
"""Gap-translation prompt with Chinese correspondence field names."""


def test_prompt_aliases_are_used_for_llm_correspondence():
    """Generated schemas and JSON should use prompt-specific aliases."""
    test_case_cls = GapTranslationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "mubiao": [
                    {"xuhao": 1, "wenben": "現有一"},
                    {"xuhao": 3, "wenben": "現有三"},
                ],
                "cankao": [
                    {"xuhao": 1, "wenben": "參考一"},
                    {"xuhao": 2, "wenben": "參考二"},
                    {"xuhao": 3, "wenben": "參考三"},
                ],
            },
            "answer": {"shuchu": [{"xuhao": 2, "wenben": "翻譯二"}]},
        }
    )

    assert test_case.query.model_dump(by_alias=True) == {
        "mubiao": [
            {"xuhao": 1, "wenben": "現有一"},
            {"xuhao": 3, "wenben": "現有三"},
        ],
        "cankao": [
            {"xuhao": 1, "wenben": "參考一"},
            {"xuhao": 2, "wenben": "參考二"},
            {"xuhao": 3, "wenben": "參考三"},
        ],
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump(by_alias=True) == {
        "shuchu": [{"xuhao": 2, "wenben": "翻譯二"}]
    }
    assert set(test_case_cls.query_cls.model_json_schema()["properties"]) == {
        "mubiao",
        "cankao",
    }
    assert set(test_case_cls.answer_cls.model_json_schema()["properties"]) == {"shuchu"}


def test_queryer_corresponds_using_prompt_aliases():
    """Queryer should send aliased lists and request an aliased answer."""
    test_case_cls = GapTranslationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "現有"}],
                "guides": [
                    {"index": 1, "text": "參考一"},
                    {"index": 2, "text": "參考二"},
                ],
            }
        }
    )
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = (
        '{"shuchu": [{"xuhao": 2, "wenben": "翻譯"}]}'
    )
    queryer = Queryer(test_case_cls, provider=provider, max_attempts=1)

    result = queryer(test_case)

    assert result.answer is not None
    messages, answer_cls, _ = provider.chat_completion.call_args.args
    assert answer_cls is test_case_cls.answer_cls
    assert json.loads(messages[1]["content"]) == {
        "mubiao": [{"xuhao": 1, "wenben": "現有"}],
        "cankao": [
            {"xuhao": 1, "wenben": "參考一"},
            {"xuhao": 2, "wenben": "參考二"},
        ],
    }


def test_query_requires_nonempty_consecutive_guides():
    """Guide indexes should be nonempty, consecutive, ordered, and one-based."""
    query_cls = GapTranslationManager.get_query_cls(GapTranslationManager.base_prompt)

    with raises(ValidationError, match="at least 1 item"):
        query_cls.model_validate({"targets": [], "guides": []})
    with raises(ValidationError, match="consecutive, ordered, and begin at 1"):
        query_cls.model_validate(
            {
                "targets": [],
                "guides": [
                    {"index": 1, "text": "one"},
                    {"index": 3, "text": "three"},
                ],
            }
        )


def test_query_requires_ordered_unique_target_indexes():
    """Target indexes should be unique and in ascending order."""
    query_cls = GapTranslationManager.get_query_cls(GapTranslationManager.base_prompt)

    with raises(ValidationError, match="unique and in ascending order"):
        query_cls.model_validate(
            {
                "targets": [
                    {"index": 2, "text": "two"},
                    {"index": 1, "text": "one"},
                ],
                "guides": [
                    {"index": 1, "text": "one"},
                    {"index": 2, "text": "two"},
                    {"index": 3, "text": "three"},
                ],
            }
        )


def test_query_requires_targets_to_be_sparse_guide_subset():
    """Targets should be a proper subset of guide indexes."""
    query_cls = GapTranslationManager.get_query_cls(GapTranslationManager.base_prompt)
    guides = [
        {"index": 1, "text": "one"},
        {"index": 2, "text": "two"},
    ]

    with raises(ValidationError, match="correspond to a guide index"):
        query_cls.model_validate(
            {
                "targets": [{"index": 3, "text": "three"}],
                "guides": guides,
            }
        )
    with raises(ValidationError, match="omit at least one guide index"):
        query_cls.model_validate(
            {
                "targets": [
                    {"index": 1, "text": "one"},
                    {"index": 2, "text": "two"},
                ],
                "guides": guides,
            }
        )


def test_answer_requires_ordered_unique_outputs():
    """Output indexes should be unique and in ascending order."""
    answer_cls = GapTranslationManager.get_answer_cls(GapTranslationManager.base_prompt)

    with raises(ValidationError, match="unique and in ascending order"):
        answer_cls.model_validate(
            {
                "outputs": [
                    {"index": 2, "text": "two"},
                    {"index": 1, "text": "one"},
                ]
            }
        )


def test_answer_allows_empty_output_text():
    """An indexed output may be structurally present with empty text."""
    answer_cls = GapTranslationManager.get_answer_cls(GapTranslationManager.base_prompt)

    answer = cast(
        GapTranslationAnswer,
        answer_cls.model_validate({"outputs": [{"index": 1, "text": ""}]}),
    )

    assert answer.outputs[0].text == ""


def test_gap_translation_preserves_unbounded_text():
    """Target, guide, and output text should retain their legacy unbounded length."""
    query_cls = GapTranslationManager.get_query_cls(GapTranslationManager.base_prompt)
    answer_cls = GapTranslationManager.get_answer_cls(GapTranslationManager.base_prompt)
    long_text = "x" * 1001

    query_cls.model_validate(
        {
            "targets": [{"index": 1, "text": long_text}],
            "guides": [
                {"index": 1, "text": long_text},
                {"index": 2, "text": long_text},
            ],
        }
    )
    answer_cls.model_validate({"outputs": [{"index": 2, "text": long_text}]})


@mark.parametrize(
    "test_case_cls",
    [
        GapTranslationTestCase,
        GapTranslationManager.get_test_case_cls(GapTranslationManager.base_prompt),
    ],
    ids=["static", "generated"],
)
def test_test_case_requires_outputs_to_exactly_fill_gaps(
    test_case_cls: type[GapTranslationTestCase],
):
    """Output indexes should exactly complement target indexes within guides."""
    query = {
        "targets": [{"index": 1, "text": "one"}],
        "guides": [
            {"index": 1, "text": "one"},
            {"index": 2, "text": "two"},
            {"index": 3, "text": "three"},
        ],
    }

    with raises(ValidationError, match="exactly match guide indexes"):
        test_case_cls.model_validate(
            {
                "query": query,
                "answer": {"outputs": [{"index": 2, "text": "translated two"}]},
            }
        )

    test_case = test_case_cls.model_validate(
        {
            "query": query,
            "answer": {
                "outputs": [
                    {"index": 2, "text": "translated two"},
                    {"index": 3, "text": "translated three"},
                ]
            },
        }
    )
    assert test_case.answer is not None
    assert [output.index for output in test_case.answer.outputs] == [2, 3]


def test_json_persistence_uses_base_prompt_fields(tmp_path: Path):
    """JSON should persist base fields and load prompt-specific aliases."""
    test_case_cls = GapTranslationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "mubiao": [{"xuhao": 1, "wenben": "現有"}],
                "cankao": [
                    {"xuhao": 1, "wenben": "參考一"},
                    {"xuhao": 2, "wenben": "參考二"},
                ],
            },
            "answer": {"shuchu": [{"xuhao": 2, "wenben": "翻譯"}]},
            "verified": True,
        }
    )
    output_path = tmp_path / "test_cases.json"

    save_test_cases_to_json(output_path, [test_case], GapTranslationManager)

    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        {
            "query": {
                "targets": [{"index": 1, "text": "現有"}],
                "guides": [
                    {"index": 1, "text": "參考一"},
                    {"index": 2, "text": "參考二"},
                ],
            },
            "answer": {"outputs": [{"index": 2, "text": "翻譯"}]},
            "verified": True,
        }
    ]
    loaded = load_test_cases_from_json(
        output_path,
        GapTranslationManager,
        _LOCALIZED_PROMPT,
    )
    assert loaded[0].query.model_dump(by_alias=True) == {
        "mubiao": [{"xuhao": 1, "wenben": "現有"}],
        "cankao": [
            {"xuhao": 1, "wenben": "參考一"},
            {"xuhao": 2, "wenben": "參考二"},
        ],
    }
    assert loaded[0].answer is not None
    assert loaded[0].answer.model_dump(by_alias=True) == {
        "shuchu": [{"xuhao": 2, "wenben": "翻譯"}]
    }


def test_processor_maps_targets_and_outputs_by_index():
    """Processor should combine existing targets and translated gaps by index."""
    prompt = GapTranslationManager.base_prompt
    test_case_cls = GapTranslationManager.get_test_case_cls(prompt)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "targets": [
                    {"index": 1, "text": "existing one"},
                    {"index": 3, "text": "existing three"},
                ],
                "guides": [
                    {"index": 1, "text": "guide one"},
                    {"index": 2, "text": "guide two"},
                    {"index": 3, "text": "guide three"},
                ],
            },
            "answer": {"outputs": [{"index": 2, "text": "translated two"}]},
            "verified": True,
        }
    )
    source_one = Series(
        events=[
            Subtitle(start=0, end=100, text="existing one"),
            Subtitle(start=200, end=300, text="existing three"),
        ]
    )
    source_two = Series(
        events=[
            Subtitle(start=0, end=100, text="guide one"),
            Subtitle(start=100, end=200, text="guide two"),
            Subtitle(start=200, end=300, text="guide three"),
        ]
    )
    expected = Series(
        events=[
            Subtitle(start=0, end=100, text="existing one"),
            Subtitle(start=100, end=200, text="translated two"),
            Subtitle(start=200, end=300, text="existing three"),
        ]
    )
    provider = Mock(spec=LLMProvider)
    processor = GapTranslationProcessor(
        prompt,
        test_cases=[test_case],
        provider=provider,
    )

    output = processor.process(source_one, source_two)

    assert_series_equal(output, expected)
    provider.chat_completion.assert_not_called()


def test_processor_honors_zero_stop_index():
    """A zero stop index should process no gap-translation blocks."""
    provider = Mock(spec=LLMProvider)
    processor = GapTranslationProcessor(
        GapTranslationManager.base_prompt,
        provider=provider,
    )
    source_one = Series(events=[Subtitle(start=0, end=100, text="existing one")])
    source_two = Series(
        events=[
            Subtitle(start=0, end=100, text="guide one"),
            Subtitle(start=100, end=200, text="guide two"),
        ]
    )

    output = processor.process(source_one, source_two, stop_at_idx=0)

    assert len(output) == 0
    provider.chat_completion.assert_not_called()


def test_processor_rejects_negative_stop_index():
    """A negative stop index should be rejected."""
    processor = GapTranslationProcessor(
        GapTranslationManager.base_prompt,
        provider=Mock(spec=LLMProvider),
    )
    source = Series(events=[Subtitle(start=0, end=100, text="subtitle")])

    with raises(ValueError, match="greater than or equal to 0"):
        processor.process(source, source, stop_at_idx=-1)


def test_repository_json_fixtures_load():
    """All repository gap-translation fixtures should use the canonical list shape."""
    fixture_paths = sorted(
        (common.package_root.parent / "test/data").glob(
            "*/output/yue-Hans_transcribe/lang/yue_zho/gap_translation/*.json"
        )
    )

    test_cases = [
        test_case
        for fixture_path in fixture_paths
        for test_case in load_test_cases_from_json(
            fixture_path,
            GapTranslationManager,
            GapTranslationManager.base_prompt,
        )
    ]

    assert len(fixture_paths) == 2
    assert len(test_cases) == 24
    assert all(
        cast(GapTranslationTestCase, test_case).query.guides for test_case in test_cases
    )
    assert all(test_case.answer is not None for test_case in test_cases)
