#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 proofing; may also be used for few-shot prompt."""

from __future__ import annotations

from functools import cached_property
from typing import ClassVar

from pydantic import model_validator

from scinoephile.audio.cantonese.proofing.proof_answer import ProofAnswer
from scinoephile.audio.cantonese.proofing.proof_query import ProofQuery
from scinoephile.core.abcs import TestCase


class ProofTestCase(ProofQuery, ProofAnswer, TestCase[ProofQuery, ProofAnswer]):
    """Test case for 粤文 proofing; may also be used for few-shot prompt."""

    answer_cls: ClassVar[type[ProofAnswer]] = ProofAnswer
    """Answer class for this test case."""
    query_cls: ClassVar[type[ProofQuery]] = ProofQuery
    """Query class for this test case."""

    @cached_property
    def noop(self) -> bool:
        """Return whether this test case is a no-op."""
        return self.yuewen == self.yuewen_proofread

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
    def validate_test_case(self) -> ProofTestCase:
        """Ensure query and answer are consistent with one another."""
        if self.yuewen != self.yuewen_proofread and not self.note:
            raise ValueError(
                "Answer's proofread 粤文 of subtitle is modified relative to query's "
                "粤文 of subtitle, but no note is provided."
            )
        if self.yuewen == self.yuewen_proofread and self.note:
            raise ValueError(
                "Answer's proofread 粤文 of subtitle is identical to query's 粤文 of "
                "subtitle, but a note is provided."
            )
        return self
