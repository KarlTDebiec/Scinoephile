#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 merging; may also be used for few-shot prompt."""

from __future__ import annotations

from pydantic import model_validator

from scinoephile.audio.cantonese.models.merge_answer import MergeAnswer
from scinoephile.audio.cantonese.models.merge_query import MergeQuery
from scinoephile.core.abcs import TestCase
from scinoephile.core.text import remove_punc_and_whitespace


class MergeTestCase(MergeQuery, MergeAnswer, TestCase[MergeQuery, MergeAnswer]):
    """Test case for 粤文 merging; may also be used for few-shot prompt."""

    @model_validator(mode="after")
    def validate_merge(self) -> MergeTestCase:
        """Ensure merged text matches input text."""
        expected = "".join(remove_punc_and_whitespace(s) for s in self.yuewen_to_merge)
        received = remove_punc_and_whitespace(self.yuewen_merged)
        if expected != received:
            raise ValueError(
                "Output text stripped of punctuation and whitespace does not match "
                "input text:\n"
                f"Expected: {expected}\n"
                f"Received: {received}"
            )
        return self
