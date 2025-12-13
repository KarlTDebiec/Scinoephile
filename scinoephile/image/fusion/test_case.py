#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for OCR fusion test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self, cast

from pydantic import create_model

from scinoephile.core.llms import Answer, Prompt, Query, TestCase
from scinoephile.core.models import get_model_name

from .answer import FusionAnswer
from .prompt import FusionPrompt
from .query import FusionQuery

__all__ = ["FusionTestCase"]


class FusionTestCase(TestCase, ABC):
    """ABC for OCR fusion test cases."""

    answer_cls: ClassVar[type[Answer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[Query]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[Prompt]]
    """Text strings to be used for corresponding with LLM."""
    query: FusionQuery
    """Query for this test case."""
    answer: FusionAnswer | None
    """Answer to this test case."""
    prompt: bool
    """Whether to include test case in prompt examples."""
    verified: bool
    """Whether to cache verified answer."""

    def get_auto_verified(self) -> bool:
        """Whether this test case should automatically be verified."""
        if self.answer is None:
            return False

        if self.get_min_difficulty() > 1:
            return False

        prompt_cls = cast(type[FusionPrompt], self.prompt_cls)
        source_one_field = prompt_cls.source_one_field
        source_two_field = prompt_cls.source_two_field
        fused_field = prompt_cls.fused_field
        source_one = getattr(self.query, source_one_field, None)
        source_two = getattr(self.query, source_two_field, None)
        fused = getattr(self.answer, fused_field, None)
        if source_one is not None and source_two is not None and fused is not None:
            if source_one == fused and "\n" not in source_one:
                return True
            if source_two == fused and "\n" not in source_two:
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
            prompt_cls = cast(type[FusionPrompt], self.prompt_cls)
            fused = getattr(self.answer, prompt_cls.fused_field, None)
            if fused is not None:
                if "-" in fused or '"' in fused:
                    min_difficulty = max(min_difficulty, 2)
        return min_difficulty

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        prompt_cls: type[FusionPrompt],
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        query_cls = FusionQuery.get_query_cls(prompt_cls)
        answer_cls = FusionAnswer.get_answer_cls(prompt_cls)
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        return model
