#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for mono n LLM model factories."""

from __future__ import annotations

from scinoephile.llms.mono_n import MonoNManager, MonoNPrompt


class _PlainPrompt(MonoNPrompt):
    """Plain transform prompt fixture for mono n manager tests."""


def test_get_answer_cls_includes_only_outputs():
    """Test mono n answer classes include only output fields."""
    answer_cls = MonoNManager.get_answer_cls(2, _PlainPrompt)

    assert set(answer_cls.model_fields) == {"output_1", "output_2"}


def test_answer_fields_are_required():
    """Test mono n answer fields are required."""
    answer_cls = MonoNManager.get_answer_cls(2, _PlainPrompt)

    assert answer_cls.model_fields["output_1"].is_required()
    assert answer_cls.model_fields["output_2"].is_required()


def test_test_case_allows_changed_output_without_note():
    """Test mono n test cases allow generated outputs without notes."""
    test_case_cls = MonoNManager.get_test_case_cls(1, _PlainPrompt)
    query = test_case_cls.query_cls.model_validate({"input_1": "Source text"})
    answer = test_case_cls.answer_cls.model_validate({"output_1": "Generated text"})
    test_case = test_case_cls(query=query, answer=answer)

    assert test_case.answer == answer
