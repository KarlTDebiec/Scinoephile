#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for OCR fusion test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model

from scinoephile.llms.base.models import get_model_name
from scinoephile.llms.dual_single import DualSinglePrompt, DualSingleTestCase

from .answer import OcrFusionAnswer
from .query import OcrFusionQuery

__all__ = ["OcrFusionTestCase"]


class OcrFusionTestCase(DualSingleTestCase, ABC):
    """ABC for OCR fusion test cases."""

    answer_cls: ClassVar[type[OcrFusionAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[OcrFusionQuery]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[DualSinglePrompt]]
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

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        prompt_cls: type[DualSinglePrompt],
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        query_cls = OcrFusionQuery.get_query_cls(prompt_cls)
        answer_cls = OcrFusionAnswer.get_answer_cls(prompt_cls)
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        return model
