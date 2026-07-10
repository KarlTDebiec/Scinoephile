#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Mapping between equivalent LLM test-case schemas."""

from __future__ import annotations

from typing import cast

from pydantic import JsonValue

from scinoephile.core.exceptions import ScinoephileError

from .test_case import TestCase

__all__ = ["remap_test_case"]


def remap_test_case[TTestCase: TestCase](
    test_case: TestCase,
    target_test_case_cls: type[TTestCase],
) -> TTestCase:
    """Remap a test case to an equivalent class with different field names.

    Query and answer fields are matched by their semantic order in each model.

    Arguments:
        test_case: test case to remap
        target_test_case_cls: equivalent test-case class using target field names
    Returns:
        test case using target field names
    Raises:
        ScinoephileError: if the source and target schemas have different shapes
    """
    data = test_case.model_dump(mode="json")
    data["query"] = _remap_payload_fields(
        cast("dict[str, JsonValue]", data["query"]),
        tuple(type(test_case.query).model_fields),
        tuple(target_test_case_cls.query_cls.model_fields),
        "query",
    )
    if test_case.answer is not None:
        data["answer"] = _remap_payload_fields(
            cast("dict[str, JsonValue]", data["answer"]),
            tuple(type(test_case.answer).model_fields),
            tuple(target_test_case_cls.answer_cls.model_fields),
            "answer",
        )
    return target_test_case_cls.model_validate(data)


def _remap_payload_fields(
    payload: dict[str, JsonValue],
    source_fields: tuple[str, ...],
    target_fields: tuple[str, ...],
    payload_name: str,
) -> dict[str, JsonValue]:
    """Rename fields between equivalent query or answer schemas.

    Arguments:
        payload: payload using source field names
        source_fields: source fields in semantic order
        target_fields: target fields in semantic order
        payload_name: payload name used in validation errors
    Returns:
        payload using target field names
    Raises:
        ScinoephileError: if the source and target schemas have different shapes
    """
    if len(source_fields) != len(target_fields):
        raise ScinoephileError(
            f"Source and target {payload_name} schemas have different shapes."
        )
    return {
        target_field: payload[source_field]
        for source_field, target_field in zip(
            source_fields,
            target_fields,
            strict=True,
        )
    }
