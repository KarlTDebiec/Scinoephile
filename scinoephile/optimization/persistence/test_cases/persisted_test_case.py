#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Persisted LLM test case model."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import JsonValue

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.llms import Manager, TestCase
from scinoephile.core.llms.test_case_mapping import remap_test_case

from .id import get_test_case_id

__all__ = ["PersistedTestCase"]


@dataclass(frozen=True, slots=True)
class PersistedTestCase:
    """A persisted test case row loaded from SQLite."""

    test_case_id: str
    """Deterministic identifier derived from operation and normalized payload."""
    operation: str
    """Operation to which this test case belongs."""
    difficulty: int
    """Difficulty level for filtering and prioritization."""
    few_shot: bool
    """Whether the test case is included as a few-shot example."""
    verified: bool
    """Whether the test case answer has been verified."""
    query: dict[str, JsonValue]
    """Query JSON using base-prompt field names."""
    answer: dict[str, JsonValue]
    """Answer JSON using base-prompt field names."""
    source_paths: tuple[str, ...]
    """Source JSON paths that contributed this test case."""

    @classmethod
    def from_test_case(
        cls,
        test_case: TestCase,
        manager_cls: type[Manager],
    ) -> PersistedTestCase:
        """Convert a loaded test case to its persisted representation.

        Arguments:
            test_case: loaded test case
            manager_cls: manager defining the test case's operation and base prompt
        Returns:
            persisted test case
        """
        if test_case.answer is None:
            raise ScinoephileError("Optimization test cases must include an answer.")
        base_test_case_cls = manager_cls.get_test_case_cls(
            manager_cls.base_prompt,
        )
        base_test_case = remap_test_case(test_case, base_test_case_cls)
        query = base_test_case.query.model_dump(mode="json")
        if base_test_case.answer is None:
            raise ScinoephileError("Optimization test cases must include an answer.")
        answer = base_test_case.answer.model_dump(mode="json")
        test_case_id = get_test_case_id(query, answer, manager_cls)
        return cls(
            test_case_id=test_case_id,
            operation=manager_cls.operation,
            difficulty=test_case.difficulty,
            few_shot=test_case.few_shot,
            verified=test_case.verified,
            query=query,
            answer=answer,
            source_paths=(),
        )
