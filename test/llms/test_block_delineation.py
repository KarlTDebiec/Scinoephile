#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for block-level delineation LLM models."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock

from pydantic import ValidationError
from pytest import raises

from scinoephile.core.llms import LLMProvider
from scinoephile.llms.block_delineation import (
    BlockDelineationManager,
    BlockDelineationProcessor,
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
    shift="yidong",
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
            "answer": {"xiugai": [{"xuhao": 1, "yidong": -1}]},
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
        "xiugai": [{"xuhao": 1, "yidong": -1}]
    }
    assert test_case.get_output_texts() == ["甲", "乙丙"]


def test_sparse_boundary_shifts_validate_indices_and_non_crossing_offsets():
    """Delineation should accept boundary shifts but reject malformed changes."""
    query = {
        "guides": [{"index": 1, "text": "參考一"}, {"index": 2, "text": "參考二"}],
        "targets": [{"index": 1, "text": "甲乙"}, {"index": 2, "text": "丙"}],
    }
    changed = BlockDelineationTestCase.model_validate(
        {"query": query, "answer": {"changes": [{"index": 1, "shift": -1}]}}
    )

    assert changed.difficulty == 1
    assert changed.get_output_texts() == ["甲", "乙丙"]
    assert changed.get_no_op_answer().changes == []
    with raises(ValidationError, match="unique and in ascending order"):
        BlockDelineationTestCase.model_validate(
            {
                "query": query,
                "answer": {
                    "changes": [{"index": 1, "shift": -1}, {"index": 1, "shift": 1}]
                },
            }
        )
    with raises(ValidationError, match="must not be zero"):
        BlockDelineationTestCase.model_validate(
            {"query": query, "answer": {"changes": [{"index": 1, "shift": 0}]}}
        )
    context_only = BlockDelineationTestCase.model_validate(
        {"query": query, "answer": {"changes": [{"index": 2, "shift": 1}]}}
    )
    assert context_only.answer is not None
    assert context_only.answer.changes == []
    with raises(ValidationError, match="between -2 and 1"):
        BlockDelineationTestCase.model_validate(
            {"query": query, "answer": {"changes": [{"index": 1, "shift": 2}]}}
        )


def test_crossed_neighbor_boundaries_report_no_valid_shift_range():
    """Delineation should distinguish crossed anchors from one bad shift."""
    with raises(ValidationError, match="offsets 3 and 1 already cross"):
        BlockDelineationTestCase.model_validate(
            {
                "query": {
                    "guides": [
                        {"index": index, "text": f"參考{index}"}
                        for index in range(1, 5)
                    ],
                    "targets": [
                        {"index": index, "text": text}
                        for index, text in enumerate("ABCD", 1)
                    ],
                },
                "answer": {
                    "changes": [
                        {"index": 1, "shift": 2},
                        {"index": 2, "shift": 2},
                        {"index": 3, "shift": -2},
                    ]
                },
            }
        )


def test_legacy_text_changes_migrate_to_boundary_shifts():
    """Persisted replacement-text answers should retain output and verification."""
    test_case = BlockDelineationTestCase.model_validate(
        {
            "query": {
                "guides": [
                    {"index": 1, "text": "參考一"},
                    {"index": 2, "text": "參考二"},
                ],
                "targets": [{"index": 1, "text": "甲乙"}, {"index": 2, "text": "丙"}],
            },
            "answer": {
                "changes": [{"index": 1, "text": "甲"}, {"index": 2, "text": "乙丙"}]
            },
            "verified": True,
        }
    )

    assert test_case.answer is not None
    assert test_case.answer.model_dump() == {"changes": [{"index": 1, "shift": -1}]}
    assert test_case.get_output_texts() == ["甲", "乙丙"]
    assert test_case.verified is True


def test_legacy_window_changes_preserve_owned_boundary_offsets():
    """Legacy context rewrites should retain every boundary owned by a window."""
    test_case = BlockDelineationTestCase.model_validate(
        {
            "query": {
                "guides": [
                    {"index": index, "text": f"參考{index}"} for index in range(1, 5)
                ],
                "targets": [
                    {"index": index, "text": text}
                    for index, text in enumerate(("A", "B", "C", "D"), 1)
                ],
                "first_owned_index": 2,
                "last_owned_index": 3,
            },
            "answer": {
                "changes": [
                    {"index": 1, "text": ""},
                    {"index": 2, "text": "AB"},
                    {"index": 3, "text": "CD"},
                    {"index": 4, "text": ""},
                ]
            },
            "verified": True,
        }
    )

    assert test_case.answer is not None
    assert test_case.answer.model_dump() == {"changes": [{"index": 3, "shift": 1}]}
    output = test_case.get_output_texts()
    assert [len("".join(output[:index])) for index in (2, 3)] == [2, 4]
    assert test_case.verified is True


def test_legacy_text_response_cache_migrates_to_boundary_shifts(tmp_path: Path):
    """A response cached under the text schema should migrate without a query.

    Arguments:
        tmp_path: temporary cache root path
    """
    legacy_prompt = BlockDelineationPrompt(
        base_system_prompt="Return replacement text.", shift=None
    )
    current_prompt = BlockDelineationPrompt(
        base_system_prompt="Return boundary shifts.",
        legacy_cache_prompts=(legacy_prompt,),
    )
    query = {
        "guides": [{"index": 1, "text": "參考一"}, {"index": 2, "text": "參考二"}],
        "targets": [{"index": 1, "text": "甲乙"}, {"index": 2, "text": "丙"}],
    }
    legacy_provider = Mock(spec=LLMProvider, cache_identity={"implementation": "test"})
    legacy_provider.chat_completion.return_value = json.dumps(
        {"changes": [{"index": 1, "text": "甲"}, {"index": 2, "text": "乙丙"}]},
        ensure_ascii=False,
    )
    legacy_processor = BlockDelineationProcessor(
        legacy_prompt, provider=legacy_provider, cache_root_path=tmp_path
    )
    legacy_processor.queryer(
        legacy_processor.test_case_cls.model_validate({"query": query})
    )

    current_provider = Mock(spec=LLMProvider, cache_identity={"implementation": "test"})
    current_processor = BlockDelineationProcessor(
        current_prompt, provider=current_provider, cache_root_path=tmp_path
    )
    result = current_processor.queryer(
        current_processor.test_case_cls.model_validate({"query": query})
    )

    assert result.answer is not None
    assert result.answer.model_dump() == {"changes": [{"index": 1, "shift": -1}]}
    assert result.get_output_texts() == ["甲", "乙丙"]
    current_provider.chat_completion.assert_not_called()


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
