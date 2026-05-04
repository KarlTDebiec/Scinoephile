#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""SQLite schema and persistence for LLM test cases."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from logging import getLogger
from pathlib import Path

from scinoephile.common.validation import val_output_path
from scinoephile.core.llms.operation_spec import OperationSpec
from scinoephile.core.optimization import (
    get_prefixed_payload,
    get_unprefixed_payload,
    quote_identifier,
)

from .persisted_test_case import PersistedTestCase

__all__ = ["TestCaseSqliteStore"]

logger = getLogger(__name__)


class TestCaseSqliteStore:
    """SQLite schema, persistence, and lookup for test cases."""

    __test__ = False
    """Inform pytest not to collect this class as a test."""

    schema_version = 2
    """SQLite schema version."""

    def __init__(
        self,
        database_path: Path,
        *,
        operation_spec: OperationSpec | None = None,
    ):
        """Initialize.

        Arguments:
            database_path: SQLite database path
            operation_spec: operation specification for operation-shaped payloads
        """
        self.database_path = val_output_path(
            database_path,
            exist_ok=True,
            create=False,
        )
        self.operation_spec = operation_spec
        self.list_fields = dict(operation_spec.list_fields if operation_spec else {})

    def create_schema(self):
        """Create SQLite schema if needed."""
        self.database_path = val_output_path(self.database_path, exist_ok=True)
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()
            cursor.execute(f"PRAGMA user_version={self.schema_version}")
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS test_case_sources(
                       table_name TEXT NOT NULL,
                       test_case_id TEXT NOT NULL,
                       source_path TEXT NOT NULL,
                       UNIQUE(table_name, test_case_id, source_path) ON CONFLICT IGNORE
                   )"""
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS test_case_sources_source_path "
                "ON test_case_sources(source_path)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS test_case_sources_table_name "
                "ON test_case_sources(table_name)"
            )
            connection.commit()

    def ensure_table(self, table_name: str):
        """Ensure a test case table exists.

        Arguments:
            table_name: SQLite table name
        """
        self.create_schema()
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()
            self._create_test_case_table(cursor, table_name)
            connection.commit()

    def get_test_case(
        self,
        table_name: str,
        test_case_id: str,
    ) -> PersistedTestCase | None:
        """Fetch a single test case row by ID.

        Arguments:
            table_name: SQLite table name
            test_case_id: test case identifier
        Returns:
            persisted test case, if present
        """
        if not self.database_path.exists():
            return None
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            try:
                row = connection.execute(
                    f"""SELECT *
                        FROM {quote_identifier(table_name)}
                        WHERE test_case_id = ?""",
                    (test_case_id,),
                ).fetchone()
            except sqlite3.OperationalError:
                return None
            if row is None:
                return None
            return self._row_to_test_case(connection, table_name, row)

    def get_test_cases_by_source_path(
        self,
        table_name: str,
        source_path: str,
    ) -> list[PersistedTestCase]:
        """Fetch test cases associated with a source path.

        Arguments:
            table_name: SQLite table name
            source_path: original JSON path recorded during import
        Returns:
            persisted test cases
        """
        if not self.database_path.exists():
            return []
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            try:
                rows = connection.execute(
                    f"""SELECT t.*
                        FROM {quote_identifier(table_name)} AS t
                        JOIN test_case_sources AS s
                          ON s.table_name = ?
                         AND s.test_case_id = t.test_case_id
                       WHERE s.source_path = ?
                       ORDER BY t.test_case_id""",
                    (table_name, source_path),
                ).fetchall()
            except sqlite3.OperationalError:
                return []
            return [self._row_to_test_case(connection, table_name, r) for r in rows]

    def list_source_paths(self, table_name: str) -> list[str]:
        """List source paths recorded for a table.

        Arguments:
            table_name: SQLite table name
        Returns:
            ordered source paths
        """
        if not self.database_path.exists():
            return []
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """SELECT DISTINCT source_path
                   FROM test_case_sources
                   WHERE table_name = ?
                   ORDER BY source_path""",
                (table_name,),
            ).fetchall()
        return [str(row[0]) for row in rows]

    def list_tables(self) -> list[str]:
        """List tables currently present in the database.

        Returns:
            ordered table names
        """
        if not self.database_path.exists():
            return []
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        return [str(row[0]) for row in rows]

    def sync_table_source_path(
        self,
        table_name: str,
        *,
        source_path: str,
        desired: Iterable[PersistedTestCase],
        dry_run: bool,
    ) -> tuple[list[PersistedTestCase], list[PersistedTestCase], list[str]]:
        """Synchronize a single source path group for a table.

        This enforces that the set of test cases associated with `source_path` in SQLite
        matches `desired`, by inserting missing rows/links and removing obsolete links.
        Rows that become orphaned are deleted.

        Arguments:
            table_name: SQLite table name
            source_path: source JSON path group to synchronize
            desired: desired test cases from this JSON file
            dry_run: if True, do not write; only compute planned changes
        Returns:
            to-insert rows, to-update rows, and to-delete test case IDs
        """
        desired_list = list(desired)
        desired_by_id = {tc.test_case_id: tc for tc in desired_list}
        desired_ids = set(desired_by_id)

        existing_ids = self._get_existing_source_test_case_ids(table_name, source_path)
        existing_by_id = self._get_test_cases_by_ids(table_name, desired_ids)

        to_insert_ids = sorted(desired_ids - existing_ids)
        to_update_ids = sorted(
            test_case_id
            for test_case_id in desired_ids
            if test_case_id in existing_by_id
            and self._get_merged_test_case(
                existing_by_id[test_case_id], desired_by_id[test_case_id]
            )
            != existing_by_id[test_case_id]
        )
        to_delete_ids = sorted(existing_ids - desired_ids)

        to_insert = [desired_by_id[i] for i in to_insert_ids]
        to_update = [desired_by_id[i] for i in to_update_ids]
        if dry_run:
            return (to_insert, to_update, to_delete_ids)

        if desired_list:
            self.upsert_table_test_cases(
                table_name, desired_list, source_path=source_path
            )

        if to_delete_ids:
            with sqlite3.connect(self.database_path) as connection:
                cursor = connection.cursor()
                cursor.executemany(
                    """DELETE FROM test_case_sources
                       WHERE table_name = ?
                         AND source_path = ?
                         AND test_case_id = ?""",
                    [
                        (table_name, source_path, test_case_id)
                        for test_case_id in to_delete_ids
                    ],
                )

                orphaned_ids = self._get_orphaned_test_case_ids(
                    cursor,
                    table_name,
                    to_delete_ids,
                )
                cursor.executemany(
                    f"DELETE FROM {quote_identifier(table_name)} "
                    "WHERE test_case_id = ?",
                    [(test_case_id,) for test_case_id in orphaned_ids],
                )
                connection.commit()

        return (to_insert, to_update, to_delete_ids)

    def upsert_table_test_cases(
        self,
        table_name: str,
        test_cases: Iterable[PersistedTestCase],
        *,
        source_path: str,
    ) -> int:
        """Upsert a collection of test cases into a table.

        Arguments:
            table_name: SQLite table name
            test_cases: test cases to upsert
            source_path: JSON path from which these cases were imported
        Returns:
            number of rows inserted or updated
        """
        self.create_schema()
        test_cases = list(test_cases)
        touched = 0
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()
            self._create_test_case_table(cursor, table_name)
            self._ensure_test_case_columns(cursor, table_name, test_cases)

            for tc in test_cases:
                existing = self._get_source_paths(cursor, table_name, tc.test_case_id)
                merged_sources = self._merge_source_paths(existing, tc.source_paths)
                if source_path not in merged_sources:
                    merged_sources.append(source_path)
                merged_sources = sorted(set(merged_sources))

                payload: dict[str, object] = {
                    "test_case_id": tc.test_case_id,
                    "difficulty": int(tc.difficulty),
                    "prompt": 1 if tc.prompt else 0,
                    "verified": 1 if tc.verified else 0,
                }
                payload.update(self._get_prefixed_payload("query", tc.query))
                payload.update(self._get_prefixed_payload("answer", tc.answer))
                columns = tuple(payload)
                placeholders = ", ".join("?" for _ in columns)
                quoted_columns = ", ".join(quote_identifier(c) for c in columns)
                updates = ", ".join(
                    self._get_upsert_update_clause(c)
                    for c in columns
                    if c != "test_case_id"
                )
                cursor.execute(
                    f"""INSERT INTO {quote_identifier(table_name)}(
                           {quoted_columns}
                       ) VALUES ({placeholders})
                       ON CONFLICT(test_case_id) DO UPDATE SET
                           {updates}""",
                    tuple(payload.values()),
                )
                touched += 1

                for sp in merged_sources:
                    cursor.execute(
                        """INSERT INTO test_case_sources(
                               table_name,
                               test_case_id,
                               source_path
                           ) VALUES (?, ?, ?)""",
                        (table_name, tc.test_case_id, sp),
                    )

            connection.commit()
        logger.info(f"Upserted {touched} rows into {table_name}")
        return touched

    def _get_existing_source_test_case_ids(
        self,
        table_name: str,
        source_path: str,
    ) -> set[str]:
        """Get test case IDs currently linked to a source path.

        Arguments:
            table_name: SQLite table name
            source_path: source JSON path group
        Returns:
            test case IDs
        """
        if not self.database_path.exists():
            return set()
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            try:
                rows = connection.execute(
                    """SELECT test_case_id
                       FROM test_case_sources
                       WHERE table_name = ?
                         AND source_path = ?""",
                    (table_name, source_path),
                ).fetchall()
            except sqlite3.OperationalError:
                return set()
        return {str(row["test_case_id"]) for row in rows}

    def _get_test_cases_by_ids(
        self,
        table_name: str,
        test_case_ids: Iterable[str],
    ) -> dict[str, PersistedTestCase]:
        """Get existing test cases by ID.

        Arguments:
            table_name: SQLite table name
            test_case_ids: test case identifiers
        Returns:
            mapping of test case IDs to persisted test cases
        """
        ids = tuple(sorted(set(test_case_ids)))
        if not ids or not self.database_path.exists():
            return {}
        placeholders = ", ".join("?" for _ in ids)
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            try:
                rows = connection.execute(
                    f"""SELECT *
                        FROM {quote_identifier(table_name)}
                        WHERE test_case_id IN ({placeholders})""",
                    ids,
                ).fetchall()
            except sqlite3.OperationalError:
                return {}
            test_cases = [
                self._row_to_test_case(connection, table_name, r) for r in rows
            ]
        return {tc.test_case_id: tc for tc in test_cases}

    @staticmethod
    def _create_test_case_table(cursor: sqlite3.Cursor, table_name: str):
        """Create a test-case table if it does not exist.

        Arguments:
            cursor: SQLite cursor
            table_name: SQLite table name
        """
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {quote_identifier(table_name)}(
                    test_case_id TEXT PRIMARY KEY,
                    difficulty INTEGER NOT NULL,
                    prompt INTEGER NOT NULL,
                    verified INTEGER NOT NULL
                )"""
        )

    def _ensure_test_case_columns(
        self,
        cursor: sqlite3.Cursor,
        table_name: str,
        test_cases: Iterable[PersistedTestCase],
    ):
        """Ensure query and answer payload columns exist.

        Arguments:
            cursor: SQLite cursor
            table_name: SQLite table name
            test_cases: test cases whose payload fields should be represented
        """
        existing_columns = {
            str(row[1])
            for row in cursor.execute(
                f"PRAGMA table_info({quote_identifier(table_name)})"
            ).fetchall()
        }
        desired_columns = set[str]()
        for test_case in test_cases:
            desired_columns.update(self._get_prefixed_payload("query", test_case.query))
            desired_columns.update(
                self._get_prefixed_payload("answer", test_case.answer)
            )
        for column in sorted(desired_columns - existing_columns):
            cursor.execute(
                f"ALTER TABLE {quote_identifier(table_name)} "
                f"ADD COLUMN {quote_identifier(column)}"
            )

    @staticmethod
    def _get_merged_test_case(
        existing: PersistedTestCase,
        incoming: PersistedTestCase,
    ) -> PersistedTestCase:
        """Merge incoming metadata into an existing persisted test case.

        Arguments:
            existing: persisted test case already stored
            incoming: persisted test case being upserted
        Returns:
            merged persisted test case
        """
        return PersistedTestCase(
            test_case_id=existing.test_case_id,
            difficulty=max(existing.difficulty, incoming.difficulty),
            prompt=existing.prompt or incoming.prompt,
            verified=existing.verified or incoming.verified,
            query=incoming.query,
            answer=incoming.answer,
            source_paths=TestCaseSqliteStore._merge_source_paths(
                existing.source_paths, incoming.source_paths
            ),
        )

    @staticmethod
    def _get_orphaned_test_case_ids(
        cursor: sqlite3.Cursor,
        table_name: str,
        test_case_ids: Iterable[str],
    ) -> list[str]:
        """Get test case IDs that no longer have source path links.

        Arguments:
            cursor: SQLite cursor
            table_name: SQLite table name
            test_case_ids: candidate test case identifiers
        Returns:
            orphaned test case identifiers
        """
        ids = tuple(sorted(set(test_case_ids)))
        if not ids:
            return []
        placeholders = ", ".join("?" for _ in ids)
        rows = cursor.execute(
            f"""SELECT DISTINCT test_case_id
                FROM test_case_sources
                WHERE table_name = ?
                  AND test_case_id IN ({placeholders})""",
            (table_name, *ids),
        ).fetchall()
        remaining_ids = {str(row[0]) for row in rows}
        return [
            test_case_id for test_case_id in ids if test_case_id not in remaining_ids
        ]

    def _get_prefixed_payload(self, prefix: str, payload: dict) -> dict[str, object]:
        """Get a flat payload using table-column prefixes.

        Arguments:
            prefix: column prefix
            payload: payload to flatten
        Returns:
            flattened payload
        """
        flattened = get_prefixed_payload(prefix, payload)
        for list_field, max_items in sorted(self.list_fields.items()):
            list_prefix, field_name = self._parse_list_field(list_field)
            if list_prefix != prefix:
                continue

            value = payload.get(field_name)
            if not isinstance(value, list):
                raise TypeError(
                    f"Configured list field {list_field} must contain a list."
                )
            if len(value) > max_items:
                raise ValueError(
                    f"Configured list field {list_field} supports at most "
                    f"{max_items} items, received {len(value)}."
                )

            flattened.pop(f"{prefix}__{field_name}", None)
            for idx in range(max_items):
                column = self._get_split_column_name(prefix, field_name, idx)
                if idx < len(value):
                    flattened[column] = value[idx]
                else:
                    flattened[column] = None
        return flattened

    @staticmethod
    def _get_source_paths(
        cursor: sqlite3.Cursor,
        table_name: str,
        test_case_id: str,
    ) -> list[str]:
        """Get source paths associated with a test case.

        Arguments:
            cursor: SQLite cursor
            table_name: SQLite table name
            test_case_id: test case identifier
        Returns:
            source paths associated with the test case
        """
        try:
            row = cursor.execute(
                """SELECT source_path
                   FROM test_case_sources
                   WHERE table_name = ?
                     AND test_case_id = ?
                   ORDER BY source_path""",
                (table_name, test_case_id),
            ).fetchall()
        except sqlite3.OperationalError:
            return []
        return [str(r[0]) for r in row]

    @staticmethod
    def _get_source_paths_for_row(
        connection: sqlite3.Connection,
        table_name: str,
        test_case_id: str,
    ) -> list[str]:
        """Get source paths associated with a row.

        Arguments:
            connection: SQLite connection
            table_name: SQLite table name
            test_case_id: test case identifier
        Returns:
            source paths associated with the row
        """
        try:
            rows = connection.execute(
                """SELECT source_path
                   FROM test_case_sources
                   WHERE table_name = ?
                     AND test_case_id = ?
                   ORDER BY source_path""",
                (table_name, test_case_id),
            ).fetchall()
        except sqlite3.OperationalError:
            return []
        return [str(row["source_path"]) for row in rows]

    @staticmethod
    def _get_upsert_update_clause(column: str) -> str:
        """Get an update clause for a SQLite upsert column.

        Arguments:
            column: SQLite column name
        Returns:
            update clause for a SQLite upsert
        """
        quoted_column = quote_identifier(column)
        if column in {"difficulty", "prompt", "verified"}:
            return f"{quoted_column}=max({quoted_column}, excluded.{quoted_column})"
        return f"{quoted_column}=excluded.{quoted_column}"

    @staticmethod
    def _get_split_column_name(prefix: str, field_name: str, idx: int) -> str:
        """Get a column name for a split list item.

        Arguments:
            prefix: column prefix
            field_name: list field name
            idx: zero-based list item index
        Returns:
            split column name
        """
        return f"{prefix}__{field_name}_{idx + 1:02d}"

    def _get_unprefixed_payload(self, row: sqlite3.Row, prefix: str) -> dict:
        """Get a nested payload from row columns matching a prefix.

        Arguments:
            row: SQLite row
            prefix: column prefix
        Returns:
            nested payload
        """
        payload = get_unprefixed_payload(row, prefix)
        row_keys = set(row.keys())
        for list_field, max_items in sorted(self.list_fields.items()):
            list_prefix, field_name = self._parse_list_field(list_field)
            if list_prefix != prefix:
                continue

            split_columns = [
                self._get_split_column_name(prefix, field_name, idx)
                for idx in range(max_items)
            ]
            if not any(column in row_keys for column in split_columns):
                continue

            values: list[object] = []
            for idx in range(max_items):
                split_key = f"{field_name}_{idx + 1:02d}"
                value = payload.pop(split_key, None)
                if value is not None:
                    values.append(value)
            payload[field_name] = values
        return payload

    @staticmethod
    def _merge_source_paths(existing: list[str], incoming: list[str]) -> list[str]:
        """Merge two source path lists.

        Arguments:
            existing: source paths already recorded
            incoming: source paths to add
        Returns:
            sorted merged source paths
        """
        merged = set(existing)
        merged.update(incoming)
        return sorted(merged)

    def _row_to_test_case(
        self,
        connection: sqlite3.Connection,
        table_name: str,
        row: sqlite3.Row,
    ) -> PersistedTestCase:
        """Convert a SQLite row to a persisted test case.

        Arguments:
            connection: SQLite connection
            table_name: SQLite table name
            row: SQLite row
        Returns:
            persisted test case
        """
        query = self._get_unprefixed_payload(row, "query")
        answer = self._get_unprefixed_payload(row, "answer")
        source_paths = TestCaseSqliteStore._get_source_paths_for_row(
            connection,
            table_name,
            str(row["test_case_id"]),
        )
        return PersistedTestCase(
            test_case_id=str(row["test_case_id"]),
            difficulty=int(row["difficulty"]),
            prompt=bool(row["prompt"]),
            verified=bool(row["verified"]),
            query=query,
            answer=answer,
            source_paths=source_paths,
        )

    @staticmethod
    def _parse_list_field(list_field: str) -> tuple[str, str]:
        """Parse a configured list field path.

        Arguments:
            list_field: configured list field path
        Returns:
            payload prefix and field name
        """
        parts = list_field.split(".", maxsplit=1)
        if len(parts) != 2 or parts[0] not in {"query", "answer"} or not parts[1]:
            raise ValueError(
                "Configured list fields must be formatted like "
                "'query.field_name' or 'answer.field_name'."
            )
        return (parts[0], parts[1])
