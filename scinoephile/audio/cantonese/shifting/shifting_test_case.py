#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription shifting test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model, model_validator

from scinoephile.audio.cantonese.shifting.shifting_answer import ShiftingAnswer
from scinoephile.audio.cantonese.shifting.shifting_llm_text import ShiftingLLMText
from scinoephile.audio.cantonese.shifting.shifting_query import ShiftingQuery
from scinoephile.core.abcs import TestCase


class ShiftingTestCase(
    ShiftingQuery, ShiftingAnswer, TestCase[ShiftingQuery, ShiftingAnswer], ABC
):
    """Abstract base class for 粤文 transcription shifting test cases."""

    answer_cls: ClassVar[type[ShiftingAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[ShiftingQuery]]
    """Query class for this test case."""
    text: ClassVar[type[ShiftingLLMText]]
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
        if self.yuewen_1_shifted != "" or self.yuewen_2_shifted != "":
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        if (
            self.yuewen_1 == self.yuewen_1_shifted
            and self.yuewen_2 == self.yuewen_2_shifted
        ):
            raise ValueError(self.text.yuewen_1_yuewen_2_unchanged_error)
        if self.yuewen_1_shifted != "" or self.yuewen_2_shifted != "":
            expected = self.yuewen_1 + self.yuewen_2
            received = self.yuewen_1_shifted + self.yuewen_2_shifted
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
        cls, text: type[ShiftingLLMText] = ShiftingLLMText
    ) -> type[Self]:
        """Get concrete test case class with provided text.

        Arguments:
            text: LLMText providing descriptions and messages
        Returns:
            TestCase type with appropriate fields and text
        """
        query_cls = ShiftingQuery.get_query_cls(text)
        answer_cls = ShiftingAnswer.get_answer_cls(text)
        return create_model(
            f"{cls.__name__}_{text.__name__}",
            __base__=(query_cls, answer_cls, cls),
            __module__=cls.__module__,
            query_cls=(ClassVar[type[ShiftingQuery]], query_cls),
            answer_cls=(ClassVar[type[ShiftingAnswer]], answer_cls),
            text=(ClassVar[type[ShiftingLLMText]], text),
        )
