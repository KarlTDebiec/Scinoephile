#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 proofing; may also be used for few-shot prompt."""

from __future__ import annotations

from functools import cached_property

from pydantic import model_validator

from scinoephile.audio.cantonese.proofing.proof_answer import ProofAnswer
from scinoephile.audio.cantonese.proofing.proof_query import ProofQuery
from scinoephile.core.abcs import TestCase


class ProofTestCase(ProofQuery, ProofAnswer, TestCase[ProofQuery, ProofAnswer]):
    """Test case for 粤文 proofing; may also be used for few-shot prompt."""

    @cached_property
    def noop(self) -> bool:
        """Return whether this test case is a no-op."""
        return self.yuewen == self.yuewen_proofread

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty.

        If the test case asks for the 粤文 text to be modified, difficulty is at least
        1.

        Returns:
            Minimum difficulty level based on the test case properties
        """
        min_difficulty = super().get_min_difficulty()
        if not self.noop:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> ProofTestCase:
        """Ensure query and answer are consistent with one another."""
        if self.yuewen != self.yuewen_proofread and not self.note:
            raise ValueError(
                "Answer's proofed 粤文 text is modified relative to query's 粤文 "
                "text, but no note is provided."
            )
        return self
