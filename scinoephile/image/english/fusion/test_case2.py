#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for English OCR fusion test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core.llms import TestCase2
from scinoephile.core.models import get_cls_name

from .answer2 import EnglishFusionAnswer2
from .prompt2 import EnglishFusionPrompt2
from .query2 import EnglishFusionQuery2

__all__ = ["EnglishFusionTestCase2"]


class EnglishFusionTestCase2(TestCase2[EnglishFusionQuery2, EnglishFusionAnswer2], ABC):
    """Abstract base class for English OCR fusion test cases."""

    answer_cls: ClassVar[type[EnglishFusionAnswer2]]  # type: ignore
    """Answer class for this test case."""
    query_cls: ClassVar[type[EnglishFusionQuery2]]  # type: ignore
    """Query class for this test case."""
    prompt_cls: ClassVar[type[EnglishFusionPrompt2]]  # type: ignore
    """Text strings to be used for corresponding with LLM."""

    def get_auto_verified(self) -> bool:
        """Whether this test case should automatically be verified."""
        if self.answer is None:
            return False

        if self.get_min_difficulty() > 1:
            return False

        lens = getattr(self.query, "lens", None)
        tesseract = getattr(self.query, "tesseract", None)
        fused = getattr(self.answer, "fused", None)
        if lens is not None and tesseract is not None and fused is not None:
            if lens == fused and "\n" not in lens:
                return True
            if tesseract == fused and "\n" not in tesseract:
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
        if self.answer is not None:
            fused = getattr(self.answer, "fused", None)
            if fused is not None:
                if "-" in fused or '"' in fused:
                    min_difficulty = max(min_difficulty, 2)
        return min_difficulty

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        prompt_cls: type[EnglishFusionPrompt2] = EnglishFusionPrompt2,
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_cls_name(cls.__name__, prompt_cls.__name__)
        query_cls = EnglishFusionQuery2.get_query_cls(prompt_cls)
        answer_cls = EnglishFusionAnswer2.get_answer_cls(prompt_cls)
        fields = {
            "query": (query_cls, Field(...)),
            "answer": (answer_cls | None, Field(default=None)),
            "difficulty": (
                int,
                Field(0, description=prompt_cls.difficulty_description),
            ),
            "prompt": (
                bool,
                Field(False, description=prompt_cls.prompt_description),
            ),
            "verified": (
                bool,
                Field(False, description=prompt_cls.verified_description),
            ),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        return model
