#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for test case identity helpers."""

from __future__ import annotations

from scinoephile.llms.review import REVIEW_OPERATION_SPEC
from scinoephile.llms.translation import TRANSLATION_OPERATION_SPEC
from scinoephile.optimization.persistence.test_cases.id import get_test_case_id


def test_get_test_case_id_stable_for_same_payload():
    """Computing an ID twice for identical normalized data should match."""
    query = {"input_1": "a"}
    answer = {"output_1": "b"}

    assert get_test_case_id(
        query,
        answer,
        TRANSLATION_OPERATION_SPEC,
    ) == get_test_case_id(
        query,
        answer,
        TRANSLATION_OPERATION_SPEC,
    )


def test_get_test_case_id_changes_with_answer():
    """Changing normalized answer content should change the computed ID."""
    query = {"input_1": "a"}

    assert get_test_case_id(
        query,
        {"output_1": "b"},
        TRANSLATION_OPERATION_SPEC,
    ) != get_test_case_id(
        query,
        {"output_1": "c"},
        TRANSLATION_OPERATION_SPEC,
    )


def test_get_test_case_id_changes_with_operation():
    """Catalog scope should contribute to the content-addressed ID."""
    query = {"input_1": "a"}
    answer = {"output_1": "b"}

    assert get_test_case_id(
        query,
        answer,
        TRANSLATION_OPERATION_SPEC,
    ) != get_test_case_id(
        query,
        answer,
        REVIEW_OPERATION_SPEC,
    )
