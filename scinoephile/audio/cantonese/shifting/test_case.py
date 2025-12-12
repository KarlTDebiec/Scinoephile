#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription shifting test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model, model_validator

from scinoephile.core.llms import TestCase2
from scinoephile.core.models import get_model_name

from .answer import ShiftingAnswer
from .prompt import ShiftingPrompt
from .query import ShiftingQuery

__all__ = ["ShiftingTestCase"]


class ShiftingTestCase(TestCase2, ABC):
    """Abstract base class for 粤文 transcription shifting test cases."""

    answer_cls: ClassVar[type[ShiftingAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[ShiftingQuery]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[ShiftingPrompt]]
    """Text strings to be used for corresponding with LLM."""

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
        if self.answer is None:
            return min_difficulty

        yuewen_1_shifted = getattr(self.answer, "yuewen_1_shifted", None)
        yuewen_2_shifted = getattr(self.answer, "yuewen_2_shifted", None)
        if yuewen_1_shifted != "" or yuewen_2_shifted != "":
            min_difficulty = max(min_difficulty, 1)

        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        if self.answer is None:
            return self

        yuewen_1 = getattr(self.query, "yuewen_1", None)
        yuewen_2 = getattr(self.query, "yuewen_2", None)
        yuewen_1_shifted = getattr(self.answer, "yuewen_1_shifted", None)
        yuewen_2_shifted = getattr(self.answer, "yuewen_2_shifted", None)
        if yuewen_1 == yuewen_1_shifted and yuewen_2 == yuewen_2_shifted:
            raise ValueError(self.prompt_cls.yuewen_1_yuewen_2_unchanged_error)
        if yuewen_1_shifted != "" or yuewen_2_shifted != "":
            expected = yuewen_1 + yuewen_2
            received = yuewen_1_shifted + yuewen_2_shifted
            if expected != received:
                raise ValueError(
                    self.prompt_cls.yuewen_characters_changed_error.format(
                        expected=expected, received=received
                    )
                )
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        prompt_cls: type[ShiftingPrompt] = ShiftingPrompt,
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        query_cls = ShiftingQuery.get_query_cls(prompt_cls)
        answer_cls = ShiftingAnswer.get_answer_cls(prompt_cls)
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        return model
