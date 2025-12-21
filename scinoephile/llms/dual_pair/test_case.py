#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for dual pair test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model, model_validator

from scinoephile.llms.base import TestCase
from scinoephile.llms.base.models import get_model_name

from .answer import DualPairAnswer
from .prompt import DualPairPrompt
from .query import DualPairQuery

__all__ = ["DualPairTestCase"]


class DualPairTestCase(TestCase, ABC):
    """ABC for dual pair test cases."""

    answer_cls: ClassVar[type[DualPairAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[DualPairQuery]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[DualPairPrompt]]
    """Text for LLM correspondence."""

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

        target_1_shifted = getattr(
            self.answer, self.prompt_cls.source_two_sub_one_shifted_field, None
        )
        target_2_shifted = getattr(
            self.answer, self.prompt_cls.source_two_sub_two_shifted_field, None
        )
        if target_1_shifted != "" or target_2_shifted != "":
            min_difficulty = max(min_difficulty, 1)

        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        if self.answer is None:
            return self

        target_1 = getattr(self.query, self.prompt_cls.source_two_sub_one_field, None)
        target_2 = getattr(self.query, self.prompt_cls.source_two_sub_two_field, None)
        target_1_shifted = getattr(
            self.answer, self.prompt_cls.source_two_sub_one_shifted_field, None
        )
        target_2_shifted = getattr(
            self.answer, self.prompt_cls.source_two_sub_two_shifted_field, None
        )
        if target_1 == target_1_shifted and target_2 == target_2_shifted:
            raise ValueError(self.prompt_cls.source_two_sub_one_sub_two_unchanged_error)
        if target_1_shifted != "" or target_2_shifted != "":
            expected = target_1 + target_2
            received = target_1_shifted + target_2_shifted
            if expected != received:
                raise ValueError(
                    self.prompt_cls.source_two_characters_changed_error(
                        expected, received
                    )
                )
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        prompt_cls: type[DualPairPrompt] = DualPairPrompt,
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        query_cls = DualPairQuery.get_query_cls(prompt_cls)
        answer_cls = DualPairAnswer.get_answer_cls(prompt_cls)
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        return model
