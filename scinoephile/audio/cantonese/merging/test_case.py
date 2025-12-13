#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 merging test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model, model_validator

from scinoephile.core.llms import TestCase
from scinoephile.core.models import get_model_name
from scinoephile.core.text import (
    remove_non_punc_and_whitespace,
    remove_punc_and_whitespace,
)

from .answer import MergingAnswer
from .prompt import MergingPrompt
from .query import MergingQuery

__all__ = ["MergingTestCase"]


class MergingTestCase(TestCase, ABC):
    """Abstract base class for 粤文 merging test cases."""

    answer_cls: ClassVar[type[MergingAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[MergingQuery]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[MergingPrompt]]
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

        zhongwen = getattr(self.query, self.prompt_cls.zhongwen_field, None)
        yuewen_merged = getattr(self.answer, self.prompt_cls.yuewen_merged_field, None)
        if remove_non_punc_and_whitespace(yuewen_merged):
            min_difficulty = max(min_difficulty, 1)
        if remove_non_punc_and_whitespace(zhongwen) != remove_non_punc_and_whitespace(
            yuewen_merged
        ):
            min_difficulty = max(min_difficulty, 2)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        if self.answer is None:
            return self

        yuewen_to_merge = getattr(
            self.query, self.prompt_cls.yuewen_to_merge_field, None
        )
        yuewen_merged = getattr(self.answer, self.prompt_cls.yuewen_merged_field, None)

        expected = "".join(remove_punc_and_whitespace(s) for s in yuewen_to_merge)
        received = remove_punc_and_whitespace(yuewen_merged)
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
        cls, prompt_cls: type[MergingPrompt] = MergingPrompt
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        query_cls = MergingQuery.get_query_cls(prompt_cls)
        answer_cls = MergingAnswer.get_answer_cls(prompt_cls)
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        return model
