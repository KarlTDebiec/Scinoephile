#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM test cases."""

from __future__ import annotations

import json
from abc import ABC
from typing import ClassVar, Self

from pydantic import BaseModel, Field, model_validator

from .answer import Answer
from .prompt import Prompt
from .query import Query

__all__ = ["TestCase"]


class TestCase(BaseModel, ABC):
    """ABC for LLM test cases."""

    __test__ = False
    """Inform pytest not to collect this class as a test case."""

    query_cls: ClassVar[type[Query]]
    """Query model class."""
    answer_cls: ClassVar[type[Answer]]
    """Answer model class."""
    prompt: ClassVar[Prompt]
    """Text for LLM correspondence."""
    query: Query
    """Query data for the test case."""
    answer: Answer | None = None
    """Answer data for the test case."""
    difficulty: int = Field(
        0,
        description="Difficulty level of the test case, used for filtering.",
    )
    """Difficulty level for filtering and prioritization."""
    few_shot: bool = Field(
        False,
        description="Whether to include test case in few-shot examples.",
    )
    """Whether the test case is included as a few-shot example."""
    verified: bool = Field(
        False,
        description="Whether to include test case in the verified answers cache.",
    )
    """Whether the test case answer has been verified."""

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)

    @model_validator(mode="after")
    def enforce_min_difficulty(self) -> Self:
        """Ensure difficulty is at least the model-defined minimum.

        Returns:
            validated test case
        """
        self.difficulty = max(self.difficulty, self.get_min_difficulty())
        return self

    @model_validator(mode="after")
    def require_answer(self) -> Self:
        """Ensure few-shot and verified test cases include an answer.

        Returns:
            validated test case
        """
        if self.answer is None and (self.few_shot or self.verified):
            raise ValueError("Few-shot and verified test cases must include an answer.")
        return self

    def get_auto_verified(self) -> bool:
        """Whether this test case should automatically be verified.

        Returns:
            whether the test case should be auto-verified
        """
        return False

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty based on the test case properties.

        Returns:
            minimum difficulty
        """
        return 0
