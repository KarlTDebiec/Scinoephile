#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 proofing; may also be used for few-shot prompt."""

from __future__ import annotations

from functools import cached_property

from pydantic import model_validator

from scinoephile.audio.cantonese.proofing.proof_answer import ProofAnswer
from scinoephile.audio.cantonese.proofing.proof_query import ProofQuery
from scinoephile.core import ScinoephileError
from scinoephile.core.abcs import TestCase


class ProofTestCase(ProofQuery, ProofAnswer, TestCase[ProofQuery, ProofAnswer]):
    """Test case for 粤文 proofing; may also be used for few-shot prompt."""

    @cached_property
    def noop(self) -> bool:
        """Return whether this test case is a no-op."""
        return self.yuewen == self.yuewen_proofread

    @model_validator(mode="after")
    def validate_test_case(self) -> ProofTestCase:
        """Ensure query and answer are consistent with one another."""
        if self.yuewen != self.yuewen_proofread and not self.note:
            raise ScinoephileError(
                "Answer's proofed 粤文 text is modified relative to query's 粤文 "
                "text, not no note is provided"
            )
        return self
