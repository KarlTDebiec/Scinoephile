#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 shifting; may also be used for few-shot prompt."""

from __future__ import annotations

import json

from pydantic import Field, model_validator

from scinoephile.audio.models import ShiftAnswer, ShiftQuery
from scinoephile.core.text import remove_punc_and_whitespace


class ShiftTestCase(ShiftQuery, ShiftAnswer):
    """Test case for 粤文 shifting; may also be used for few-shot prompt."""

    include_in_prompt: bool = Field(
        False, description="Whether to include test case in prompt examples."
    )

    def __str__(self) -> str:
        """Return string representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)

    @property
    def answer(self) -> ShiftAnswer:
        """Answer part of the test case."""
        return ShiftAnswer.model_validate(
            {k: getattr(self, k) for k in ShiftAnswer.model_fields}
        )

    @property
    def query(self) -> ShiftQuery:
        """Query part of the test case."""
        return ShiftQuery.model_validate(
            {k: getattr(self, k) for k in ShiftQuery.model_fields}
        )

    @staticmethod
    def from_query_and_answer(
        query: ShiftQuery, answer: ShiftAnswer, include_in_prompt: bool = False
    ) -> ShiftTestCase:
        """Create test case from query and answer."""
        return ShiftTestCase(
            **query.model_dump(),
            **answer.model_dump(),
            include_in_prompt=include_in_prompt,
        )

    def to_source(self) -> str:
        """Get Python source-like string representation."""

        def format_field(name: str, value: object) -> str:
            return f"    {name}={value!r},"

        lines = ["ShiftTestCase("]

        for field in ShiftQuery.model_fields:
            lines.append(format_field(field, getattr(self, field)))

        for field in ShiftAnswer.model_fields:
            lines.append(format_field(field, getattr(self, field)))

        test_case_fields = (
            set(self.model_fields)
            - set(ShiftQuery.model_fields)
            - set(ShiftAnswer.model_fields)
        )
        for field in ShiftTestCase.model_fields:
            if field in test_case_fields:
                lines.append(format_field(field, getattr(self, field)))

        lines.append(")")
        return "\n".join(lines)

    @model_validator(mode="after")
    def validate_shift(self) -> ShiftTestCase:
        """Ensure shifted text matches input text."""
        expected = remove_punc_and_whitespace(self.one_yuewen + self.two_yuewen)
        received = remove_punc_and_whitespace(
            self.one_yuewen_shifted + self.two_yuewen_shifted
        )
        if expected != received:
            raise ValueError(
                "Output text does not match input:\n"
                f"Expected: {expected}\n"
                f"Received: {received}"
            )
        return self
