#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for OCR fusion dual track / single subtitle LLM classes."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.llms.base import TestCase
from scinoephile.llms.dual_single import DualSingleManager

from .prompt import OcrFusionPrompt

__all__ = ["OcrFusionManager"]


class OcrFusionManager(DualSingleManager):
    """Factories for OCR fusion dual track / single subtitle LLM classes."""

    prompt_cls: ClassVar[type[OcrFusionPrompt]] = OcrFusionPrompt
    """Default prompt class."""

    @staticmethod
    def get_auto_verified(model: TestCase) -> bool:
        """Whether this test case should automatically be verified.

        Arguments:
            model: test case to inspect
        Returns:
            whether the test case should be auto-verified
        """
        if model.answer is None:
            return False

        if model.get_min_difficulty() > 1:
            return False

        source_one = getattr(model.query, model.prompt_cls.src_1, None)
        source_two = getattr(model.query, model.prompt_cls.src_2, None)
        output_text = getattr(model.answer, model.prompt_cls.output, None)
        if (
            source_one is not None
            and source_two is not None
            and output_text is not None
        ):
            if source_one == output_text and "\n" not in source_one:
                return True
            if source_two == output_text and "\n" not in source_two:
                return True
        return DualSingleManager.get_auto_verified(model)

    @staticmethod
    def get_min_difficulty(model: TestCase) -> int:
        """Get minimum difficulty based on the test case properties.

        Arguments:
            model: test case to inspect
        Returns:
            minimum difficulty
        """
        min_difficulty = DualSingleManager.get_min_difficulty(model)
        min_difficulty = max(min_difficulty, 1)
        if model.answer is None:
            return min_difficulty

        if output_text := getattr(model.answer, model.prompt_cls.output):
            if any(char in output_text for char in ("-", '"', "“", "”")):
                min_difficulty = max(min_difficulty, 2)
        return min_difficulty
