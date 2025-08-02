#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 merging; may also be used for few-shot prompt."""

from __future__ import annotations

from functools import cached_property

from pydantic import model_validator

from scinoephile.audio.cantonese.merging.merge_answer import MergeAnswer
from scinoephile.audio.cantonese.merging.merge_query import MergeQuery
from scinoephile.core.abcs import TestCase
from scinoephile.core.text import (
    remove_non_punc_and_whitespace,
    remove_punc_and_whitespace,
)


class MergeTestCase(MergeQuery, MergeAnswer, TestCase[MergeQuery, MergeAnswer]):
    """Test case for 粤文 merging; may also be used for few-shot prompt."""

    @cached_property
    def noop(self) -> bool:
        """Return whether this test case is a no-op."""
        return (
            len(self.yuewen_to_merge) == 1
            and self.yuewen_to_merge[0] == self.yuewen_merged
        )

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty.

        If the test case asks for the 粤文 text to have punctuation or spacing added,
        difficulty is at least 1. If the test case asks for the 粤文 text to have
        additional punctuation or spacing not present in the 中文 text added,
        difficulty is at least 2.

        Returns:
            Minimum difficulty level based on the test case properties
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
    def validate_test_case(self) -> MergeTestCase:
        """Ensure query and answer are consistent with one another."""
        expected = "".join(remove_punc_and_whitespace(s) for s in self.yuewen_to_merge)
        received = remove_punc_and_whitespace(self.yuewen_merged)
        if expected != received:
            raise ValueError(
                "Answer's 粤文 text stripped of punctuation and whitespace does not "
                "match query's 粤文 text concatendated and stripped of punctuation of "
                "whitespace:\n"
                f"Expected: {expected}\n"
                f"Received: {received}"
            )
        return self
