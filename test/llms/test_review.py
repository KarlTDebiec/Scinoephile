#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for list-shaped review LLM models."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock

from pydantic import ValidationError
from pytest import mark, raises

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, Queryer
from scinoephile.core.llms.utils import save_test_cases_to_json
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.review import (
    ReviewManager,
    ReviewProcessor,
    ReviewPrompt,
    ReviewTestCase,
)

_LOCALIZED_PROMPT = ReviewPrompt(
    language=Language.zho_hant,
    subtitles="zimu",
    revisions="xiugai",
    index="xuhao",
    text="wenben",
    note="beizhu",
    revision_index_missing_err_tpl="修訂序號 {idx} 未對應字幕。",
)
"""Review prompt with Chinese correspondence field names."""


def test_prompt_aliases_are_used_for_llm_correspondence():
    """Generated schemas and JSON should use prompt-specific aliases."""
    test_case_cls = ReviewManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "zimu": [
                    {"xuhao": 1, "wenben": "原文一"},
                    {"xuhao": 2, "wenben": "原文二"},
                ]
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
        "zimu": [
            {"xuhao": 1, "wenben": "原文一"},
            {"xuhao": 2, "wenben": "原文二"},
        ]
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump(by_alias=True) == {
        "xiugai": [{"xuhao": 2, "wenben": "修改二", "beizhu": "修正錯字"}]
    }
    assert set(test_case_cls.query_cls.model_json_schema()["properties"]) == {"zimu"}
    assert set(test_case_cls.answer_cls.model_json_schema()["properties"]) == {"xiugai"}


def test_queryer_corresponds_using_prompt_aliases():
    """Queryer should send aliased queries and request aliased answers."""
    test_case_cls = ReviewManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {"query": {"subtitles": [{"index": 1, "text": "原文"}]}}
    )
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = '{"xiugai": []}'
    queryer = Queryer(_LOCALIZED_PROMPT, provider=provider, max_attempts=1)

    result = queryer(test_case)

    assert result.answer is not None
    messages = provider.chat_completion.call_args.args[0]
    assert json.loads(messages[1]["content"]) == {
        "zimu": [{"xuhao": 1, "wenben": "原文"}]
    }
    assert '"xiugai"' in messages[0]["content"]
    assert '"xuhao"' in messages[0]["content"]
    assert '"wenben"' in messages[0]["content"]
    assert '"beizhu"' in messages[0]["content"]


def test_partial_processing_preserves_unencountered_test_cases(tmp_path: Path):
    """Stopping before processing should not erase persisted test cases."""
    test_case_cls = ReviewManager.get_test_case_cls(ReviewManager.base_prompt)
    existing_test_case = test_case_cls.model_validate(
        {
            "query": {"subtitles": [{"index": 1, "text": "existing"}]},
            "answer": {"revisions": []},
            "verified": True,
        }
    )
    test_case_path = tmp_path / "review.json"
    save_test_cases_to_json(test_case_path, [existing_test_case], ReviewManager)
    original_contents = test_case_path.read_bytes()
    processor = ReviewProcessor(
        ReviewManager.base_prompt,
        test_case_path=test_case_path,
        provider=Mock(spec=LLMProvider),
    )
    series = Series(events=[Subtitle(start=0, end=1000, text="existing")])

    processor.process(series, stop_at_idx=0)

    assert test_case_path.read_bytes() == original_contents


def test_partial_processing_prunes_only_when_requested(tmp_path: Path):
    """Explicit pruning should remove cases not encountered in the current run."""
    test_case_cls = ReviewManager.get_test_case_cls(ReviewManager.base_prompt)
    existing_test_case = test_case_cls.model_validate(
        {
            "query": {"subtitles": [{"index": 1, "text": "existing"}]},
            "answer": {"revisions": []},
            "verified": True,
        }
    )
    test_case_path = tmp_path / "review.json"
    save_test_cases_to_json(test_case_path, [existing_test_case], ReviewManager)
    processor = ReviewProcessor(
        ReviewManager.base_prompt,
        test_case_path=test_case_path,
        provider=Mock(spec=LLMProvider),
        prune_test_cases=True,
    )
    series = Series(events=[Subtitle(start=0, end=1000, text="existing")])

    processor.process(series, stop_at_idx=0)

    assert json.loads(test_case_path.read_text(encoding="utf-8")) == []


def test_query_requires_consecutive_ordered_indexes():
    """Query subtitle indexes should be consecutive, ordered, and one-based."""
    query_cls = ReviewManager.get_query_cls(ReviewManager.base_prompt)

    with raises(ValidationError, match="consecutive, ordered, and begin at 1"):
        query_cls.model_validate(
            {
                "subtitles": [
                    {"index": 1, "text": "one"},
                    {"index": 3, "text": "three"},
                ]
            }
        )


def test_answer_requires_unique_ordered_revision_indexes():
    """Answer revision indexes should be unique and ordered."""
    answer_cls = ReviewManager.get_answer_cls(ReviewManager.base_prompt)

    with raises(ValidationError, match="unique and in ascending order"):
        answer_cls.model_validate(
            {
                "revisions": [
                    {"index": 2, "text": "two", "note": "second"},
                    {"index": 1, "text": "one", "note": "first"},
                ]
            }
        )


@mark.parametrize(
    "test_case_cls",
    [
        ReviewTestCase,
        ReviewManager.get_test_case_cls(ReviewManager.base_prompt),
    ],
    ids=["static", "generated"],
)
def test_test_case_rejects_missing_and_unmodified_revision_indexes(
    test_case_cls: type[ReviewTestCase],
):
    """Revisions should target and modify query subtitles."""
    query = {"subtitles": [{"index": 1, "text": "original"}]}

    with raises(ValidationError, match="does not correspond to a query subtitle"):
        test_case_cls.model_validate(
            {
                "query": query,
                "answer": {
                    "revisions": [{"index": 2, "text": "changed", "note": "typo"}]
                },
            }
        )
    with raises(ValidationError, match="unchanged subtitles must be omitted"):
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
        ReviewTestCase,
        ReviewManager.get_test_case_cls(ReviewManager.base_prompt),
    ],
    ids=["static", "generated"],
)
def test_revisions_raise_minimum_difficulty(
    test_case_cls: type[ReviewTestCase],
):
    """A nonempty revisions list should require difficulty one."""
    unchanged = test_case_cls.model_validate(
        {
            "query": {"subtitles": [{"index": 1, "text": "original"}]},
            "answer": {"revisions": []},
        }
    )
    changed = test_case_cls.model_validate(
        {
            "query": {"subtitles": [{"index": 1, "text": "original"}]},
            "answer": {
                "revisions": [{"index": 1, "text": "corrected", "note": "typo"}]
            },
        }
    )

    assert unchanged.difficulty == 0
    assert changed.difficulty == 1


def test_generated_test_case_uses_prompt_validation_errors():
    """Generated test-case validators should use their localized prompt."""
    test_case_cls = ReviewManager.get_test_case_cls(_LOCALIZED_PROMPT)

    with raises(ValidationError, match="修訂序號 2 未對應字幕"):
        test_case_cls.model_validate(
            {
                "query": {"subtitles": [{"index": 1, "text": "原文"}]},
                "answer": {
                    "revisions": [{"index": 2, "text": "修改", "note": "修正錯字"}]
                },
            }
        )
