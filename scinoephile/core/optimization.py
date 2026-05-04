#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core optimization persistence utilities."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

from scinoephile.common.validation import val_output_path

from .exceptions import ScinoephileError
from .llms import Answer, Query, TestCase

__all__ = [
    "PersistedTestCase",
    "SyncReport",
    "TestCaseSqliteStore",
    "get_prefixed_payload",
    "get_test_case_id",
    "get_unprefixed_payload",
]

logger = getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PersistedTestCase:
    """A persisted test case row loaded from SQLite."""

    test_case_id: str
    """Deterministic identifier derived from query+answer JSON."""
    difficulty: int
    """Difficulty level for filtering and prioritization."""
    prompt: bool
    """Whether the test case is included in the prompt."""
    verified: bool
    """Whether the test case answer has been verified."""
    query: dict
    """Query JSON."""
    answer: dict
    """Answer JSON."""
    source_paths: list[str]
    """Source JSON paths that contributed this test case."""

    @staticmethod
    def from_test_case(test_case: TestCase) -> PersistedTestCase:
        """Convert a loaded test case to its persisted representation.

        Arguments:
            test_case: loaded test case
        Returns:
            persisted test case
        """
        query_dict = test_case.query.model_dump()
        if test_case.answer is None:
            raise ScinoephileError("Optimization test cases must include an answer.")
        answer_dict = test_case.answer.model_dump()
        test_case_id = get_test_case_id(test_case.query, test_case.answer)
        return PersistedTestCase(
            test_case_id=test_case_id,
            difficulty=int(test_case.difficulty),
            prompt=bool(test_case.prompt),
            verified=bool(test_case.verified),
            query=query_dict,
            answer=answer_dict,
            source_paths=[],
        )


@dataclass(frozen=True, slots=True)
class SyncReport:
    """Summary of a sync operation."""

    table_name: str
    """SQLite table name that was synchronized."""
    input_paths: tuple[Path, ...]
    """Input JSON paths included in the sync run."""
    insert_ids: tuple[str, ...]
    """Test case identifiers that would be inserted/updated."""
    delete_ids: tuple[str, ...]
    """Test case identifiers whose link to an input path would be removed."""


class TestCaseSqliteStore:
    """SQLite schema, persistence, and lookup for test cases."""

    __test__ = False
    """Inform pytest not to collect this class as a test."""

    schema_version = 2
    """SQLite schema version."""

    def __init__(self, database_path: Path):
        """Initialize.

        Arguments:
            database_path: SQLite database path
        """
        self.database_path = val_output_path(database_path, exist_ok=True)

    def create_schema(self):
        """Create SQLite schema if needed."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
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
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
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
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            try:
                row = connection.execute(
                    f"""SELECT *
                        FROM {_quote_identifier(table_name)}
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
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                f"""SELECT t.*
                    FROM {_quote_identifier(table_name)} AS t
                    JOIN test_case_sources AS s
                      ON s.table_name = ?
                     AND s.test_case_id = t.test_case_id
                   WHERE s.source_path = ?
                   ORDER BY t.test_case_id""",
                (table_name, source_path),
            ).fetchall()
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
    ) -> tuple[list[PersistedTestCase], list[str]]:
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
            to-insert rows and to-delete test case IDs
        """
        desired_list = list(desired)
        desired_by_id = {tc.test_case_id: tc for tc in desired_list}
        desired_ids = set(desired_by_id)

        if not dry_run:
            self.create_schema()
            self.ensure_table(table_name)
        existing_ids = self._get_existing_source_test_case_ids(table_name, source_path)

        to_insert_ids = sorted(desired_ids - existing_ids)
        to_delete_ids = sorted(existing_ids - desired_ids)

        to_insert = [desired_by_id[i] for i in to_insert_ids]
        if dry_run:
            return (to_insert, to_delete_ids)

        self.upsert_table_test_cases(table_name, desired_list, source_path=source_path)

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

                for test_case_id in to_delete_ids:
                    row = cursor.execute(
                        """SELECT source_path
                           FROM test_case_sources
                           WHERE table_name = ?
                             AND test_case_id = ?
                           ORDER BY source_path""",
                        (table_name, test_case_id),
                    ).fetchall()
                    paths = [str(r[0]) for r in row]
                    if not paths:
                        cursor.execute(
                            f"DELETE FROM {_quote_identifier(table_name)} "
                            "WHERE test_case_id = ?",
                            (test_case_id,),
                        )
                connection.commit()

        return (to_insert, to_delete_ids)

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
                payload.update(get_prefixed_payload("query", tc.query))
                payload.update(get_prefixed_payload("answer", tc.answer))
                columns = tuple(payload)
                placeholders = ", ".join("?" for _ in columns)
                quoted_columns = ", ".join(_quote_identifier(c) for c in columns)
                updates = ", ".join(
                    f"{_quote_identifier(c)}=excluded.{_quote_identifier(c)}"
                    for c in columns
                    if c != "test_case_id"
                )
                cursor.execute(
                    f"""INSERT INTO {_quote_identifier(table_name)}(
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

    @staticmethod
    def _create_test_case_table(cursor: sqlite3.Cursor, table_name: str):
        """Create a test-case table if it does not exist.

        Arguments:
            cursor: SQLite cursor
            table_name: SQLite table name
        """
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {_quote_identifier(table_name)}(
                    test_case_id TEXT PRIMARY KEY,
                    difficulty INTEGER NOT NULL,
                    prompt INTEGER NOT NULL,
                    verified INTEGER NOT NULL
                )"""
        )

    @staticmethod
    def _ensure_test_case_columns(
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
                f"PRAGMA table_info({_quote_identifier(table_name)})"
            ).fetchall()
        }
        desired_columns = set[str]()
        for test_case in test_cases:
            desired_columns.update(get_prefixed_payload("query", test_case.query))
            desired_columns.update(get_prefixed_payload("answer", test_case.answer))
        for column in sorted(desired_columns - existing_columns):
            cursor.execute(
                f"ALTER TABLE {_quote_identifier(table_name)} "
                f"ADD COLUMN {_quote_identifier(column)}"
            )

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

    @staticmethod
    def _row_to_test_case(
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
        query = get_unprefixed_payload(row, "query")
        answer = get_unprefixed_payload(row, "answer")
        return PersistedTestCase(
            test_case_id=str(row["test_case_id"]),
            difficulty=int(row["difficulty"]),
            prompt=bool(row["prompt"]),
            verified=bool(row["verified"]),
            query=query,
            answer=answer,
            source_paths=TestCaseSqliteStore._get_source_paths_for_row(
                connection,
                table_name,
                str(row["test_case_id"]),
            ),
        )


def get_prefixed_payload(prefix: str, payload: dict) -> dict[str, object]:
    """Get a flat payload using table-column prefixes.

    Arguments:
        prefix: column prefix
        payload: payload to flatten
    Returns:
        flattened payload
    """
    return {
        f"{prefix}__{key}": _serialize_value(value)
        for key, value in sorted(payload.items())
    }


def get_test_case_id(query: Query, answer: Answer) -> str:
    """Compute canonical identifier for a test case.

    Arguments:
        query: query payload
        answer: answer payload
    Returns:
        deterministic hexadecimal identifier
    """
    query_json = json.dumps(
        query.model_dump(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    answer_json = json.dumps(
        answer.model_dump(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(f"{query_json}\n{answer_json}".encode()).hexdigest()
    return digest


def get_unprefixed_payload(row: sqlite3.Row, prefix: str) -> dict:
    """Get a nested payload from row columns matching a prefix.

    Arguments:
        row: SQLite row
        prefix: column prefix
    Returns:
        nested payload
    """
    column_prefix = f"{prefix}__"
    return {
        key.removeprefix(column_prefix): _deserialize_value(row[key])
        for key in row.keys()
        if key.startswith(column_prefix) and row[key] is not None
    }


def _deserialize_value(value: object) -> object:
    """Deserialize a value loaded from SQLite.

    Arguments:
        value: value loaded from SQLite
    Returns:
        deserialized value
    """
    if isinstance(value, str) and value.startswith(("[", "{")):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _quote_identifier(identifier: str) -> str:
    """Quote a SQLite identifier.

    Arguments:
        identifier: SQLite identifier
    Returns:
        quoted identifier
    """
    return '"' + identifier.replace('"', '""') + '"'


def _serialize_value(value: object) -> object:
    """Serialize a value for storage in SQLite.

    Arguments:
        value: value to serialize
    Returns:
        serialized value
    """
    if isinstance(value, dict | list):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return value
