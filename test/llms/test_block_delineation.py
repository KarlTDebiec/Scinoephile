#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for block-level delineation LLM models."""

from __future__ import annotations

from pydantic import ValidationError
from pytest import raises

from scinoephile.llms.block_delineation import (
    BlockDelineationManager,
    BlockDelineationPrompt,
    BlockDelineationTestCase,
)

_LOCALIZED_PROMPT = BlockDelineationPrompt(
    guides="cankao",
    targets="chushi",
    first_owned_index="fuze_kaishi",
    last_owned_index="fuze_jieshu",
    changes="xiugai",
    index="xuhao",
    text="wenben",
)
"""Block-delineation prompt with localized correspondence field names."""


def test_prompt_aliases_apply_to_lists_and_nested_subtitles():
    """Generated models should use aliases on collections and their items."""
    test_case_cls = BlockDelineationManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "cankao": [
                    {"xuhao": 1, "wenben": "參考一"},
                    {"xuhao": 2, "wenben": "參考二"},
                ],
                "chushi": [
                    {"xuhao": 1, "wenben": "甲乙"},
                    {"xuhao": 2, "wenben": "丙"},
                ],
                "fuze_kaishi": 1,
                "fuze_jieshu": 2,
            },
            "answer": {
                "xiugai": [{"xuhao": 1, "wenben": "甲"}, {"xuhao": 2, "wenben": "乙丙"}]
            },
        }
    )

    assert test_case.query.model_dump(by_alias=True) == {
        "cankao": [{"xuhao": 1, "wenben": "參考一"}, {"xuhao": 2, "wenben": "參考二"}],
        "chushi": [{"xuhao": 1, "wenben": "甲乙"}, {"xuhao": 2, "wenben": "丙"}],
        "fuze_kaishi": 1,
        "fuze_jieshu": 2,
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump(by_alias=True) == {
        "xiugai": [{"xuhao": 1, "wenben": "甲"}, {"xuhao": 2, "wenben": "乙丙"}]
    }


def test_sparse_changes_validate_indices_and_complete_character_order():
    """Delineation should accept boundary moves but reject malformed changes."""
    query = {
        "guides": [{"index": 1, "text": "參考一"}, {"index": 2, "text": "參考二"}],
        "targets": [{"index": 1, "text": "甲乙"}, {"index": 2, "text": "丙"}],
    }
    changed = BlockDelineationTestCase.model_validate(
        {
            "query": query,
            "answer": {
                "changes": [{"index": 1, "text": "甲"}, {"index": 2, "text": "乙丙"}]
            },
        }
    )

    assert changed.difficulty == 1
    assert changed.get_no_op_answer().changes == []
    with raises(ValidationError, match="unique and in ascending order"):
        BlockDelineationTestCase.model_validate(
            {
                "query": query,
                "answer": {
                    "changes": [
                        {"index": 2, "text": "乙丙"},
                        {"index": 1, "text": "甲"},
                    ]
                },
            }
        )
    with raises(ValidationError, match=r"(?s)index 1.*U\+4E59.*Expected: 甲乙丙"):
        BlockDelineationTestCase.model_validate(
            {"query": query, "answer": {"changes": [{"index": 1, "text": "甲壞"}]}}
        )
    with raises(ValidationError, match="correspond to a query guide index"):
        BlockDelineationTestCase.model_validate(
            {"query": query, "answer": {"changes": [{"index": 3, "text": ""}]}}
        )


def test_query_requires_complete_corresponding_indexes():
    """Queries should require consecutive guide and matching target indexes."""
    with raises(ValidationError, match="consecutive, ordered, and begin at 1"):
        BlockDelineationTestCase.model_validate(
            {
                "query": {
                    "guides": [{"index": 2, "text": "參考"}],
                    "targets": [{"index": 2, "text": "目標"}],
                }
            }
        )
    with raises(ValidationError, match="correspond exactly"):
        BlockDelineationTestCase.model_validate(
            {
                "query": {
                    "guides": [
                        {"index": 1, "text": "參考一"},
                        {"index": 2, "text": "參考二"},
                    ],
                    "targets": [{"index": 1, "text": "目標"}],
                }
            }
        )
    with raises(ValidationError, match="owned indexes"):
        BlockDelineationTestCase.model_validate(
            {
                "query": {
                    "guides": [{"index": 1, "text": "參考"}],
                    "targets": [{"index": 1, "text": "目標"}],
                    "first_owned_index": 1,
                }
            }
        )
