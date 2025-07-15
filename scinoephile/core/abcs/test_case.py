#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM test cases; may also be used for few-shot prompt."""

from __future__ import annotations

import json
from abc import ABC
from functools import cached_property
from typing import Self

from pydantic import BaseModel, Field

from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.query import Query


class TestCase[TQuery: Query, TAnswer: Answer](BaseModel, ABC):
    """Abstract base class for LLM test cases; may also be used for few-shot prompt."""

    __test__ = False
    """Inform pytest not to collect this class as a test case."""

    include_in_prompt: bool = Field(
        False, description="Whether to include test case in prompt examples."
    )

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)

    @cached_property
    def answer_cls(self) -> type[TAnswer]:
        """Answer parent class."""
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
        """Query parent class."""
        for base in type(self).__mro__:
            if base is not self.__class__ and issubclass(base, Query):
                return base
        raise TypeError("No Query subclass found in MRO.")

    def to_source(self) -> str:
        """Get Python source-like string representation."""

        def format_field(name: str, value: object) -> str:
            return f"    {name}={value!r},"

        lines = [f"{self.__class__.__name__}("]

        lines.extend(
            format_field(field, getattr(self, field))
            for field in self.query_cls.model_fields
        )

        lines.extend(
            format_field(field, getattr(self, field))
            for field in self.answer_cls.model_fields
        )

        test_case_fields = (
            set(self.model_fields)
            - set(self.query_cls.model_fields)
            - set(self.answer_cls.model_fields)
        )
        lines.extend(
            format_field(field, getattr(self, field)) for field in test_case_fields
        )

        lines.append(")")
        return "\n".join(lines)

    @classmethod
    def from_query_and_answer(
        cls, query: TQuery, answer: TAnswer, include_in_prompt: bool = False
    ) -> Self:
        """Create test case from query and answer.

        Arguments:
            query: Query part of the test case
            answer: Answer part of the test case
            include_in_prompt: Whether to include this test case in prompt examples
        """
        return cls(
            **query.model_dump(),
            **answer.model_dump(),
            include_in_prompt=include_in_prompt,
        )
