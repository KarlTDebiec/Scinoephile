#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM test cases."""

from __future__ import annotations

import json
from abc import ABC
from typing import ClassVar

from pydantic import BaseModel

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
    prompt_cls: ClassVar[type[Prompt]]
    """Text for LLM correspondence."""
    query: Query
    """Query data for the test case."""
    answer: Answer | None = None
    """Answer data for the test case."""
    difficulty: int = 0
    """Difficulty level for filtering and prioritization."""
    prompt: bool = False
    """Whether the test case is included in the prompt."""
    verified: bool = False
    """Whether the test case answer has been verified."""

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)

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
