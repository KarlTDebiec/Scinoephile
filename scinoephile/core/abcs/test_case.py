#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM test cases; may also be used for few-shot prompt."""

from __future__ import annotations

import json
from abc import ABC
from typing import ClassVar, Self

from pydantic import BaseModel, Field, model_validator
from pydantic.fields import FieldInfo

from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.llm_text import LLMText
from scinoephile.core.abcs.query import Query
from scinoephile.core.models import format_field


class TestCase[TQuery: Query, TAnswer: Answer](BaseModel, ABC):
    """Abstract base class for LLM test cases; may also be used for few-shot prompt.

    Difficulty of 1 indicates that the test case represents nontrivial work; e.g.
    text that needs to be split.
    Difficulty of 2 indicates that the test case represents more difficult work; e.g.
    copying over punctuation from source text to target text, and needing to add
    additional punctuation due to large differences between the source and target. In
    addition, all test cases that are included in the prompt are assigned a difficulty
    of 2.
    Difficulty of 3 indicates that the test case is not reasonably solvable; e.g. the
    source text and target text are completely different, and the requested operation
    is not possible.
    """

    __test__ = False
    """Inform pytest not to collect this class as a test case."""

    answer_cls: ClassVar[type[Answer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[Query]]
    """Query class for this test case."""
    text: ClassVar[type[LLMText]]
    """Text strings to be used for corresponding with LLM."""

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

    @property
    def answer(self) -> TAnswer:
        """Answer part of the test case."""
        return self.answer_cls.model_validate(
            {k: getattr(self, k) for k in self.answer_cls.model_fields}
        )

    @property
    def answer_fields(self) -> dict[str, FieldInfo]:
        """List of answer fields."""
        return self.answer_cls.model_fields

    @property
    def query(self) -> TQuery:
        """Query part of the test case."""
        return self.query_cls.model_validate(
            {k: getattr(self, k) for k in self.query_fields}
        )

    @property
    def query_fields(self) -> dict[str, FieldInfo]:
        """List of query fields."""
        return self.query_cls.model_fields

    @property
    def source_str(self) -> str:
        """Python source-like string representation."""
        lines = [f"{self.__class__.__name__}("]
        for field in self.query_fields:
            value = getattr(self, field)
            lines.append(format_field(field, value))
        for field in self.answer_fields:
            value = getattr(self, field)
            if value == "":
                continue
            lines.append(format_field(field, value))
        for field in self.test_case_fields:
            value = getattr(self, field)
            lines.append(format_field(field, value))
        lines.append(")")
        return "\n".join(lines)

    @property
    def test_case_fields(self) -> dict[str, FieldInfo]:
        """List of test case fields."""
        exclusions = set()
        if not self.difficulty:
            exclusions.add("difficulty")
        if not self.prompt:
            exclusions.add("prompt")
        if not self.verified:
            exclusions.add("verified")
        exclusions.update(self.query_fields)
        exclusions.update(self.answer_fields)
        return {k: v for k, v in self.model_fields.items() if k not in exclusions}

    @model_validator(mode="after")
    def enforce_min_difficulty(self) -> Self:
        """Ensure difficulty reflects prompt/split status if not already higher."""
        self.difficulty = max(self.difficulty, self.get_min_difficulty())
        return self

    def get_auto_verified(self) -> bool:
        """Whether this test case should automatically be verified."""
        return False

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty based on the test case properties.

        0: No change needed
        1: Change needed
        2: Difficult change needed, worthy of inclusion in prompt or difficult test set
        3: Not considered realistic for LLM to handle correctly

        Returns:
            minimum difficulty level based on the test case properties
        """
        return 0

    @classmethod
    def from_query_and_answer(cls, query: TQuery, answer: TAnswer) -> Self:
        """Create test case from query and answer.

        Arguments:
            query: Query part of the test case
            answer: Answer part of the test case
        Returns:
            Test case combining the query and answer
        """
        return cls(**query.model_dump(), **answer.model_dump())
