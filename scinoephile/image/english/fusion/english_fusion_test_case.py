#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for English OCR fusion; may also be used for few-shot prompt."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.abcs import TestCase
from scinoephile.image.english.fusion.english_fusion_answer import (
    EnglishFusionAnswer,
)
from scinoephile.image.english.fusion.english_fusion_query import EnglishFusionQuery


class EnglishFusionTestCase(
    EnglishFusionQuery,
    EnglishFusionAnswer,
    TestCase[EnglishFusionQuery, EnglishFusionAnswer],
):
    """Test case for English OCR fusion; may also be used for few-shot prompt."""

    answer_cls: ClassVar[type[EnglishFusionAnswer]] = EnglishFusionAnswer
    """Answer class for this test case."""
    query_cls: ClassVar[type[EnglishFusionQuery]] = EnglishFusionQuery
    """Query class for this test case."""

    def get_auto_verified(self) -> bool:
        """Whether this test case should automatically be verified."""
        auto_verified = super().get_auto_verified()
        if self.get_min_difficulty() > 1:
            return False
        if self.lens == self.fused and "\n" not in self.lens:
            auto_verified = True
        if self.tesseract == self.fused and "\n" not in self.tesseract:
            auto_verified = True
        return auto_verified

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
        if "-" in self.fused or '"' in self.fused:
            min_difficulty = max(min_difficulty, 2)
        return min_difficulty
