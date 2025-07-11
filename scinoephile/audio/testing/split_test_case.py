#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 splitting; may also be used for few-shot prompt."""

from __future__ import annotations

from pydantic import Field

from scinoephile.audio.models import SplitAnswer, SplitQuery


class SplitTestCase(SplitQuery, SplitAnswer):
    """Test case for 粤文 splitting; may also be used for few-shot prompt."""

    include_in_prompt: bool = Field(
        False, description="Whether to include test case in prompt examples."
    )

    @property
    def answer(self) -> SplitAnswer:
        """Answer part of the test case."""
        return SplitAnswer.model_validate(
            {k: getattr(self, k) for k in SplitAnswer.model_fields}
        )

    @property
    def query(self) -> SplitQuery:
        """Query part of the test case."""
        return SplitQuery.model_validate(
            {k: getattr(self, k) for k in SplitQuery.model_fields}
        )

    @staticmethod
    def from_query_and_answer(
        query: SplitQuery, answer: SplitAnswer, include_in_prompt: bool = False
    ) -> SplitTestCase:
        """Create a test case from a query and an answer."""
        return SplitTestCase(
            **query.model_dump(),
            **answer.model_dump(),
            include_in_prompt=include_in_prompt,
        )
