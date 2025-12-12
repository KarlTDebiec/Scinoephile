#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM test cases."""

from __future__ import annotations

import json
from abc import ABC
from typing import Any, ClassVar, Self

from pydantic import BaseModel, Field, model_validator

from .answer2 import Answer2
from .prompt2 import Prompt2
from .query2 import Query2

__all__ = ["TestCase2"]


class TestCase2(BaseModel, ABC):
    """Abstract base class for LLM test cases."""

    __test__ = False
    """Inform pytest not to collect this class as a test case."""

    answer_cls: ClassVar[type[Answer2]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[Query2]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[Prompt2]]
    """Text strings to be used for corresponding with LLM."""

    answer: Answer2 | None = None
    """Answer part of the test case."""
    query: Query2
    """Query part of the test case."""

    difficulty: int = Field(0)
    """Difficulty level of the test case, used for filtering."""
    prompt: bool = Field(False)
    """Whether to include test case in prompt examples."""
    verified: bool = Field(False)
    """Whether to include test case in the verified answers cache."""

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)

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
    def get_test_case_cls_from_data(cls, data: dict, **kwargs: Any) -> type[Self]:
        """Get concrete test case class for provided data with provided configuration.

        Arguments:
            data: data dictionary
            kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            test case class
        """
        test_case_cls = cls.get_test_case_cls(**kwargs)
        return test_case_cls

    @staticmethod
    def get_fields(
        query_cls: Query2, answer_cls: Answer2, prompt_cls: type[Prompt2]
    ) -> dict[str, Any]:
        """Get fields dictionary for dynamic TestCase class creation.

        Arguments:
            query_cls: Query class for this test case
            answer_cls: Answer class for this test case
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            fields dictionary for dynamic TestCase class creation
        """
        fields: dict[str, Any] = {
            "query": (query_cls, Field(...)),
            "answer": (answer_cls | None, Field(default=None)),
            "difficulty": (
                int,
                Field(0, description=prompt_cls.difficulty_description),
            ),
            "prompt": (
                bool,
                Field(False, description=prompt_cls.prompt_description),
            ),
            "verified": (
                bool,
                Field(False, description=prompt_cls.verified_description),
            ),
        }
        return fields
