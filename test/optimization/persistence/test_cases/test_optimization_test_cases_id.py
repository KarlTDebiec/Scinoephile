#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for test case identity helpers."""

from __future__ import annotations

from pydantic import JsonValue

from scinoephile.llms.review import ReviewManager
from scinoephile.llms.translation import TranslationManager
from scinoephile.optimization.persistence.test_cases.id import get_test_case_id


def _get_translation_answer(text: str) -> dict[str, JsonValue]:
    """Get a canonical translation answer payload."""
    return {"outputs": [{"index": 1, "text": text}]}


def _get_translation_query(text: str) -> dict[str, JsonValue]:
    """Get a canonical translation query payload."""
    return {"subtitles": [{"index": 1, "text": text}]}


def test_get_test_case_id_stable_for_same_payload():
    """Computing an ID twice for identical normalized data should match."""
    query = _get_translation_query("a")
    answer = _get_translation_answer("b")

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
    query = _get_translation_query("a")

    assert get_test_case_id(
        query,
        _get_translation_answer("b"),
        TranslationManager,
    ) != get_test_case_id(
        query,
        _get_translation_answer("c"),
        TranslationManager,
    )


def test_get_test_case_id_changes_with_operation():
    """Catalog scope should contribute to the content-addressed ID."""
    query = _get_translation_query("a")
    answer = _get_translation_answer("b")

    assert get_test_case_id(
        query,
        answer,
        TranslationManager,
    ) != get_test_case_id(
        query,
        answer,
        ReviewManager,
    )
