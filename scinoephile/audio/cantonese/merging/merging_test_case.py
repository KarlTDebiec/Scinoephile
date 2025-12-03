#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 merging test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model, model_validator

from scinoephile.audio.cantonese.merging.merging_answer import MergingAnswer
from scinoephile.audio.cantonese.merging.merging_llm_text import MergingLLMText
from scinoephile.audio.cantonese.merging.merging_query import MergingQuery
from scinoephile.core.abcs import TestCase
from scinoephile.core.models import format_field
from scinoephile.core.text import (
    remove_non_punc_and_whitespace,
    remove_punc_and_whitespace,
)


class MergingTestCase(
    MergingQuery, MergingAnswer, TestCase[MergingQuery, MergingAnswer], ABC
):
    """Abstract base class for 粤文 merging test cases."""

    answer_cls: ClassVar[type[MergingAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[MergingQuery]]
    """Query class for this test case."""
    text: ClassVar[type[MergingLLMText]]
    """Text strings to be used for corresponding with LLM."""

    @property
    def noop(self) -> bool:
        """Return whether this test case is a no-op."""
        return (
            len(self.yuewen_to_merge) == 1
            and self.yuewen_to_merge[0] == self.yuewen_merged
        )

    @property
    def source_str(self) -> str:
        """Get Python source string."""
        lines = [f"{MergingTestCase.__name__}.get_test_case_cls({self.text.__name__})("]
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
        if remove_non_punc_and_whitespace(self.yuewen_merged):
            min_difficulty = max(min_difficulty, 1)
        if remove_non_punc_and_whitespace(
            self.zhongwen
        ) != remove_non_punc_and_whitespace(self.yuewen_merged):
            min_difficulty = max(min_difficulty, 2)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        expected = "".join(remove_punc_and_whitespace(s) for s in self.yuewen_to_merge)
        received = remove_punc_and_whitespace(self.yuewen_merged)
        if expected != received:
            raise ValueError(
                self.text.yuewen_characters_changed_error.format(
                    expected=expected, received=received
                )
            )
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls, text: type[MergingLLMText] = MergingLLMText
    ) -> type[Self]:
        """Get concrete test case class with provided text.

        Arguments:
            text: LLMText providing descriptions and messages
        Returns:
            TestCase type with appropriate fields and text
        """
        query_cls = MergingQuery.get_query_cls(text)
        answer_cls = MergingAnswer.get_answer_cls(text)
        return create_model(
            f"{cls.__name__}_{text.__name__}",
            __base__=(query_cls, answer_cls, cls),
            __module__=cls.__module__,
            query_cls=(ClassVar[type[MergingQuery]], query_cls),
            answer_cls=(ClassVar[type[MergingAnswer]], answer_cls),
            text=(ClassVar[type[MergingLLMText]], text),
        )
