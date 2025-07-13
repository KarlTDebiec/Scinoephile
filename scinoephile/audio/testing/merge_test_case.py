#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 merging; may also be used for few-shot prompt."""

from __future__ import annotations

import json

from pydantic import Field, model_validator

from scinoephile.audio.models import MergeAnswer, MergeQuery
from scinoephile.core.text import remove_punc_and_whitespace


class MergeTestCase(MergeQuery, MergeAnswer):
    """Test case for 粤文 merging; may also be used for few-shot prompt."""

    include_in_prompt: bool = Field(
        False, description="Whether to include test case in prompt examples."
    )

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)

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
        """Create test case from query and answer."""
        return MergeTestCase(
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

        lines = ["MergeTestCase("]

        # Fields from query
        for field in MergeQuery.model_fields:
            lines.append(format_field(field, getattr(self, field)))

        # Fields from answer
        for field in MergeAnswer.model_fields:
            lines.append(format_field(field, getattr(self, field)))

        # Fields from test case
        test_case_fields = (
            set(self.model_fields)
            - set(MergeQuery.model_fields)
            - set(MergeAnswer.model_fields)
        )
        for field in MergeTestCase.model_fields:
            if field in test_case_fields:
                lines.append(format_field(field, getattr(self, field)))

        lines.append(")")
        return "\n".join(lines)

    @model_validator(mode="after")
    def validate_merge(self) -> MergeTestCase:
        """Ensure merged text matches input text."""
        expected = "".join(remove_punc_and_whitespace(s) for s in self.yuewen_to_merge)
        received = remove_punc_and_whitespace(self.yuewen_merged)
        if expected != received:
            raise ValueError(
                "Output text does not match input:\n"
                f"Expected: {expected}\n"
                f"Received: {received}"
            )
        return self
