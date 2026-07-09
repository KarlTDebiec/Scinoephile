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
    """Deterministic identifier derived from operation and normalized payload."""
    operation: str
    """Operation to which this test case belongs."""
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
    ) -> PersistedTestCase:
        """Validate raw JSON test-case data and prepare it for persistence.

        Arguments:
            data: raw JSON test-case object
            operation: operation to which the test case belongs
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
            ),
            operation=operation,
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
        base_test_case_cls: type[TestCase],
    ) -> PersistedTestCase:
        """Convert a loaded test case to its persisted representation.

        Arguments:
            test_case: loaded test case
            operation: operation to which the test case belongs
            base_test_case_cls: equivalent class using base-prompt field names
        Returns:
            persisted test case
        """
        if test_case.answer is None:
            raise ScinoephileError("Optimization test cases must include an answer.")
        query_dict = PersistedTestCase._normalize_payload(
            test_case.query.model_dump(mode="json"),
            tuple(type(test_case.query).model_fields),
            tuple(base_test_case_cls.query_cls.model_fields),
            "query",
        )
        answer_dict = PersistedTestCase._normalize_payload(
            test_case.answer.model_dump(mode="json"),
            tuple(type(test_case.answer).model_fields),
            tuple(base_test_case_cls.answer_cls.model_fields),
            "answer",
        )
        test_case_id = get_test_case_id(
            query_dict,
            answer_dict,
            operation=operation,
        )
        return PersistedTestCase(
            test_case_id=test_case_id,
            operation=operation,
            difficulty=int(test_case.difficulty),
            prompt=bool(test_case.prompt),
            verified=bool(test_case.verified),
            query=query_dict,
            answer=answer_dict,
            source_paths=[],
        )

    @staticmethod
    def _normalize_payload(
        payload: dict[str, object],
        concrete_fields: tuple[str, ...],
        base_fields: tuple[str, ...],
        payload_name: str,
    ) -> dict[str, object]:
        """Rename concrete prompt fields to equivalent base-prompt fields.

        Arguments:
            payload: concrete prompt payload
            concrete_fields: concrete prompt fields in semantic order
            base_fields: base prompt fields in semantic order
            payload_name: payload name used in validation errors
        Returns:
            payload using base-prompt field names
        Raises:
            ScinoephileError: if concrete and base schemas have different shapes
        """
        if len(concrete_fields) != len(base_fields):
            raise ScinoephileError(
                f"Concrete and base prompt {payload_name} schemas have different "
                "shapes."
            )
        return {
            base_field: payload[concrete_field]
            for concrete_field, base_field in zip(
                concrete_fields,
                base_fields,
                strict=True,
            )
        }
