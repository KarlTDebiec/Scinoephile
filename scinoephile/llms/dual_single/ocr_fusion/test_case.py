#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for OCR fusion test cases."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.llms.dual_single import DualSingleQuery, DualSingleTestCase

from .answer import OcrFusionAnswer
from .prompt import OcrFusionPrompt

__all__ = ["OcrFusionTestCase"]


class OcrFusionTestCase(DualSingleTestCase, ABC):
    """ABC for OCR fusion test cases."""

    answer_cls: ClassVar[type[OcrFusionAnswer]] = OcrFusionAnswer
    """Answer class for this test case."""
    query_cls: ClassVar[type[DualSingleQuery]] = DualSingleQuery
    """Query class for this test case."""
    prompt_cls: ClassVar[type[OcrFusionPrompt]]
    """Text for LLM correspondence."""

    def get_auto_verified(self) -> bool:
        """Whether this test case should automatically be verified."""
        if self.answer is None:
            return False

        if self.get_min_difficulty() > 1:
            return False

        source_one = getattr(self.query, self.prompt_cls.src_1, None)
        source_two = getattr(self.query, self.prompt_cls.src_2, None)
        output_text = getattr(self.answer, self.prompt_cls.output, None)
        if (
            source_one is not None
            and source_two is not None
            and output_text is not None
        ):
            if source_one == output_text and "\n" not in source_one:
                return True
            if source_two == output_text and "\n" not in source_two:
                return True
        return super().get_auto_verified()

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty based on the test case properties.

        0: No change needed
        1: Change needed
        2: Difficult change needed, worthy of inclusion in prompt or difficult test set
        3: Not considered realistic for LLM to handle correctly

        Returns:
            minimum difficulty level based on the test case properties
        """
        min_difficulty = super().get_min_difficulty()
        min_difficulty = max(min_difficulty, 1)
        if self.answer is None:
            return min_difficulty

        if output_text := getattr(self.answer, self.prompt_cls.output):
            if any(char in output_text for char in ("-", '"', "“", "”")):
                min_difficulty = max(min_difficulty, 2)
        return min_difficulty
