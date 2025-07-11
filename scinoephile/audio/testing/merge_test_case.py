#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 merging; may also be used for few-shot prompt."""

from __future__ import annotations

from pydantic import Field

from scinoephile.audio.models import MergeAnswer, MergeQuery


class MergeTestCase(MergeQuery, MergeAnswer):
    """Test case for 粤文 merging; may also be used for few-shot prompt."""

    include_in_prompt: bool = Field(
        False, description="Whether to include test case in prompt examples."
    )

    @property
    def answer(self) -> MergeAnswer:
        """Answer part of the test case."""
        return MergeAnswer.model_validate(
            {k: getattr(self, k) for k in MergeAnswer.model_fields}
        )

    @property
    def query(self) -> MergeQuery:
        """Query part of the test case."""
        return MergeQuery.model_validate(
            {k: getattr(self, k) for k in MergeQuery.model_fields}
        )

    @staticmethod
    def from_query_and_answer(
        query: MergeQuery, answer: MergeAnswer, include_in_prompt: bool = False
    ) -> MergeTestCase:
        """Create a test case from a query and an answer."""
        return MergeTestCase(
            **query.model_dump(),
            **answer.model_dump(),
            include_in_prompt=include_in_prompt,
        )
