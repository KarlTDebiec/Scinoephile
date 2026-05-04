#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Persisted LLM test case model."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.llms import TestCase

from .id import get_test_case_id

__all__ = ["PersistedTestCase"]


@dataclass(frozen=True, slots=True)
class PersistedTestCase:
    """A persisted test case row loaded from SQLite."""

    test_case_id: str
    """Deterministic identifier derived from query+answer JSON."""
    difficulty: int
    """Difficulty level for filtering and prioritization."""
    prompt: bool
    """Whether the test case is included in the prompt."""
    verified: bool
    """Whether the test case answer has been verified."""
    query: dict
    """Query JSON."""
    answer: dict
    """Answer JSON."""
    source_paths: list[str]
    """Source JSON paths that contributed this test case."""

    @staticmethod
    def from_test_case(test_case: TestCase) -> PersistedTestCase:
        """Convert a loaded test case to its persisted representation.

        Arguments:
            test_case: loaded test case
        Returns:
            persisted test case
        """
        query_dict = test_case.query.model_dump()
        if test_case.answer is None:
            raise ScinoephileError("Optimization test cases must include an answer.")
        answer_dict = test_case.answer.model_dump()
        test_case_id = get_test_case_id(test_case.query, test_case.answer)
        return PersistedTestCase(
            test_case_id=test_case_id,
            difficulty=int(test_case.difficulty),
            prompt=bool(test_case.prompt),
            verified=bool(test_case.verified),
            query=query_dict,
            answer=answer_dict,
            source_paths=[],
        )
