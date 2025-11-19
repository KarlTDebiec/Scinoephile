#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 中文 OCR fusion; may also be used for few-shot prompt."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.abcs import TestCase
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_answer import (
    ZhongwenFusionAnswer,
)
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_query import ZhongwenFusionQuery


class ZhongwenFusionTestCase(
    ZhongwenFusionQuery,
    ZhongwenFusionAnswer,
    TestCase[ZhongwenFusionQuery, ZhongwenFusionAnswer],
):
    """Test case for 中文 OCR fusion; may also be used for few-shot prompt."""

    answer_cls: ClassVar[type[ZhongwenFusionAnswer]] = ZhongwenFusionAnswer
    """Answer class for this test case."""
    query_cls: ClassVar[type[ZhongwenFusionQuery]] = ZhongwenFusionQuery
    """Query class for this test case."""

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
        return min_difficulty
