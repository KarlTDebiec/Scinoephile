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
    """Deterministic identifier derived from operation, variant, and payload."""
    operation: str
    """Operation to which this test case belongs."""
    variant: str
    """Stable schema variant within the operation."""
    difficulty: int
    """Difficulty level for filtering and prioritization."""
    prompt: bool
    """Whether the test case is included in the prompt."""
    verified: bool
    """Whether the test case answer has been verified."""
    query: dict[str, object]
    """Query JSON."""
    answer: dict[str, object]
    """Answer JSON."""
    source_paths: list[str]
    """Source JSON paths that contributed this test case."""

    @classmethod
    def from_json_data(
        cls,
        data: object,
        *,
        operation: str,
        variant: str,
    ) -> PersistedTestCase:
        """Validate raw JSON test-case data and prepare it for persistence.

        Arguments:
            data: raw JSON test-case object
            operation: operation to which the test case belongs
            variant: stable schema variant within the operation
        Returns:
            persisted test case
        Raises:
            ScinoephileError: if the serialized test case has an invalid shape
        """
        if not isinstance(data, dict):
            raise ScinoephileError("Each optimization test case must be an object.")
        if not operation.strip():
            raise ScinoephileError(
                "Optimization test case operation must not be empty."
            )
        if not variant.strip():
            raise ScinoephileError("Optimization test case variant must not be empty.")

        allowed_fields = {"answer", "difficulty", "prompt", "query", "verified"}
        unexpected_fields = sorted(set(data) - allowed_fields)
        if unexpected_fields:
            fields = ", ".join(str(field) for field in unexpected_fields)
            raise ScinoephileError(
                f"Optimization test case contains unexpected fields: {fields}."
            )

        query = data.get("query")
        if not isinstance(query, dict):
            raise ScinoephileError(
                "Optimization test case query must be a JSON object."
            )
        if any(not isinstance(key, str) for key in query):
            raise ScinoephileError("Optimization test case query keys must be strings.")
        query_payload = {
            key: value for key, value in query.items() if isinstance(key, str)
        }
        answer = data.get("answer")
        if not isinstance(answer, dict):
            raise ScinoephileError(
                "Optimization test case answer must be a JSON object."
            )
        if any(not isinstance(key, str) for key in answer):
            raise ScinoephileError(
                "Optimization test case answer keys must be strings."
            )
        answer_payload = {
            key: value for key, value in answer.items() if isinstance(key, str)
        }

        difficulty = data.get("difficulty", 0)
        if type(difficulty) is not int:
            raise ScinoephileError(
                "Optimization test case difficulty must be an integer."
            )
        prompt = data.get("prompt", False)
        if type(prompt) is not bool:
            raise ScinoephileError(
                "Optimization test case prompt flag must be a boolean."
            )
        verified = data.get("verified", False)
        if type(verified) is not bool:
            raise ScinoephileError(
                "Optimization test case verified flag must be a boolean."
            )

        return cls(
            test_case_id=get_test_case_id(
                query_payload,
                answer_payload,
                operation=operation,
                variant=variant,
            ),
            operation=operation,
            variant=variant,
            difficulty=difficulty,
            prompt=prompt,
            verified=verified,
            query=query_payload,
            answer=answer_payload,
            source_paths=[],
        )

    @staticmethod
    def from_test_case(
        test_case: TestCase,
        *,
        operation: str,
        variant: str,
    ) -> PersistedTestCase:
        """Convert a loaded test case to its persisted representation.

        Arguments:
            test_case: loaded test case
            operation: operation to which the test case belongs
            variant: stable schema variant within the operation
        Returns:
            persisted test case
        """
        query_dict = test_case.query.model_dump(mode="json")
        if test_case.answer is None:
            raise ScinoephileError("Optimization test cases must include an answer.")
        answer_dict = test_case.answer.model_dump(mode="json")
        test_case_id = get_test_case_id(
            test_case.query,
            test_case.answer,
            operation=operation,
            variant=variant,
        )
        return PersistedTestCase(
            test_case_id=test_case_id,
            operation=operation,
            variant=variant,
            difficulty=int(test_case.difficulty),
            prompt=bool(test_case.prompt),
            verified=bool(test_case.verified),
            query=query_dict,
            answer=answer_dict,
            source_paths=[],
        )
