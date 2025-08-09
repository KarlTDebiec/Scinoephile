#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 shifting; may also be used for few-shot prompt."""

from __future__ import annotations

from functools import cached_property

from pydantic import model_validator

from scinoephile.audio.cantonese.shifting.shift_answer import ShiftAnswer
from scinoephile.audio.cantonese.shifting.shift_query import ShiftQuery
from scinoephile.core.abcs import TestCase


class ShiftTestCase(ShiftQuery, ShiftAnswer, TestCase[ShiftQuery, ShiftAnswer]):
    """Test case for 粤文 shifting; may also be used for few-shot prompt."""

    @cached_property
    def noop(self) -> bool:
        """Return whether this test case is a no-op."""
        return (
            self.yuewen_1 == self.yuewen_1_shifted
            and self.yuewen_2 == self.yuewen_2_shifted
        )

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty.

        If the test case asks for 粤文 text to be shifted, difficulty is at least 1.

        Returns:
            Minimum difficulty level based on the test case properties
        """
        min_difficulty = super().get_min_difficulty()
        if not self.noop:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> ShiftTestCase:
        """Ensure query and answer are consistent with one another."""
        expected = self.yuewen_1 + self.yuewen_2
        received = self.yuewen_1_shifted + self.yuewen_2_shifted
        if expected != received:
            raise ValueError(
                "Answer's concatenated shifted 粤文 subtitle 1 and shifted 粤文 "
                "subtitle 2 does not match query's concatenated 粤文 subtitle 1 and "
                "粤文 subtitle 2:\n"
                f"Expected: {expected}\n"
                f"Received: {received}"
            )
        return self
