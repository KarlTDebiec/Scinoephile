#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for test case identity helpers."""

from __future__ import annotations

from pydantic import JsonValue

from scinoephile.llms.review import ReviewManager
from scinoephile.llms.translation import TranslationManager
from scinoephile.optimization.persistence.test_cases.id import get_test_case_id


def test_get_test_case_id_stable_for_same_payload():
    """Computing an ID twice for identical normalized data should match."""
    query: dict[str, JsonValue] = {"input_1": "a"}
    answer: dict[str, JsonValue] = {"output_1": "b"}

    assert get_test_case_id(
        query,
        answer,
        TranslationManager,
    ) == get_test_case_id(
        query,
        answer,
        TranslationManager,
    )


def test_get_test_case_id_changes_with_answer():
    """Changing normalized answer content should change the computed ID."""
    query: dict[str, JsonValue] = {"input_1": "a"}

    assert get_test_case_id(
        query,
        {"output_1": "b"},
        TranslationManager,
    ) != get_test_case_id(
        query,
        {"output_1": "c"},
        TranslationManager,
    )


def test_get_test_case_id_changes_with_operation():
    """Catalog scope should contribute to the content-addressed ID."""
    query: dict[str, JsonValue] = {"input_1": "a"}
    answer: dict[str, JsonValue] = {"output_1": "b"}

    assert get_test_case_id(
        query,
        answer,
        TranslationManager,
    ) != get_test_case_id(
        query,
        answer,
        ReviewManager,
    )
