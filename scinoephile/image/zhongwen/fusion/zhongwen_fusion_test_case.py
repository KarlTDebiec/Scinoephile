#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 中文 OCR fusion test cases."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar, Self

from pydantic import create_model

from scinoephile.core.abcs import TestCase
from scinoephile.core.models import format_field
from scinoephile.core.text import whitespace
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_answer import (
    ZhongwenFusionAnswer,
)
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_llm_text import (
    ZhongwenFusionLLMText,
)
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_query import ZhongwenFusionQuery


class ZhongwenFusionTestCase(
    ZhongwenFusionQuery,
    ZhongwenFusionAnswer,
    TestCase[ZhongwenFusionQuery, ZhongwenFusionAnswer],
    ABC,
):
    """Abstract base class for 中文 OCR fusion test cases."""

    answer_cls: ClassVar[type[ZhongwenFusionAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[ZhongwenFusionQuery]]
    """Query class for this test case."""
    text: ClassVar[type[ZhongwenFusionLLMText]]
    """Text strings to be used for corresponding with LLM."""

    @property
    def source_str(self) -> str:
        """Get Python source string."""
        lines = [
            f"{ZhongwenFusionTestCase.__name__}.get_test_case_cls({self.text.__name__})("
        ]
        for field in self.query_fields:
            value = getattr(self, field)
            lines.append(format_field(field, value))
        for field in self.answer_fields:
            value = getattr(self, field)
            if value == "":
                continue
            lines.append(format_field(field, value))
        for field in self.test_case_fields:
            value = getattr(self, field)
            lines.append(format_field(field, value))
        lines.append(")")
        return "\n".join(lines)

    def get_auto_verified(self) -> bool:
        """Whether this test case should automatically be verified."""
        auto_verified = super().get_auto_verified()
        if any(ch in self.ronghe for ch in whitespace.values()):
            return False
        if self.get_min_difficulty() > 1:
            return False
        if self.lens == self.ronghe and "\n" not in self.lens:
            return True
        if self.paddle == self.ronghe and "\n" not in self.paddle:
            return True
        return False

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
        if any(ch in self.ronghe for ch in whitespace.values()):
            min_difficulty = max(min_difficulty, 2)
        return min_difficulty

    @classmethod
    def get_test_case_cls(
        cls, text: type[ZhongwenFusionLLMText] = ZhongwenFusionLLMText
    ) -> type[Self]:
        """Get concrete class for 中文 OCR fusion test case.

        Arguments:
            text: LLMText providing descriptions and messages
        Returns:
            ZhongwenFusionTestCase type with appropriate fields and descriptions
        """
        query_cls = ZhongwenFusionQuery.get_query_cls(text)
        answer_cls = ZhongwenFusionAnswer.get_answer_cls(text)
        model = create_model(
            f"{cls.__name__}_{text.__name__}",
            __base__=(query_cls, answer_cls, cls),
            __module__=cls.__module__,
            query_cls=(ClassVar[type[ZhongwenFusionQuery]], query_cls),
            answer_cls=(ClassVar[type[ZhongwenFusionAnswer]], answer_cls),
            text=(ClassVar[type[ZhongwenFusionLLMText]], text),
        )

        return model
