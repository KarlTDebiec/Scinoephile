#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for 粤文/中文 transcription punctuating LLM classes."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.llms import TestCase
from scinoephile.core.text import (
    remove_non_punc_and_whitespace,
    remove_punc_and_whitespace,
)
from scinoephile.llms.dual_multi_single import DualMultiSingleManager

from .prompt import YueZhoHansPunctuatingPrompt

__all__ = ["YueZhoPunctuatingManager"]


class YueZhoPunctuatingManager(DualMultiSingleManager):
    """Factories for 粤文/中文 transcription punctuating LLM classes."""

    prompt_cls: ClassVar[type[YueZhoHansPunctuatingPrompt]] = (
        YueZhoHansPunctuatingPrompt
    )
    """Default prompt class."""

    @staticmethod
    def get_min_difficulty(model: TestCase) -> int:
        """Get minimum difficulty based on the test case properties.

        Arguments:
            model: test case to inspect
        Returns:
            minimum difficulty
        """
        prompt_cls: type[YueZhoHansPunctuatingPrompt] = getattr(model, "prompt_cls")
        min_difficulty = DualMultiSingleManager.get_min_difficulty(model)
        if model.answer is None:
            return min_difficulty

        zhongwen = getattr(model.query, prompt_cls.src_2, "")
        yuewen_punctuated = getattr(model.answer, prompt_cls.output, "")
        if remove_non_punc_and_whitespace(yuewen_punctuated):
            min_difficulty = max(min_difficulty, 1)
        if remove_non_punc_and_whitespace(zhongwen) != remove_non_punc_and_whitespace(
            yuewen_punctuated
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
        prompt_cls: type[YueZhoHansPunctuatingPrompt] = getattr(model, "prompt_cls")
        if model.answer is None:
            return model

        yuewen_to_punctuate = getattr(model.query, prompt_cls.src_1, None) or []
        yuewen_punctuated = getattr(model.answer, prompt_cls.output, None) or ""

        expected = "".join(remove_punc_and_whitespace(s) for s in yuewen_to_punctuate)
        received = remove_punc_and_whitespace(yuewen_punctuated)
        if expected != received:
            raise ValueError(prompt_cls.yuewen_chars_changed_err(expected, received))
        return model
