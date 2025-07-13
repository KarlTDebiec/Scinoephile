#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case; may also be used for few-shot prompt."""

from __future__ import annotations

import json
from abc import ABC
from functools import cached_property

from pydantic import BaseModel, Field

from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.query import Query


class TestCase[TQuery: Query, TAnswer: Answer](BaseModel, ABC):
    """Test case; may also be used for few-shot prompt."""

    include_in_prompt: bool = Field(
        False, description="Whether to include test case in prompt examples."
    )

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)

    @cached_property
    def answer_cls(self) -> type[TAnswer]:
        for base in type(self).__mro__:
            if base is not self.__class__ and issubclass(base, Answer):
                return base
        raise TypeError("No Answer subclass found in MRO.")

    @property
    def answer(self) -> TAnswer:
        """Answer part of the test case."""
        return self.answer_cls.model_validate(
            {k: getattr(self, k) for k in self.answer_cls.model_fields}
        )

    @property
    def query(self) -> TQuery:
        """Query part of the test case."""
        return self.query_cls.model_validate(
            {k: getattr(self, k) for k in self.query_cls.model_fields}
        )

    @cached_property
    def query_cls(self) -> type[TQuery]:
        for base in type(self).__mro__:
            if base is not self.__class__ and issubclass(base, Query):
                return base
        raise TypeError("No Query subclass found in MRO.")

    def to_source(self) -> str:
        """Get Python source-like string representation."""
        cls = self.__class__

        def format_field(name: str, value: object) -> str:
            return f"    {name}={value!r},"

        lines = [f"{cls.__name__}("]

        for field in self.query_cls.model_fields:
            lines.append(format_field(field, getattr(self, field)))

        for field in self.answer_cls.model_fields:
            lines.append(format_field(field, getattr(self, field)))

        test_case_fields = (
            set(self.model_fields)
            - set(self.query_cls.model_fields)
            - set(self.answer_cls.model_fields)
        )
        for field in cls.model_fields:
            if field in test_case_fields:
                lines.append(format_field(field, getattr(self, field)))

        lines.append(")")
        return "\n".join(lines)

    @classmethod
    def from_query_and_answer(
        cls, query: TQuery, answer: TAnswer, include_in_prompt: bool = False
    ) -> TestCase:
        """Create test case from query and answer."""
        return cls(
            **query.model_dump(),
            **answer.model_dump(),
            include_in_prompt=include_in_prompt,
        )
