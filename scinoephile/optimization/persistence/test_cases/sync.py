#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""JSON to SQLite synchronization for LLM test cases."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from pydantic import ValidationError

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.llms import OperationSpec, Prompt, TestCase

from .persisted_test_case import PersistedTestCase
from .sqlite_store import TestCaseSqliteStore

__all__ = [
    "SyncReport",
    "sync_test_cases_from_json_paths",
]


@dataclass(frozen=True, slots=True)
class SyncReport:
    """Summary of a sync operation."""

    operation: str
    """Operation that was synchronized."""
    input_paths: tuple[Path, ...]
    """Input JSON paths included in the sync run."""
    insert_ids: tuple[str, ...]
    """Test case identifiers whose source association would be inserted."""
    delete_ids: tuple[str, ...]
    """Test case identifiers whose source association would be removed."""


def sync_test_cases_from_json_paths(
    *,
    database_path: Path,
    operation_spec: OperationSpec,
    source_prompt_cls: type[Prompt],
    input_paths: Iterable[Path],
    dry_run: bool,
) -> SyncReport:
    """Synchronize test cases from JSON files into SQLite.

    Source prompt field names are normalized to the operation's base prompt field
    names before test-case IDs are computed. All input files are loaded and validated
    before the database is modified.

    Arguments:
        database_path: SQLite database path
        operation_spec: operation, manager, and base prompt configuration
        source_prompt_cls: prompt class defining the input JSON field names
        input_paths: JSON paths to import or synchronize
        dry_run: if True, report planned changes without writing
    Returns:
        sync report
    Raises:
        ScinoephileError: if the source prompt does not belong to the operation
    """
    if not issubclass(source_prompt_cls, operation_spec.prompt_cls):
        raise ScinoephileError(
            f"Source prompt {source_prompt_cls.__name__} is not a subclass of "
            f"{operation_spec.prompt_cls.__name__} for operation "
            f"{operation_spec.operation}."
        )

    input_paths_tuple = tuple(input_path.resolve() for input_path in input_paths)
    source_test_cases = {
        str(input_path): _load_test_cases(
            input_path,
            operation_spec=operation_spec,
            source_prompt_cls=source_prompt_cls,
        )
        for input_path in input_paths_tuple
    }

    store = TestCaseSqliteStore(database_path)
    insert_ids, delete_ids = store.sync_source_paths(
        source_test_cases,
        dry_run=dry_run,
    )
    return SyncReport(
        operation=operation_spec.operation,
        input_paths=input_paths_tuple,
        insert_ids=tuple(sorted(insert_ids)),
        delete_ids=tuple(sorted(delete_ids)),
    )


def _load_test_cases(
    input_path: Path,
    *,
    operation_spec: OperationSpec,
    source_prompt_cls: type[Prompt],
) -> list[PersistedTestCase]:
    """Load, validate, and normalize persisted test cases from JSON.

    Arguments:
        input_path: path to a JSON test-case array
        operation_spec: operation, manager, and base prompt configuration
        source_prompt_cls: prompt class defining the input JSON field names
    Returns:
        persisted test cases using base-prompt field names
    Raises:
        ScinoephileError: if the file cannot be loaded or contains an invalid case
    """
    try:
        with open(input_path, encoding="utf-8") as input_file:
            data = json.load(input_file)
    except (OSError, json.JSONDecodeError) as exc:
        raise ScinoephileError(
            f"Unable to load optimization test cases from {input_path}: {exc}"
        ) from exc
    if not isinstance(data, list):
        raise ScinoephileError(
            f"Optimization test-case file {input_path} must contain a JSON array."
        )

    test_cases: list[PersistedTestCase] = []
    for index, item in enumerate(data, start=1):
        try:
            item_dict = _validate_json_object(item)
            test_case = _normalize_test_case(
                item_dict,
                operation_spec=operation_spec,
                source_prompt_cls=source_prompt_cls,
            )
        except (
            AttributeError,
            KeyError,
            ScinoephileError,
            TypeError,
            ValidationError,
        ) as exc:
            raise ScinoephileError(
                f"Invalid optimization test case {index} in {input_path}: {exc}"
            ) from exc
        test_cases.append(test_case)
    return test_cases


def _normalize_test_case(
    data: dict[str, object],
    *,
    operation_spec: OperationSpec,
    source_prompt_cls: type[Prompt],
) -> PersistedTestCase:
    """Validate one test case and normalize its prompt-specific field names.

    Arguments:
        data: serialized test case
        operation_spec: operation, manager, and base prompt configuration
        source_prompt_cls: prompt class defining the input JSON field names
    Returns:
        test case using base-prompt field names
    Raises:
        ScinoephileError: if the payload contains fields outside the prompt schema
    """
    manager_cls = operation_spec.manager_cls
    test_case_cls = manager_cls.get_test_case_cls_from_data(
        data,
        prompt_cls=source_prompt_cls,
    )
    _validate_payload_fields(data, test_case_cls)
    test_case = test_case_cls.model_validate(data, strict=True)
    base_test_case_cls = manager_cls.get_test_case_cls_with_prompt(
        test_case_cls,
        operation_spec.prompt_cls,
    )
    return PersistedTestCase.from_test_case(
        test_case,
        operation=operation_spec.operation,
        base_test_case_cls=base_test_case_cls,
    )


def _validate_json_object(data: object) -> dict[str, object]:
    """Validate top-level serialized test-case structure.

    Arguments:
        data: raw JSON test-case value
    Returns:
        validated test-case dictionary
    Raises:
        ScinoephileError: if the serialized test case has an invalid shape
    """
    if not isinstance(data, dict):
        raise ScinoephileError("Each optimization test case must be an object.")
    allowed_fields = {"answer", "difficulty", "prompt", "query", "verified"}
    unexpected_fields = sorted(set(data) - allowed_fields)
    if unexpected_fields:
        fields = ", ".join(str(field) for field in unexpected_fields)
        raise ScinoephileError(
            f"Optimization test case contains unexpected fields: {fields}."
        )
    return cast("dict[str, object]", data)


def _validate_payload_fields(
    data: dict[str, object],
    test_case_cls: type[TestCase],
):
    """Reject query or answer fields outside a concrete prompt schema.

    Arguments:
        data: serialized test case
        test_case_cls: concrete prompt test-case class
    Raises:
        ScinoephileError: if query or answer fields are not in the schema
    """
    for payload_name, model_cls in (
        ("query", test_case_cls.query_cls),
        ("answer", test_case_cls.answer_cls),
    ):
        payload = data[payload_name]
        if not isinstance(payload, dict):
            raise ScinoephileError(
                f"Optimization test case {payload_name} must be a JSON object."
            )
        unexpected_fields = sorted(set(payload) - set(model_cls.model_fields))
        if unexpected_fields:
            fields = ", ".join(str(field) for field in unexpected_fields)
            raise ScinoephileError(
                f"Optimization test case {payload_name} contains fields outside "
                f"the prompt schema: {fields}."
            )
