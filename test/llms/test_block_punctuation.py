#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for block-level punctuation LLM models."""

from __future__ import annotations

from pydantic import ValidationError
from pytest import raises

from scinoephile.llms.block_punctuation import (
    BlockPunctuationManager,
    BlockPunctuationPrompt,
    BlockPunctuationTestCase,
)

_LOCALIZED_PROMPT = BlockPunctuationPrompt(
    guides="cankao",
    targets="daibiao",
    first_owned_index="fuze_kaishi",
    last_owned_index="fuze_jieshu",
    changes="xiugai",
    index="xuhao",
    text="wenben",
)
"""Block-punctuation prompt with localized correspondence field names."""


def test_prompt_aliases_apply_to_lists_and_nested_subtitles():
    """Generated models should use aliases on collections and their items."""
    test_case_cls = BlockPunctuationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "cankao": [{"xuhao": 1, "wenben": "參考"}],
                "daibiao": [{"xuhao": 1, "wenben": "你好"}],
                "fuze_kaishi": 1,
                "fuze_jieshu": 1,
            },
            "answer": {"xiugai": [{"xuhao": 1, "wenben": "你好！"}]},
        }
    )

    assert test_case.query.model_dump(by_alias=True) == {
        "cankao": [{"xuhao": 1, "wenben": "參考"}],
        "daibiao": [{"xuhao": 1, "wenben": "你好"}],
        "fuze_kaishi": 1,
        "fuze_jieshu": 1,
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump(by_alias=True) == {
        "xiugai": [{"xuhao": 1, "wenben": "你好！"}]
    }


def test_sparse_changes_may_only_adjust_punctuation_within_each_index():
    """Punctuation should preserve non-punctuation text at every changed index."""
    query = {
        "guides": [{"index": 1, "text": "參考一"}, {"index": 2, "text": "參考二"}],
        "targets": [{"index": 1, "text": "你好"}, {"index": 2, "text": "再見"}],
    }
    changed = BlockPunctuationTestCase.model_validate(
        {
            "query": query,
            "answer": {
                "changes": [
                    {"index": 1, "text": "你好！"},
                    {"index": 2, "text": "再見。"},
                ]
            },
        }
    )

    assert changed.difficulty == 1
    assert changed.get_no_op_answer().changes == []
    with raises(ValidationError, match=r"(?s)index 1.*U\+518D"):
        BlockPunctuationTestCase.model_validate(
            {
                "query": query,
                "answer": {
                    "changes": [
                        {"index": 1, "text": "你好再"},
                        {"index": 2, "text": "見"},
                    ]
                },
            }
        )
    with raises(ValidationError, match="unique and in ascending order"):
        BlockPunctuationTestCase.model_validate(
            {
                "query": query,
                "answer": {
                    "changes": [
                        {"index": 2, "text": "再見。"},
                        {"index": 1, "text": "你好！"},
                    ]
                },
            }
        )
    unknown = BlockPunctuationTestCase.model_validate(
        {"query": query, "answer": {"changes": [{"index": 3, "text": "！"}]}}
    )
    assert unknown.answer is not None
    assert unknown.answer.changes == []


def test_sparse_changes_restore_source_characters_with_matching_length():
    """Punctuation layout should survive harmless script normalization."""
    test_case = BlockPunctuationTestCase.model_validate(
        {
            "query": {
                "guides": [{"index": 1, "text": "我們成親"}],
                "targets": [{"index": 1, "text": "我哋成亲"}],
            },
            "answer": {"changes": [{"index": 1, "text": "我哋成親！"}]},
        }
    )

    assert test_case.answer is not None
    assert test_case.answer.changes[0].text == "我哋成亲！"


def test_sparse_changes_may_only_modify_owned_window_indexes():
    """Punctuation should ignore sparse changes to context-only indexes."""
    query = {
        "guides": [
            {"index": 1, "text": "前文"},
            {"index": 2, "text": "負責"},
            {"index": 3, "text": "後文"},
        ],
        "targets": [
            {"index": 1, "text": "甲"},
            {"index": 2, "text": "乙"},
            {"index": 3, "text": "丙"},
        ],
        "first_owned_index": 2,
        "last_owned_index": 2,
    }

    test_case = BlockPunctuationTestCase.model_validate(
        {"query": query, "answer": {"changes": [{"index": 1, "text": "甲！"}]}}
    )

    assert test_case.answer is not None
    assert test_case.answer.changes == []


def test_output_quality_validation_rejects_deterministic_layout_defects():
    """Configured prompts should reject obvious final punctuation defects."""
    prompt = BlockPunctuationPrompt(validate_output_quality=True)
    test_case_cls = BlockPunctuationManager.get_test_case_cls(prompt)
    query = {
        "guides": [
            {"index": 1, "text": "參考一"},
            {"index": 2, "text": "參考二"},
            {"index": 3, "text": "參考三"},
        ],
        "targets": [
            {"index": 1, "text": "甲"},
            {"index": 2, "text": "，乙!"},
            {"index": 3, "text": "。"},
        ],
        "first_owned_index": 2,
        "last_owned_index": 3,
    }

    with raises(
        ValidationError,
        match=r"(?s)indexes 2 begin.*indexes 3 contain.*indexes 2 contain Hanzi",
    ):
        test_case_cls.model_validate({"query": query, "answer": {"changes": []}})

    corrected = test_case_cls.model_validate(
        {
            "query": query,
            "answer": {
                "changes": [{"index": 2, "text": "乙！"}, {"index": 3, "text": ""}]
            },
        }
    )
    assert corrected.answer is not None
    assert [change.text for change in corrected.answer.changes] == ["乙！", ""]


def test_output_quality_validation_can_be_skipped_for_persisted_or_no_op_answers():
    """Loading and explicit no-op behavior should preserve old answer data."""
    prompt = BlockPunctuationPrompt(validate_output_quality=True)
    test_case_cls = BlockPunctuationManager.get_test_case_cls(prompt)

    test_case = test_case_cls.model_validate(
        {
            "query": {
                "guides": [{"index": 1, "text": "參考"}],
                "targets": [{"index": 1, "text": "，目標!"}],
            },
            "answer": {"changes": []},
        },
        context={"skip_output_quality_validation": True},
    )

    assert test_case.answer is not None
    assert test_case.answer.changes == []
