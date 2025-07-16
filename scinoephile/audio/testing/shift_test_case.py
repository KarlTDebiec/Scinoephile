#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 shifting; may also be used for few-shot prompt."""

from __future__ import annotations

from pydantic import model_validator

from scinoephile.audio.models import ShiftAnswer, ShiftQuery
from scinoephile.core.abcs import TestCase
from scinoephile.core.text import remove_punc_and_whitespace


class ShiftTestCase(ShiftQuery, ShiftAnswer, TestCase[ShiftQuery, ShiftAnswer]):
    """Test case for 粤文 shifting; may also be used for few-shot prompt."""

    @model_validator(mode="after")
    def validate_shift(self) -> ShiftTestCase:
        """Ensure shifted text matches input text."""
        expected = remove_punc_and_whitespace(self.one_yuewen + self.two_yuewen)
        received = remove_punc_and_whitespace(
            self.one_yuewen_shifted + self.two_yuewen_shifted
        )
        if expected != received:
            raise ValueError(
                "Concatenated output text does not match concatenated input text:\n"
                f"Expected: {expected}\n"
                f"Received: {received}"
            )
        return self
