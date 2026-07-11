#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for legacy manager-defined test-case callbacks."""

from __future__ import annotations

from pydantic import ValidationError
from pytest import raises

from scinoephile.llms.delineation import DelineationManager


def test_delineation_retains_validation_and_minimum_difficulty():
    """Delineation should retain shifted-boundary validation and scoring."""
    test_case_cls = DelineationManager.get_test_case_cls(DelineationManager.base_prompt)
    query = {
        "src_1_sub_1": "source one first",
        "src_1_sub_2": "source one second",
        "src_2_sub_1": "ab",
        "src_2_sub_2": "cd",
    }
    shifted = test_case_cls.model_validate(
        {
            "query": query,
            "answer": {
                "src_2_sub_1_shifted": "abc",
                "src_2_sub_2_shifted": "d",
            },
        }
    )

    assert shifted.difficulty == 1
    with raises(ValidationError, match="are equal to query"):
        test_case_cls.model_validate(
            {
                "query": query,
                "answer": {
                    "src_2_sub_1_shifted": "ab",
                    "src_2_sub_2_shifted": "cd",
                },
            }
        )
