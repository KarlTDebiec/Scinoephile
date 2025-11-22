#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 shifting; may also be used for few-shot prompt."""

from __future__ import annotations

from typing import ClassVar

from pydantic import model_validator

from scinoephile.audio.cantonese.shifting.shift_answer import ShiftAnswer
from scinoephile.audio.cantonese.shifting.shift_query import ShiftQuery
from scinoephile.core.abcs import TestCase


class ShiftTestCase(ShiftQuery, ShiftAnswer, TestCase[ShiftQuery, ShiftAnswer]):
    """Test case for 粤文 shifting; may also be used for few-shot prompt."""

    answer_cls: ClassVar[type[ShiftAnswer]] = ShiftAnswer
    """Answer class for this test case."""
    query_cls: ClassVar[type[ShiftQuery]] = ShiftQuery
    """Query class for this test case."""

    @property
    def noop(self) -> bool:
        """Return whether this test case is a no-op."""
        return (
            self.yuewen_1 == self.yuewen_1_shifted
            and self.yuewen_2 == self.yuewen_2_shifted
        )

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
