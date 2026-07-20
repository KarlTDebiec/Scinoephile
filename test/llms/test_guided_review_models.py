#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for list-shaped guided-review LLM models and processing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast
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
from scinoephile.llms.guided_review import (
    GuidedReviewManager,
    GuidedReviewProcessor,
    GuidedReviewPrompt,
    GuidedReviewTestCase,
)

_LOCALIZED_PROMPT = GuidedReviewPrompt(
    language=Language.zho_hant,
    targets="mubiao",
    guides="zhinan",
    revisions="xiugai",
    index="xuhao",
    text="wenben",
    note="beizhu",
)
"""Guided-review prompt with localized correspondence field names."""


def test_prompt_aliases_are_used_for_llm_correspondence():
    """Generated schemas and JSON should use prompt-specific aliases."""
    test_case_cls = GuidedReviewManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "mubiao": [
                    {"xuhao": 1, "wenben": "原文一"},
                    {"xuhao": 2, "wenben": "原文二"},
                ],
                "zhinan": [{"xuhao": 1, "wenben": "參考"}],
            },
            "answer": {
                "xiugai": [
                    {
                        "xuhao": 2,
                        "wenben": "修改二",
                        "beizhu": "修正錯字",
                    }
                ]
            },
        }
    )

    assert test_case.query.model_dump(by_alias=True) == {
        "mubiao": [
            {"xuhao": 1, "wenben": "原文一"},
            {"xuhao": 2, "wenben": "原文二"},
        ],
        "zhinan": [{"xuhao": 1, "wenben": "參考"}],
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump(by_alias=True) == {
        "xiugai": [{"xuhao": 2, "wenben": "修改二", "beizhu": "修正錯字"}]
    }
    assert set(test_case_cls.query_cls.model_json_schema()["properties"]) == {
        "mubiao",
        "zhinan",
    }
    assert set(test_case_cls.answer_cls.model_json_schema()["properties"]) == {"xiugai"}


def test_queryer_corresponds_using_prompt_aliases():
    """Queryer should send aliased queries and request aliased answers."""
    test_case_cls = GuidedReviewManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "原文"}],
                "guides": [{"index": 1, "text": "參考"}],
            }
        }
    )
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = '{"xiugai": []}'
    queryer = Queryer(test_case_cls, provider=provider, max_attempts=1)
    queryer.cache_dir_path = None

    result = queryer(test_case)

    assert result.answer is not None
    messages, answer_cls, _ = provider.chat_completion.call_args.args
    assert answer_cls is test_case_cls.answer_cls
    assert json.loads(messages[1]["content"]) == {
        "mubiao": [{"xuhao": 1, "wenben": "原文"}],
        "zhinan": [{"xuhao": 1, "wenben": "參考"}],
    }


def test_processing_preserves_unencountered_few_shot_cases(tmp_path: Path):
    """A run should preserve unencountered reusable cases by default."""
    test_case_cls = GuidedReviewManager.get_test_case_cls(_LOCALIZED_PROMPT)
    old_test_case = test_case_cls.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "舊原文"}],
                "guides": [{"index": 1, "text": "參考"}],
            },
            "answer": {"revisions": []},
            "few_shot": True,
            "verified": True,
        }
    )
    test_case_path = tmp_path / "guided_review.json"
    save_test_cases_to_json(
        test_case_path,
        [old_test_case],
        GuidedReviewManager,
    )
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = '{"xiugai": []}'
    processor = GuidedReviewProcessor(
        _LOCALIZED_PROMPT,
        test_case_path=test_case_path,
        provider=provider,
    )
    processor.queryer.cache_dir_path = None
    target = Series(events=[Subtitle(start=0, end=100, text="新原文")])
    guide = Series(events=[Subtitle(start=0, end=100, text="參考")])

    processor.process(target, guide)

    persisted = load_test_cases_from_json(
        test_case_path,
        GuidedReviewManager,
        _LOCALIZED_PROMPT,
    )
    assert len(persisted) == 2
    persisted_cases = cast("list[GuidedReviewTestCase]", persisted)
    assert [item.query.targets[0].text for item in persisted_cases] == [
        "舊原文",
        "新原文",
    ]


def test_processor_honors_start_index():
    """An inclusive start index should skip earlier guided-review blocks."""
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = '{"xiugai": []}'
    processor = GuidedReviewProcessor(_LOCALIZED_PROMPT, provider=provider)
    processor.queryer.cache_dir_path = None
    target = Series(
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

    output = processor.process(target, guide, start_at_idx=1)

    assert [subtitle.text for subtitle in output] == ["原文二"]
    provider.chat_completion.assert_called_once()


def test_query_lists_require_items_and_consecutive_ordered_indexes():
    """Targets should be nonempty and both lists should use ordered indexes."""
    query_cls = GuidedReviewManager.get_query_cls(GuidedReviewManager.base_prompt)

    with raises(ValidationError, match="at least 1 item"):
        query_cls.model_validate(
            {"targets": [], "guides": [{"index": 1, "text": "guide"}]}
        )
    query = query_cls.model_validate(
        {"targets": [{"index": 1, "text": "target"}], "guides": []}
    )
    assert query.model_dump()["guides"] == []
    with raises(ValidationError, match="target indexes must be consecutive"):
        query_cls.model_validate(
            {
                "targets": [
                    {"index": 1, "text": "one"},
                    {"index": 3, "text": "three"},
                ],
                "guides": [{"index": 1, "text": "guide"}],
            }
        )
    with raises(ValidationError, match="guide indexes must be consecutive"):
        query_cls.model_validate(
            {
                "targets": [{"index": 1, "text": "target"}],
                "guides": [
                    {"index": 2, "text": "two"},
                    {"index": 1, "text": "one"},
                ],
            }
        )


def test_answer_requires_sparse_ordered_annotated_revisions():
    """Revisions should be ordered, unique, and include text and a note."""
    answer_cls = GuidedReviewManager.get_answer_cls(GuidedReviewManager.base_prompt)

    assert answer_cls.model_validate({"revisions": []}).model_dump(
        exclude_defaults=True
    ) == {"revisions": []}
    with raises(ValidationError, match="unique and in ascending order"):
        answer_cls.model_validate(
            {
                "revisions": [
                    {"index": 2, "text": "two", "note": "second"},
                    {"index": 1, "text": "one", "note": "first"},
                ]
            }
        )
    with raises(ValidationError, match="Field required"):
        answer_cls.model_validate({"revisions": [{"index": 1, "text": "revision"}]})


@mark.parametrize(
    "test_case_cls",
    [
        GuidedReviewTestCase,
        GuidedReviewManager.get_test_case_cls(GuidedReviewManager.base_prompt),
    ],
    ids=["static", "generated"],
)
def test_test_case_rejects_missing_and_unmodified_revision_indexes(
    test_case_cls: type[GuidedReviewTestCase],
):
    """Revisions should target and modify query target subtitles."""
    query = {
        "targets": [{"index": 1, "text": "original"}],
        "guides": [{"index": 1, "text": "guide"}],
    }

    with raises(ValidationError, match="does not correspond to a query target"):
        test_case_cls.model_validate(
            {
                "query": query,
                "answer": {
                    "revisions": [{"index": 2, "text": "changed", "note": "typo"}]
                },
            }
        )
    with raises(ValidationError, match="unchanged targets must be omitted"):
        test_case_cls.model_validate(
            {
                "query": query,
                "answer": {
                    "revisions": [{"index": 1, "text": "original", "note": "unchanged"}]
                },
            }
        )


@mark.parametrize(
    "test_case_cls",
    [
        GuidedReviewTestCase,
        GuidedReviewManager.get_test_case_cls(GuidedReviewManager.base_prompt),
    ],
    ids=["static", "generated"],
)
def test_revisions_raise_minimum_difficulty(
    test_case_cls: type[GuidedReviewTestCase],
):
    """A nonempty revisions list should require difficulty one."""
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "original"}],
                "guides": [],
            },
            "answer": {"revisions": [{"index": 1, "text": "revised", "note": "typo"}]},
        }
    )

    assert test_case.difficulty == 1


def test_list_cardinality_does_not_change_model_class():
    """One prompt-specific class should validate all target and guide list sizes."""
    test_case_cls = GuidedReviewManager.get_test_case_cls(
        GuidedReviewManager.base_prompt
    )
    one_by_one = test_case_cls.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "target"}],
                "guides": [{"index": 1, "text": "guide"}],
            },
            "answer": {"revisions": []},
        }
    )
    two_by_three = test_case_cls.model_validate(
        {
            "query": {
                "targets": [
                    {"index": 1, "text": "target one"},
                    {"index": 2, "text": "target two"},
                ],
                "guides": [
                    {"index": 1, "text": "guide one"},
                    {"index": 2, "text": "guide two"},
                    {"index": 3, "text": "guide three"},
                ],
            },
            "answer": {
                "revisions": [{"index": 2, "text": "revised", "note": "correction"}]
            },
        }
    )

    assert type(one_by_one) is type(two_by_three)
    assert one_by_one.difficulty == 0
    assert two_by_three.difficulty == 1


def test_json_uses_base_prompt_fields_and_loads_localized_aliases(tmp_path: Path):
    """JSON should persist base fields and load them into a localized prompt."""
    test_case_cls = GuidedReviewManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "mubiao": [{"xuhao": 1, "wenben": "原文"}],
                "zhinan": [{"xuhao": 1, "wenben": "參考"}],
            },
            "answer": {"xiugai": [{"xuhao": 1, "wenben": "修改", "beizhu": "錯字"}]},
            "verified": True,
        }
    )
    output_path = tmp_path / "guided_review.json"

    save_test_cases_to_json(output_path, [test_case], GuidedReviewManager)

    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        {
            "query": {
                "targets": [{"index": 1, "text": "原文"}],
                "guides": [{"index": 1, "text": "參考"}],
            },
            "answer": {"revisions": [{"index": 1, "text": "修改", "note": "錯字"}]},
            "difficulty": 1,
            "verified": True,
        }
    ]
    loaded = load_test_cases_from_json(
        output_path,
        GuidedReviewManager,
        _LOCALIZED_PROMPT,
    )
    assert loaded[0].query.model_dump(by_alias=True) == {
        "mubiao": [{"xuhao": 1, "wenben": "原文"}],
        "zhinan": [{"xuhao": 1, "wenben": "參考"}],
    }
    assert loaded[0].answer is not None
    assert loaded[0].answer.model_dump(by_alias=True) == {
        "xiugai": [{"xuhao": 1, "wenben": "修改", "beizhu": "錯字"}]
    }


def test_processor_uses_indexed_lists_and_applies_sparse_revisions():
    """Processor should send indexed lists and apply revisions by target index."""
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = json.dumps(
        {"xiugai": [{"xuhao": 2, "wenben": "修改二", "beizhu": "修正錯字"}]},
        ensure_ascii=False,
    )
    processor = GuidedReviewProcessor(_LOCALIZED_PROMPT, provider=provider)
    processor.queryer.cache_dir_path = None
    target = Series(
        events=[
            Subtitle(start=0, end=1000, text="原文一"),
            Subtitle(start=1100, end=2000, text="原文二"),
        ]
    )
    guide = Series(events=[Subtitle(start=0, end=2000, text="參考")])

    output = processor.process(target, guide)

    assert [subtitle.text for subtitle in output] == ["原文一", "修改二"]
    messages = provider.chat_completion.call_args.args[0]
    assert json.loads(messages[1]["content"]) == {
        "mubiao": [
            {"xuhao": 1, "wenben": "原文一"},
            {"xuhao": 2, "wenben": "原文二"},
        ],
        "zhinan": [{"xuhao": 1, "wenben": "參考"}],
    }
