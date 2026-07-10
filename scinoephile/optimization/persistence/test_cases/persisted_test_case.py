#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Persisted LLM test case model."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.llms import OperationSpec, TestCase

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
    """Query JSON using base-prompt field names."""
    answer: dict[str, object]
    """Answer JSON using base-prompt field names."""
    source_paths: tuple[str, ...]
    """Source JSON paths that contributed this test case."""

    @classmethod
    def from_test_case(
        cls,
        test_case: TestCase,
        *,
        operation_spec: OperationSpec,
        base_test_case_cls: type[TestCase],
    ) -> PersistedTestCase:
        """Convert a loaded test case to its persisted representation.

        Arguments:
            test_case: loaded test case
            operation_spec: operation to which the test case belongs
            base_test_case_cls: equivalent class using base-prompt field names
        Returns:
            persisted test case
        """
        if test_case.answer is None:
            raise ScinoephileError("Optimization test cases must include an answer.")
        query = cls._normalize_payload(
            test_case.query.model_dump(mode="json"),
            tuple(type(test_case.query).model_fields),
            tuple(base_test_case_cls.query_cls.model_fields),
            "query",
        )
        answer = cls._normalize_payload(
            test_case.answer.model_dump(mode="json"),
            tuple(type(test_case.answer).model_fields),
            tuple(base_test_case_cls.answer_cls.model_fields),
            "answer",
        )
        return cls(
            test_case_id=get_test_case_id(
                query,
                answer,
                operation_spec=operation_spec,
            ),
            operation=operation_spec.operation,
            difficulty=test_case.difficulty,
            prompt=test_case.prompt,
            verified=test_case.verified,
            query=query,
            answer=answer,
            source_paths=(),
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
