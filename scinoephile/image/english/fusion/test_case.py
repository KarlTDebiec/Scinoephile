#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for English OCR fusion test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model

from scinoephile.core.abcs import TestCase
from scinoephile.core.models import format_field

from .answer import EnglishFusionAnswer
from .llm_text import EnglishFusionLLMText
from .query import EnglishFusionQuery

__all__ = ["EnglishFusionTestCase"]


class EnglishFusionTestCase(
    EnglishFusionQuery,
    EnglishFusionAnswer,
    TestCase[EnglishFusionQuery, EnglishFusionAnswer],
    ABC,
):
    """Abstract base class for English OCR fusion test cases."""

    answer_cls: ClassVar[type[EnglishFusionAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[EnglishFusionQuery]]
    """Query class for this test case."""
    text: ClassVar[type[EnglishFusionLLMText]]
    """Text strings to be used for corresponding with LLM."""

    @property
    def source_str(self) -> str:
        """Get Python source string."""
        lines = [
            f"{EnglishFusionTestCase.__name__}.get_test_case_cls({self.text.__name__})("
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
        if self.get_min_difficulty() > 1:
            return False
        if self.lens == self.fused and "\n" not in self.lens:
            return True
        if self.tesseract == self.fused and "\n" not in self.tesseract:
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
        if "-" in self.fused or '"' in self.fused:
            min_difficulty = max(min_difficulty, 2)
        return min_difficulty

    @classmethod
    @cache
    def get_test_case_cls(
        cls, text: type[EnglishFusionLLMText] = EnglishFusionLLMText
    ) -> type[Self]:
        """Get concrete test case class with provided text.

        Arguments:
            text: LLMText providing descriptions and messages
        Returns:
            TestCase type with appropriate fields and text
        """
        query_cls = EnglishFusionQuery.get_query_cls(text)
        answer_cls = EnglishFusionAnswer.get_answer_cls(text)
        return create_model(
            f"{cls.__name__}_{text.__name__}",
            __base__=(query_cls, answer_cls, cls),
            __module__=cls.__module__,
            query_cls=(ClassVar[type[EnglishFusionQuery]], query_cls),
            answer_cls=(ClassVar[type[EnglishFusionAnswer]], answer_cls),
            text=(ClassVar[type[EnglishFusionLLMText]], text),
        )
