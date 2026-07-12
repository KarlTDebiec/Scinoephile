#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""JSON to SQLite synchronization for LLM test cases."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.llms import Manager
from scinoephile.core.llms.utils import load_test_cases_from_json

from .persisted_test_case import PersistedTestCase
from .sqlite_store import TestCaseSqliteStore

__all__ = [
    "SyncReport",
    "sync_test_cases",
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


def sync_test_cases(
    input_paths: Iterable[Path],
    output_path: Path,
    manager_cls: type[Manager],
    *,
    dry_run: bool,
) -> SyncReport:
    """Synchronize test cases from JSON files into SQLite.

    All input files are loaded and validated before the database is modified.

    Arguments:
        input_paths: JSON paths to import or synchronize
        output_path: SQLite database output path
        manager_cls: manager defining the operation and base prompt
        dry_run: if True, report planned changes without writing
    Returns:
        sync report
    """
    input_paths_tuple = tuple(input_path.resolve() for input_path in input_paths)
    source_test_cases = {
        str(input_path): _load_test_cases(
            input_path,
            manager_cls,
        )
        for input_path in input_paths_tuple
    }

    store = TestCaseSqliteStore(output_path)
    insert_ids, delete_ids = store.sync_source_paths(
        source_test_cases,
        manager_cls=manager_cls,
        dry_run=dry_run,
    )
    return SyncReport(
        operation=manager_cls.operation,
        input_paths=input_paths_tuple,
        insert_ids=tuple(sorted(insert_ids)),
        delete_ids=tuple(sorted(delete_ids)),
    )


def _load_test_cases(
    input_path: Path,
    manager_cls: type[Manager],
) -> list[PersistedTestCase]:
    """Load, validate, and normalize persisted test cases from JSON.

    Arguments:
        input_path: path to a JSON test-case array
        manager_cls: manager defining the operation and base prompt
    Returns:
        persisted test cases using base-prompt field names
    Raises:
        ScinoephileError: if the file cannot be loaded or contains an invalid case
    """
    try:
        test_cases = load_test_cases_from_json(
            input_path,
            manager_cls,
            manager_cls.base_prompt,
        )
        return [
            PersistedTestCase.from_test_case(test_case, manager_cls)
            for test_case in test_cases
        ]
    except (OSError, ScinoephileError, TypeError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to load optimization test cases from {input_path}: {exc}"
        ) from exc
