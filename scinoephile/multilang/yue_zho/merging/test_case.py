#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for 粤文/中文 transcription merging test cases."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar, Self

from pydantic import model_validator

from scinoephile.core.text import (
    remove_non_punc_and_whitespace,
    remove_punc_and_whitespace,
)
from scinoephile.llms.dual_multi_single import DualMultiSingleTestCase

from .answer import YueZhoMergingAnswer
from .prompt import YueZhoHansMergingPrompt
from .query import YueZhoMergingQuery

__all__ = ["YueZhoMergingTestCase"]


class YueZhoMergingTestCase(DualMultiSingleTestCase, ABC):
    """ABC for 粤文/中文 transcription merging test cases."""

    answer_cls: ClassVar[type[YueZhoMergingAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[YueZhoMergingQuery]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[YueZhoHansMergingPrompt]]
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

        zhongwen = getattr(self.query, self.prompt_cls.src_2, None)
        yuewen_merged = getattr(self.answer, self.prompt_cls.output, None)
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

        yuewen_to_merge = getattr(self.query, self.prompt_cls.src_1, None)
        yuewen_merged = getattr(self.answer, self.prompt_cls.output, None)

        expected = "".join(remove_punc_and_whitespace(s) for s in yuewen_to_merge)
        received = remove_punc_and_whitespace(yuewen_merged)
        if expected != received:
            raise ValueError(
                self.prompt_cls.yuewen_chars_changed_err(expected, received)
            )
        return self
