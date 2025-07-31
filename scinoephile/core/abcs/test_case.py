#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM test cases; may also be used for few-shot prompt."""

from __future__ import annotations

import json
from abc import ABC
from functools import cached_property
from typing import Self

from pydantic import BaseModel, Field, model_validator

from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.query import Query
from scinoephile.core.models import format_field


class TestCase[TQuery: Query, TAnswer: Answer](BaseModel, ABC):
    """Abstract base class for LLM test cases; may also be used for few-shot prompt."""

    __test__ = False
    """Inform pytest not to collect this class as a test case."""

    difficulty: int = Field(
        0, description="Difficulty level of the test case, used for filtering."
    )
    prompt: bool = Field(
        False, description="Whether to include test case in prompt examples."
    )
    verified: bool = Field(
        False, description="Whether to include test case in the verified answers cache."
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

    @cached_property
    def key(self) -> tuple[str, ...]:
        """Unique key for the test case."""
        return tuple(list(self.query.query_key) + list(self.answer.answer_key))

    @cached_property
    def noop(self) -> bool:
        """Whether this test case is a no-op."""
        return False

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

    @cached_property
    def source_str(self) -> str:
        """Get Python source-like string representation."""
        query_fields = self.query_cls.model_fields
        answer_fields = self.answer_cls.model_fields
        exclusions = set()
        if not self.difficulty:
            exclusions.add("difficulty")
        if not self.prompt:
            exclusions.add("prompt")
        if not self.verified:
            exclusions.add("verified")
        test_case_fields = (
            set(self.model_fields) - set(query_fields) - set(answer_fields) - exclusions
        )

        lines = (
            [f"{self.__class__.__name__}("]
            + [format_field(field, getattr(self, field)) for field in query_fields]
            + [format_field(field, getattr(self, field)) for field in answer_fields]
            + [format_field(field, getattr(self, field)) for field in test_case_fields]
            + [")"]
        )
        return "\n".join(lines)

    @model_validator(mode="after")
    def enforce_min_difficulty(self) -> Self:
        """Ensure difficulty reflects prompt/split status if not already higher."""
        self.difficulty = max(self.difficulty, self.get_min_difficulty())
        return self

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty.

        If test case is marked for inclusion in the prompt, minimum difficulty is at
        least 2.

        Returns:
            Minimum difficulty level based on the test case properties
        """
        min_difficulty = 0
        if self.prompt:
            min_difficulty = max(min_difficulty, 2)
        return min_difficulty

    @classmethod
    def from_query_and_answer(
        cls, query: TQuery, answer: TAnswer, prompt: bool = False
    ) -> Self:
        """Create test case from query and answer.

        Arguments:
            query: Query part of the test case
            answer: Answer part of the test case
            prompt: Whether to include this test case in prompt examples
        """
        return cls(**query.model_dump(), **answer.model_dump(), prompt=prompt)
