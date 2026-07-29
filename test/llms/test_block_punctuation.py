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
    guides="cankao", targets="daibiao", changes="xiugai", index="xuhao", text="wenben"
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
            },
            "answer": {"xiugai": [{"xuhao": 1, "wenben": "你好！"}]},
        }
    )

    assert test_case.query.model_dump(by_alias=True) == {
        "cankao": [{"xuhao": 1, "wenben": "參考"}],
        "daibiao": [{"xuhao": 1, "wenben": "你好"}],
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
    with raises(ValidationError, match="index 1"):
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
    with raises(ValidationError, match="correspond to a query guide index"):
        BlockPunctuationTestCase.model_validate(
            {"query": query, "answer": {"changes": [{"index": 3, "text": "！"}]}}
        )
