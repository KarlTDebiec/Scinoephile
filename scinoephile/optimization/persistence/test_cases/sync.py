#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""JSON ↔ SQLite synchronization for LLM test cases."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from scinoephile.core.llms import OperationSpec, TestCase
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.core.optimization import (
    PersistedTestCase,
    SyncReport,
    TestCaseSqliteStore,
)

__all__ = [
    "SyncReport",
    "sync_test_cases_from_json_paths",
]


def sync_test_cases_from_json_paths(
    *,
    database_path: Path,
    operation_spec: OperationSpec,
    input_paths: Iterable[Path],
    dry_run: bool,
) -> SyncReport:
    """Synchronize test cases from JSON files into SQLite.

    Arguments:
        database_path: SQLite database path
        operation_spec: operation specification
        input_paths: JSON paths to import/sync
        dry_run: if True, report planned changes without writing
    Returns:
        sync report
    """
    store = TestCaseSqliteStore(database_path)

    input_paths_tuple = tuple(input_paths)
    insert_ids: list[str] = []
    delete_ids: list[str] = []
    for input_path in input_paths_tuple:
        loaded: list[TestCase] = load_test_cases_from_json(
            input_path,
            operation_spec.manager_cls,
            prompt_cls=operation_spec.prompt_cls,
        )
        persisted = [PersistedTestCase.from_test_case(tc) for tc in loaded]
        to_insert, to_delete = store.sync_table_source_path(
            operation_spec.test_case_table_name,
            source_path=str(input_path),
            desired=persisted,
            dry_run=dry_run,
        )
        insert_ids.extend([tc.test_case_id for tc in to_insert])
        delete_ids.extend(to_delete)

    return SyncReport(
        table_name=operation_spec.test_case_table_name,
        input_paths=input_paths_tuple,
        insert_ids=tuple(sorted(set(insert_ids))),
        delete_ids=tuple(sorted(set(delete_ids))),
    )
