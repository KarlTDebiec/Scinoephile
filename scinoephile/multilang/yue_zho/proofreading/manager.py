#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for 粤文 vs. 中文 proofreading LLM classes."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.llms.dual_single import DualSingleManager

from .prompts import YueZhoHansProofreadingPrompt

from scinoephile.core.llms import Answer, TestCase

__all__ = ["YueZhoProofreadingManager"]


class YueZhoProofreadingManager(DualSingleManager):
    """Factories for 粤文 vs. 中文 proofreading LLM classes."""

    prompt_cls: ClassVar[type[YueZhoHansProofreadingPrompt]] = (
        YueZhoHansProofreadingPrompt
    )
    """Default prompt class."""

    @staticmethod
    def validate_answer(model: Answer) -> Answer:
        """Ensure answer is internally valid.

        Arguments:
            model: answer to validate
        Returns:
            validated answer
        """
        prompt_cls: type[YueZhoHansProofreadingPrompt] = getattr(model, "prompt_cls")
        output = getattr(model, prompt_cls.output, None)
        note = getattr(model, prompt_cls.note, None)
        if not output and not note:
            raise ValueError(prompt_cls.output_missing_note_missing_err)
        return model

    @staticmethod
    def validate_test_case(model: TestCase) -> TestCase:
        """Ensure query and answer together are valid.

        Arguments:
            model: test case to validate
        Returns:
            validated test case
        """
        prompt_cls: type[YueZhoHansProofreadingPrompt] = getattr(model, "prompt_cls")
        if model.answer is None:
            return model

        yuewen = getattr(model.query, prompt_cls.src_1, None)
        yuewen_proofread = getattr(model.answer, prompt_cls.output, None)
        if yuewen != yuewen_proofread:
            model.difficulty = max(model.difficulty, 1)
        return model
