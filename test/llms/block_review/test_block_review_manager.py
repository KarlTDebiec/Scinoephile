#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for block review LLM model factories."""

from __future__ import annotations

import pytest

from scinoephile.llms.block_review import BlockReviewManager, BlockReviewPrompt


class _ReviewPrompt(BlockReviewPrompt):
    """Review prompt fixture for block review manager tests."""


def test_get_answer_cls_includes_outputs_and_notes():
    """Test block review answer classes include output and note fields."""
    answer_cls = BlockReviewManager.get_answer_cls(2, _ReviewPrompt)

    assert set(answer_cls.model_fields) == {
        "output_1",
        "note_1",
        "output_2",
        "note_2",
    }


def test_changed_output_requires_note():
    """Test block review changed outputs require notes."""
    test_case_cls = BlockReviewManager.get_test_case_cls(1, _ReviewPrompt)
    query = test_case_cls.query_cls.model_validate({"input_1": "Source text"})
    answer = test_case_cls.answer_cls.model_validate({"output_1": "Edited text"})

    with pytest.raises(ValueError, match="note is provided"):
        test_case_cls(query=query, answer=answer)


def test_note_requires_output():
    """Test block review notes require changed output."""
    test_case_cls = BlockReviewManager.get_test_case_cls(1, _ReviewPrompt)
    query = test_case_cls.query_cls.model_validate({"input_1": "Source text"})
    answer = test_case_cls.answer_cls.model_validate({"note_1": "Note text"})

    with pytest.raises(ValueError, match="output 1 is not provided"):
        test_case_cls(query=query, answer=answer)


def test_unmodified_output_is_cleared():
    """Test unmodified block review outputs are converted to no-change answers."""
    test_case_cls = BlockReviewManager.get_test_case_cls(1, _ReviewPrompt)
    query = test_case_cls.query_cls.model_validate({"input_1": "Source text"})
    answer = test_case_cls.answer_cls.model_validate(
        {"output_1": "Source text", "note_1": "No change"}
    )

    test_case = test_case_cls(query=query, answer=answer)

    assert test_case.answer is not None
    assert getattr(test_case.answer, "output_1") == ""
    assert getattr(test_case.answer, "note_1") == ""
