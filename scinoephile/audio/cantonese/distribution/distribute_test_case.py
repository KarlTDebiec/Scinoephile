#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 distribution; may also be used for few-shot prompt."""

from __future__ import annotations

from pydantic import model_validator

from scinoephile.audio.cantonese.distribution.distribute_answer import DistributeAnswer
from scinoephile.audio.cantonese.distribution.distribute_query import DistributeQuery
from scinoephile.core.abcs import TestCase


class DistributeTestCase(
    DistributeQuery, DistributeAnswer, TestCase[DistributeQuery, DistributeAnswer]
):
    """Test case for 粤文 distribution; may also be used for few-shot prompt."""

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty.

        If the test case asks for the 粤文 text to be split, difficulty is at least 1.

        Returns:
            Minimum difficulty level based on the test case properties
        """
        min_difficulty = super().get_min_difficulty()
        if self.one_yuewen_to_append and self.two_yuewen_to_prepend:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> DistributeTestCase:
        """Ensure query and answer are consistent with one another."""
        expected = self.yuewen_to_distribute
        received = self.one_yuewen_to_append + self.two_yuewen_to_prepend
        if expected != received:
            raise ValueError(
                "Answer's concatenated 粤文 text to append and prepend does not match "
                "query's 粤文 text to split:\n"
                f"Expected: {self.yuewen_to_distribute}\n"
                f"Received: {received}"
            )
        return self
