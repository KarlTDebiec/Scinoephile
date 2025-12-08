#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM test cases."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Self

from pydantic import BaseModel, Field

from .answer2 import Answer2
from .prompt2 import Prompt2
from .query2 import Query2

__all__ = ["TestCase2"]


class TestCase2[TQuery: Query2, TAnswer: Answer2](BaseModel, ABC):
    """Abstract base class for LLM test cases."""

    __test__ = False
    """Inform pytest not to collect this class as a test case."""

    answer_cls: ClassVar[type[Answer2]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[Query2]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[Prompt2]]
    """Text strings to be used for corresponding with LLM."""

    answer: TAnswer | None = None
    """Answer part of the test case."""
    query: TQuery
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

    @classmethod
    @abstractmethod
    def get_test_case_cls_from_data(cls, data: dict, **kwargs: Any) -> type[Self]:
        """Get test case class from data.

        Arguments:
            data: data dictionary
        Returns:
            test case class
        """
        raise NotImplementedError()
