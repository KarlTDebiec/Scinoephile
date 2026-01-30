#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for 粤文/中文 transcription merging LLM classes."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import (
    remove_non_punc_and_whitespace,
    remove_punc_and_whitespace,
)
from scinoephile.llms.base import TestCase
from scinoephile.llms.dual_multi_single import DualMultiSingleManager

from .prompt import YueZhoHansMergingPrompt

__all__ = ["YueZhoMergingManager"]


class YueZhoMergingManager(DualMultiSingleManager):
    """Factories for 粤文/中文 transcription merging LLM classes."""

    prompt_cls: ClassVar[type[YueZhoHansMergingPrompt]] = YueZhoHansMergingPrompt
    """Default prompt class."""

    @staticmethod
    def get_min_difficulty(model: TestCase) -> int:
        """Get minimum difficulty based on the test case properties.

        Arguments:
            model: test case to inspect
        Returns:
            minimum difficulty
        """
        min_difficulty = DualMultiSingleManager.get_min_difficulty(model)
        if model.answer is None:
            return min_difficulty

        zhongwen = getattr(model.query, model.prompt_cls.src_2, None) or ""
        yuewen_merged = getattr(model.answer, model.prompt_cls.output, None) or ""
        if remove_non_punc_and_whitespace(yuewen_merged):
            min_difficulty = max(min_difficulty, 1)
        if remove_non_punc_and_whitespace(zhongwen) != remove_non_punc_and_whitespace(
            yuewen_merged
        ):
            min_difficulty = max(min_difficulty, 2)
        return min_difficulty

    @staticmethod
    def validate_test_case(model: TestCase) -> TestCase:
        """Ensure query and answer together are valid.

        Arguments:
            model: test case to validate
        Returns:
            validated test case
        """
        if model.answer is None:
            return model

        yuewen_to_merge = getattr(model.query, model.prompt_cls.src_1, None) or []
        yuewen_merged = getattr(model.answer, model.prompt_cls.output, None) or ""

        expected = "".join(remove_punc_and_whitespace(s) for s in yuewen_to_merge)
        received = remove_punc_and_whitespace(yuewen_merged)
        if expected != received:
            raise ValueError(
                model.prompt_cls.yuewen_chars_changed_err(expected, received)
            )
        return model
