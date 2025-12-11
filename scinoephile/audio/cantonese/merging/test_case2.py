#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 merging test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import TestCase2
from scinoephile.core.models import get_cls_name
from scinoephile.core.text import (
    remove_non_punc_and_whitespace,
    remove_punc_and_whitespace,
)

from .answer2 import MergingAnswer2
from .prompt2 import MergingPrompt2
from .query2 import MergingQuery2

__all__ = ["MergingTestCase2"]


class MergingTestCase2(TestCase2[MergingQuery2, MergingAnswer2], ABC):
    """Abstract base class for 粤文 merging test cases."""

    answer_cls: ClassVar[type[MergingAnswer2]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[MergingQuery2]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[MergingPrompt2]]
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

        zhongwen = getattr(self.query, "zhongwen", None)
        yuewen_merged = getattr(self.answer, "yuewen_merged", None)
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

        yuewen_to_merge = getattr(self.query, "yuewen_to_merge", None)
        yuewen_merged = getattr(self.answer, "yuewen_merged", None)

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
        cls, prompt_cls: type[MergingPrompt2] = MergingPrompt2
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_cls_name(cls.__name__, prompt_cls.__name__)
        query_cls = MergingQuery2.get_query_cls(prompt_cls)
        answer_cls = MergingAnswer2.get_answer_cls(prompt_cls)
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
