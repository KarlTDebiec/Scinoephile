#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""JSON to SQLite synchronization for LLM test cases."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import cast

from pydantic import ValidationError

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.llms import OperationSpec, Prompt, TestCase

from .persisted_test_case import PersistedTestCase
from .sqlite_store import TestCaseSqliteStore
from .sync_report import SyncReport

__all__ = ["sync_test_cases_from_json_paths"]


def sync_test_cases_from_json_paths(
    *,
    database_path: Path,
    operation_spec: OperationSpec,
    input_paths: Iterable[Path],
    dry_run: bool,
) -> SyncReport:
    """Synchronize test cases from JSON files into SQLite.

    Concrete prompt field names are detected and normalized to the base prompt's
    field names before test-case IDs are computed. All input files are loaded and
    validated before the database is modified.

    Arguments:
        database_path: SQLite database path
        operation_spec: operation, manager, and base prompt configuration
        input_paths: JSON paths to import or synchronize
        dry_run: if True, report planned changes without writing
    Returns:
        sync report
    """
    input_paths_tuple = tuple(input_path.resolve() for input_path in input_paths)
    source_test_cases = {
        str(input_path): _load_test_cases(input_path, operation_spec=operation_spec)
        for input_path in input_paths_tuple
    }

    store = TestCaseSqliteStore(database_path)
    to_insert, to_update, to_delete = store.sync_source_paths(
        source_test_cases,
        dry_run=dry_run,
    )
    return SyncReport(
        operation=operation_spec.operation,
        input_paths=input_paths_tuple,
        insert_ids=tuple(sorted({test_case.test_case_id for test_case in to_insert})),
        update_ids=tuple(sorted({test_case.test_case_id for test_case in to_update})),
        delete_ids=tuple(sorted(set(to_delete))),
    )


def _get_prompt_classes(base_prompt_cls: type[Prompt]) -> tuple[type[Prompt], ...]:
    """Get a base prompt class and all currently loaded descendants.

    Arguments:
        base_prompt_cls: base correspondence schema for an operation
    Returns:
        prompt classes in deterministic order
    """
    prompt_classes = {base_prompt_cls}
    pending = [base_prompt_cls]
    while pending:
        prompt_cls = pending.pop()
        for subclass in prompt_cls.__subclasses__():
            if subclass not in prompt_classes:
                prompt_classes.add(subclass)
                pending.append(subclass)
    return tuple(
        sorted(
            prompt_classes,
            key=lambda prompt_cls: f"{prompt_cls.__module__}.{prompt_cls.__qualname__}",
        )
    )


def _get_source_prompt_cls(
    data: dict[str, object],
    operation_spec: OperationSpec,
) -> type[Prompt]:
    """Detect a concrete prompt schema from one serialized test case.

    Multiple prompt classes may use the same fields. They are considered equivalent
    when they produce the same base-prompt-normalized payload.

    Arguments:
        data: serialized test case
        operation_spec: operation, manager, and base prompt configuration
    Returns:
        detected prompt class
    Raises:
        ScinoephileError: if no schema matches or matches normalize differently
    """
    matches: list[tuple[type[Prompt], PersistedTestCase]] = []
    for prompt_cls in _get_prompt_classes(operation_spec.prompt_cls):
        try:
            persisted = _normalize_test_case(
                data,
                operation_spec=operation_spec,
                prompt_cls=prompt_cls,
            )
        except (AttributeError, KeyError, ScinoephileError, TypeError, ValidationError):
            continue
        matches.append((prompt_cls, persisted))

    if not matches:
        raise ScinoephileError(
            "Test case does not match any loaded prompt correspondence schema for "
            f"operation {operation_spec.operation}."
        )
    normalized_payloads = {
        (
            json.dumps(persisted.query, ensure_ascii=False, sort_keys=True),
            json.dumps(persisted.answer, ensure_ascii=False, sort_keys=True),
        )
        for _, persisted in matches
    }
    if len(normalized_payloads) != 1:
        prompt_names = ", ".join(prompt_cls.__name__ for prompt_cls, _ in matches)
        raise ScinoephileError(
            "Test case ambiguously matches prompt schemas that normalize "
            f"differently: {prompt_names}."
        )
    return matches[0][0]


def _load_test_cases(
    input_path: Path,
    *,
    operation_spec: OperationSpec,
) -> list[PersistedTestCase]:
    """Load, validate, and normalize persisted test cases from JSON.

    Arguments:
        input_path: path to a JSON test-case array
        operation_spec: operation, manager, and base prompt configuration
    Returns:
        persisted test cases using base-prompt field names
    Raises:
        ScinoephileError: if the file cannot be loaded or has an invalid shape
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
    if not data:
        return []

    try:
        first_item = _validate_json_object(data[0], operation_spec.operation)
        prompt_cls = _get_source_prompt_cls(first_item, operation_spec)
    except ScinoephileError as exc:
        raise ScinoephileError(
            f"Invalid optimization test case 1 in {input_path}: {exc}"
        ) from exc

    test_cases: list[PersistedTestCase] = []
    for index, item in enumerate(data, start=1):
        try:
            item_dict = _validate_json_object(item, operation_spec.operation)
            test_case = _normalize_test_case(
                item_dict,
                operation_spec=operation_spec,
                prompt_cls=prompt_cls,
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
    prompt_cls: type[Prompt],
) -> PersistedTestCase:
    """Validate one test case and normalize its prompt-specific field names.

    Arguments:
        data: serialized test case
        operation_spec: operation, manager, and base prompt configuration
        prompt_cls: concrete prompt schema used by the serialized payload
    Returns:
        test case using base-prompt field names
    Raises:
        ScinoephileError: if the payload contains fields outside the prompt schema
    """
    manager_cls = operation_spec.manager_cls
    test_case_cls = manager_cls.get_test_case_cls_from_data(
        data,
        prompt_cls=prompt_cls,
    )
    _validate_payload_fields(data, test_case_cls)
    test_case = test_case_cls.model_validate(data)
    base_test_case_cls = manager_cls.get_test_case_cls_with_prompt(
        test_case_cls,
        operation_spec.prompt_cls,
    )
    return PersistedTestCase.from_test_case(
        test_case,
        operation=operation_spec.operation,
        base_test_case_cls=base_test_case_cls,
    )


def _validate_json_object(data: object, operation: str) -> dict[str, object]:
    """Validate top-level serialized test-case structure.

    Arguments:
        data: raw JSON test-case value
        operation: operation used for structural validation
    Returns:
        validated test-case dictionary
    Raises:
        ScinoephileError: if the serialized test case has an invalid shape
    """
    PersistedTestCase.from_json_data(data, operation=operation)
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
