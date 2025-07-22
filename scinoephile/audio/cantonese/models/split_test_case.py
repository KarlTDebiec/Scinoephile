#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 splitting; may also be used for few-shot prompt."""

from __future__ import annotations

from pydantic import model_validator

from scinoephile.audio.cantonese.models.split_answer import SplitAnswer
from scinoephile.audio.cantonese.models.split_query import SplitQuery
from scinoephile.core.abcs import TestCase


class SplitTestCase(SplitQuery, SplitAnswer, TestCase[SplitQuery, SplitAnswer]):
    """Test case for 粤文 splitting; may also be used for few-shot prompt."""

    @model_validator(mode="after")
    def validate_split(self) -> SplitTestCase:
        """Ensure split text matches input text."""
        expected = self.yuewen_to_split
        received = self.one_yuewen_to_append + self.two_yuewen_to_prepend
        if expected != received:
            raise ValueError(
                "Concatenated output text does not match input text:\n"
                f"Expected: {expected}\n"
                f"Received: {received}"
            )
        return self
