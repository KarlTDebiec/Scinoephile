#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM test cases."""

from __future__ import annotations

import json
from abc import ABC
from typing import Any, ClassVar, Self

from pydantic import BaseModel, Field, model_validator

from .answer import Answer
from .prompt import Prompt
from .query import Query

__all__ = ["TestCase"]


class TestCase(BaseModel, ABC):
    """ABC for LLM test cases."""

    __test__ = False
    """Inform pytest not to collect this class as a test case."""

    answer_cls: ClassVar[type[Answer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[Query]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[Prompt]]
    """Text for LLM correspondence."""

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
    def get_test_case_cls_from_data(
        cls,
        data: dict,
        **kwargs: Any,
    ) -> type[Self]:
        """Get concrete test case class for provided data with provided configuration.

        Arguments:
            data: data from JSON
            kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            test case class
        """
        return cls.get_test_case_cls(**kwargs)

    @staticmethod
    def get_fields(
        query_cls: Query, answer_cls: Answer, prompt_cls: type[Prompt]
    ) -> dict[str, Any]:
        """Get fields dictionary for dynamic TestCase class creation.

        Arguments:
            query_cls: Query class for this test case
            answer_cls: Answer class for this test case
            prompt_cls: text for LLM correspondence
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
