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
    AdvisoryBlockDelineationManager,
    AdvisoryBlockDelineationPrompt,
    BlockDelineationManager,
    BlockDelineationProcessor,
    BlockDelineationPrompt,
    BlockDelineationTestCase,
    CandidateBlockDelineationManager,
    CandidateBlockDelineationPrompt,
)

_LOCALIZED_PROMPT = BlockDelineationPrompt(
    guides="cankao",
    targets="chushi",
    first_owned_index="fuze_kaishi",
    last_owned_index="fuze_jieshu",
    boundaries="bianjie",
    changes="xiugai",
    index="xuhao",
    text="wenben",
    shift="yidong",
    original_offset="yuanben",
    minimum_shift="zuixiao",
    maximum_shift="zuida",
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
        "bianjie": [{"xuhao": 1, "yuanben": 2, "zuixiao": -2, "zuida": 1}],
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump(by_alias=True) == {
        "xiugai": [{"xuhao": 1, "yidong": -1}]
    }
    assert test_case.get_output_texts() == ["甲", "乙丙"]


def test_query_supplies_original_offsets_and_legal_shift_ranges():
    """Queries should deterministically expose every editable boundary's range."""
    query_cls = BlockDelineationManager.get_query_cls(_LOCALIZED_PROMPT)

    query = query_cls.model_validate(
        {
            "cankao": [
                {"xuhao": index, "wenben": f"參考{index}"} for index in range(1, 5)
            ],
            "chushi": [
                {"xuhao": index, "wenben": text}
                for index, text in enumerate(("甲乙", "", "丙", "丁戊"), 1)
            ],
            "fuze_kaishi": 2,
            "fuze_jieshu": 3,
        }
    )

    assert query.model_dump(by_alias=True)["bianjie"] == [
        {"xuhao": 2, "yuanben": 2, "zuixiao": -2, "zuida": 3},
        {"xuhao": 3, "yuanben": 3, "zuixiao": -3, "zuida": 2},
    ]
    with raises(ValidationError, match="exactly describe every editable boundary"):
        query_cls.model_validate(
            {
                **query.model_dump(by_alias=True),
                "bianjie": [{"xuhao": 2, "yuanben": 2, "zuixiao": -1, "zuida": 3}],
            }
        )


def test_candidate_delineation_requires_supplied_boundary_shift():
    """Candidate delineation should accept only one of each boundary's listed cuts."""
    prompt = CandidateBlockDelineationPrompt()
    test_case_cls = CandidateBlockDelineationManager.get_test_case_cls(prompt)
    query = {
        "guides": [{"index": 1, "text": "參考一"}, {"index": 2, "text": "參考二"}],
        "targets": [{"index": 1, "text": "甲乙"}, {"index": 2, "text": "丙"}],
        "first_owned_index": 1,
        "last_owned_index": 1,
        "boundaries": [
            {
                "index": 1,
                "original_offset": 2,
                "minimum_shift": -2,
                "maximum_shift": 1,
                "candidates": [
                    {
                        "shift": -1,
                        "offset": 1,
                        "left_context": "甲",
                        "right_context": "乙丙",
                        "timing_delta_ms": -100,
                        "pause_ms": 50,
                    },
                    {
                        "shift": 0,
                        "offset": 2,
                        "left_context": "甲乙",
                        "right_context": "丙",
                        "timing_delta_ms": 100,
                        "pause_ms": 0,
                    },
                ],
            }
        ],
    }

    test_case = test_case_cls.model_validate(
        {"query": query, "answer": {"changes": [{"index": 1, "shift": -1}]}}
    )

    assert test_case.get_output_texts() == ["甲", "乙丙"]
    with raises(ValidationError, match="selected from the supplied candidate"):
        test_case_cls.model_validate(
            {"query": query, "answer": {"changes": [{"index": 1, "shift": 1}]}}
        )


def test_advisory_delineation_accepts_legal_unsuggested_boundary_shift():
    """Advisory timing cuts should rank evidence without restricting answers."""
    prompt = AdvisoryBlockDelineationPrompt()
    test_case_cls = AdvisoryBlockDelineationManager.get_test_case_cls(prompt)
    query = {
        "guides": [{"index": 1, "text": "參考一"}, {"index": 2, "text": "參考二"}],
        "targets": [{"index": 1, "text": "甲乙"}, {"index": 2, "text": "丙"}],
        "first_owned_index": 1,
        "last_owned_index": 1,
        "boundaries": [
            {
                "index": 1,
                "original_offset": 2,
                "minimum_shift": -2,
                "maximum_shift": 1,
                "suggestions": [
                    {
                        "rank": 1,
                        "shift": -1,
                        "offset": 1,
                        "left_context": "甲",
                        "right_context": "乙丙",
                        "timing_delta_ms": -100,
                        "pause_ms": 50,
                    },
                    {
                        "rank": 2,
                        "shift": 0,
                        "offset": 2,
                        "left_context": "甲乙",
                        "right_context": "丙",
                        "timing_delta_ms": 100,
                        "pause_ms": 0,
                    },
                ],
            }
        ],
    }

    test_case = test_case_cls.model_validate(
        {"query": query, "answer": {"changes": [{"index": 1, "shift": 1}]}}
    )

    assert test_case.get_output_texts() == ["甲乙丙", ""]
    query_without_suggestions = {
        **query,
        "boundaries": [{**query["boundaries"][0], "suggestions": []}],
    }
    assert (
        test_case_cls.model_validate(
            {"query": query_without_suggestions, "answer": {"changes": []}}
        )
        .query.boundaries[0]
        .suggestions
        == []
    )
    with raises(ValidationError, match="consecutive ranks"):
        test_case_cls.model_validate(
            {
                "query": {
                    **query,
                    "boundaries": [
                        {
                            **query["boundaries"][0],
                            "suggestions": [
                                {**query["boundaries"][0]["suggestions"][0], "rank": 2},
                                query["boundaries"][0]["suggestions"][1],
                            ],
                        }
                    ],
                },
                "answer": {"changes": []},
            }
        )


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
    legacy_provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
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

    current_provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
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


def test_output_quality_validation_rejects_stranded_boundary_punctuation():
    """Configured delineation prompts should reject obvious boundary fragments."""
    prompt = BlockDelineationPrompt(validate_output_quality=True)
    test_case_cls = BlockDelineationManager.get_test_case_cls(prompt)
    query = {
        "guides": [
            {"index": 1, "text": "參考一"},
            {"index": 2, "text": "參考二"},
            {"index": 3, "text": "參考三"},
        ],
        "targets": [
            {"index": 1, "text": "甲「"},
            {"index": 2, "text": "，"},
            {"index": 3, "text": "乙"},
        ],
        "first_owned_index": 1,
        "last_owned_index": 2,
    }

    with raises(ValidationError, match=r"(?s)indexes 1 end.*indexes 2 contain"):
        test_case_cls.model_validate({"query": query, "answer": {"changes": []}})

    corrected = test_case_cls.model_validate(
        {"query": query, "answer": {"changes": [{"index": 1, "shift": 1}]}}
    )
    assert corrected.get_output_texts() == ["甲「，", "", "乙"]


def test_output_quality_validation_ignores_immutable_outer_edges():
    """Delineation should inspect only edges controlled by editable boundaries."""
    prompt = BlockDelineationPrompt(validate_output_quality=True)
    test_case_cls = BlockDelineationManager.get_test_case_cls(prompt)
    query = {
        "guides": [{"index": index, "text": f"參考{index}"} for index in range(1, 5)],
        "targets": [
            {"index": 1, "text": "，甲"},
            {"index": 2, "text": "乙"},
            {"index": 3, "text": "丙"},
            {"index": 4, "text": "丁「"},
        ],
        "first_owned_index": 2,
        "last_owned_index": 3,
    }

    test_case = test_case_cls.model_validate(
        {"query": query, "answer": {"changes": []}}
    )

    assert test_case.get_output_texts() == ["，甲", "乙", "丙", "丁「"]
