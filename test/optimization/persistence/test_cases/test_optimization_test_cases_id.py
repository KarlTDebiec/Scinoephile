#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for test case identity helpers."""

from __future__ import annotations

from scinoephile.core.optimization import get_test_case_id
from scinoephile.llms.mono_block.manager import MonoBlockManager
from scinoephile.llms.mono_block.prompt import MonoBlockPrompt


def test_get_test_case_id_stable_for_same_payload():
    """Computing an ID twice for identical data should match."""
    test_case_cls = MonoBlockManager.get_test_case_cls(
        size=1, prompt_cls=MonoBlockPrompt
    )
    tc1 = test_case_cls.model_validate(
        {
            "query": {"input_1": "a"},
            "answer": {"output_1": "b", "note_1": "changed"},
        }
    )
    tc2 = test_case_cls.model_validate(
        {
            "query": {"input_1": "a"},
            "answer": {"output_1": "b", "note_1": "changed"},
        }
    )
    assert tc1.answer is not None
    assert tc2.answer is not None
    assert get_test_case_id(tc1.query, tc1.answer) == get_test_case_id(
        tc2.query, tc2.answer
    )


def test_get_test_case_id_changes_with_answer():
    """Changing answer content should change computed ID."""
    test_case_cls = MonoBlockManager.get_test_case_cls(
        size=1, prompt_cls=MonoBlockPrompt
    )
    tc1 = test_case_cls.model_validate(
        {
            "query": {"input_1": "a"},
            "answer": {"output_1": "b", "note_1": "changed"},
        }
    )
    tc2 = test_case_cls.model_validate(
        {
            "query": {"input_1": "a"},
            "answer": {"output_1": "c", "note_1": "changed"},
        }
    )
    assert tc1.answer is not None
    assert tc2.answer is not None
    assert get_test_case_id(tc1.query, tc1.answer) != get_test_case_id(
        tc2.query, tc2.answer
    )
