#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 splitting; may also be used for few-shot prompt."""

from __future__ import annotations

import json

from pydantic import Field, model_validator

from scinoephile.audio.models import SplitAnswer, SplitQuery


class SplitTestCase(SplitQuery, SplitAnswer):
    """Test case for 粤文 splitting; may also be used for few-shot prompt."""

    include_in_prompt: bool = Field(
        False, description="Whether to include test case in prompt examples."
    )

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)

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
        """Create test case from query and answer."""
        return SplitTestCase(
            **query.model_dump(),
            **answer.model_dump(),
            include_in_prompt=include_in_prompt,
        )

    def to_source(self) -> str:
        """Get Python source-like string representation.

        Returns:
            Python source-like string representation
        """

        def format_field(name: str, value: object) -> str:
            return f"    {name}={value!r},"

        lines = ["SplitTestCase("]

        # Fields from query
        for field in SplitQuery.model_fields:
            lines.append(format_field(field, getattr(self, field)))

        # Fields from answer
        for field in SplitAnswer.model_fields:
            lines.append(format_field(field, getattr(self, field)))

        # Fields from test case
        test_case_fields = (
            set(self.model_fields)
            - set(SplitQuery.model_fields)
            - set(SplitAnswer.model_fields)
        )
        for field in SplitTestCase.model_fields:
            if field in test_case_fields:
                lines.append(format_field(field, getattr(self, field)))

        lines.append(")")
        return "\n".join(lines)

    @model_validator(mode="after")
    def validate_split(self) -> SplitTestCase:
        """Ensure split text matches input text."""
        expected = self.yuewen_to_split
        received = self.one_yuewen_to_append + self.two_yuewen_to_prepend
        if expected != received:
            raise ValueError(
                "Output text does not match input:\n"
                f"Expected: {expected}\n"
                f"Received: {received}"
            )
        return self
