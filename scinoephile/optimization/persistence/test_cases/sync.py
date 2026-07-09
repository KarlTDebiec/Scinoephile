#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""JSON to SQLite synchronization for LLM test cases."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from scinoephile.core.exceptions import ScinoephileError

from .persisted_test_case import PersistedTestCase
from .sqlite_store import TestCaseSqliteStore
from .sync_report import SyncReport

__all__ = ["sync_test_cases_from_json_paths"]


def sync_test_cases_from_json_paths(
    *,
    database_path: Path,
    operation: str,
    variant: str,
    input_paths: Iterable[Path],
    dry_run: bool,
) -> SyncReport:
    """Synchronize test cases from JSON files into SQLite.

    All input files are loaded and validated before the database is modified.

    Arguments:
        database_path: SQLite database path
        operation: operation to which the test cases belong
        variant: stable schema variant within the operation
        input_paths: JSON paths to import or synchronize
        dry_run: if True, report planned changes without writing
    Returns:
        sync report
    """
    input_paths_tuple = tuple(input_path.resolve() for input_path in input_paths)
    source_test_cases = {
        str(input_path): _load_test_cases(
            input_path,
            operation=operation,
            variant=variant,
        )
        for input_path in input_paths_tuple
    }

    store = TestCaseSqliteStore(database_path)
    to_insert, to_update, to_delete = store.sync_source_paths(
        source_test_cases,
        dry_run=dry_run,
    )
    return SyncReport(
        operation=operation,
        variant=variant,
        input_paths=input_paths_tuple,
        insert_ids=tuple(sorted({test_case.test_case_id for test_case in to_insert})),
        update_ids=tuple(sorted({test_case.test_case_id for test_case in to_update})),
        delete_ids=tuple(sorted(set(to_delete))),
    )


def _load_test_cases(
    input_path: Path,
    *,
    operation: str,
    variant: str,
) -> list[PersistedTestCase]:
    """Load and structurally validate persisted test cases from JSON.

    Arguments:
        input_path: path to a JSON test-case array
        operation: operation to which the test cases belong
        variant: stable schema variant within the operation
    Returns:
        persisted test cases
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

    test_cases: list[PersistedTestCase] = []
    for index, item in enumerate(data, start=1):
        try:
            test_case = PersistedTestCase.from_json_data(
                item,
                operation=operation,
                variant=variant,
            )
        except ScinoephileError as exc:
            raise ScinoephileError(
                f"Invalid optimization test case {index} in {input_path}: {exc}"
            ) from exc
        test_cases.append(test_case)
    return test_cases
