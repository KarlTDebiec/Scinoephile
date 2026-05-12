#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for dual n to m LLM model factories."""

from __future__ import annotations

import pytest

from scinoephile.core import ScinoephileError
from scinoephile.llms.dual_n_to_m import (
    DualNToMManager,
    DualNToMPrompt,
)


class _Prompt(DualNToMPrompt):
    """Prompt fixture for dual n to m tests."""


def test_get_query_cls_includes_both_sources_with_distinct_sizes():
    """Test query class includes all source-one and source-two fields."""
    query_cls = DualNToMManager.get_query_cls(2, 3, _Prompt)

    assert set(query_cls.model_fields) == {
        "source_one_1",
        "source_one_2",
        "source_two_1",
        "source_two_2",
        "source_two_3",
    }
    assert getattr(query_cls, "source_one_size") == 2
    assert getattr(query_cls, "source_two_size") == 3


def test_get_answer_cls_follows_source_one_size():
    """Test answer class includes one output field per source-one subtitle."""
    answer_cls = DualNToMManager.get_answer_cls(2, 3, _Prompt)

    assert set(answer_cls.model_fields) == {"output_1", "output_2"}
    assert getattr(answer_cls, "source_one_size") == 2
    assert getattr(answer_cls, "source_two_size") == 3


def test_get_test_case_cls_from_data_detects_both_source_sizes():
    """Test JSON test case reconstruction detects both source sizes."""
    test_case_cls = DualNToMManager.get_test_case_cls_from_data(
        {
            "query": {
                "source_one_1": "一",
                "source_one_2": "二",
                "source_two_1": "one",
                "source_two_2": "two",
                "source_two_3": "three",
            }
        },
        prompt_cls=_Prompt,
    )

    assert getattr(test_case_cls, "source_one_size") == 2
    assert getattr(test_case_cls, "source_two_size") == 3


def test_get_query_cls_rejects_empty_source_one():
    """Test source one must contain at least one subtitle."""
    with pytest.raises(ScinoephileError):
        DualNToMManager.get_query_cls(0, 1, _Prompt)


def test_get_query_cls_rejects_negative_source_two():
    """Test source two size may not be negative."""
    with pytest.raises(ScinoephileError):
        DualNToMManager.get_query_cls(1, -1, _Prompt)
