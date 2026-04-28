#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""SQLite schema and persistence for LLM test cases."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from logging import getLogger
from pathlib import Path

from scinoephile.common.validation import val_output_path

from .persisted_test_case import PersistedTestCase

__all__ = ["TestCaseSqliteStore"]

logger = getLogger(__name__)


class TestCaseSqliteStore:
    """SQLite schema, persistence, and lookup for test cases."""

    __test__ = False
    """Inform pytest not to collect this class as a test."""

    schema_version = 1

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
                    f"""SELECT
                            test_case_id,
                            difficulty,
                            prompt,
                            verified,
                            query,
                            answer,
                            source_paths
                        FROM {table_name}
                        WHERE test_case_id = ?""",
                    (test_case_id,),
                ).fetchone()
            except sqlite3.OperationalError:
                return None
            if row is None:
                return None
            return self._row_to_test_case(row)

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
                f"""SELECT
                        t.test_case_id,
                        t.difficulty,
                        t.prompt,
                        t.verified,
                        t.query,
                        t.answer,
                        t.source_paths
                    FROM {table_name} AS t
                    JOIN test_case_sources AS s
                      ON s.table_name = ?
                     AND s.test_case_id = t.test_case_id
                   WHERE s.source_path = ?
                   ORDER BY t.test_case_id""",
                (table_name, source_path),
            ).fetchall()
        return [self._row_to_test_case(r) for r in rows]

    def list_tables(self) -> list[str]:
        """List tables currently present in the database."""
        if not self.database_path.exists():
            return []
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        return [str(row[0]) for row in rows]

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
        touched = 0
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()
            self._create_test_case_table(cursor, table_name)

            for tc in test_cases:
                existing = self._get_source_paths(cursor, table_name, tc.test_case_id)
                merged_sources = self._merge_source_paths(existing, tc.source_paths)
                if source_path not in merged_sources:
                    merged_sources.append(source_path)
                merged_sources = sorted(set(merged_sources))

                cursor.execute(
                    f"""INSERT INTO {table_name}(
                           test_case_id,
                           difficulty,
                           prompt,
                           verified,
                           query,
                           answer,
                           source_paths
                       ) VALUES (?, ?, ?, ?, ?, ?, ?)
                       ON CONFLICT(test_case_id) DO UPDATE SET
                           difficulty=excluded.difficulty,
                           prompt=excluded.prompt,
                           verified=excluded.verified,
                           query=excluded.query,
                           answer=excluded.answer,
                           source_paths=excluded.source_paths""",
                    (
                        tc.test_case_id,
                        int(tc.difficulty),
                        1 if tc.prompt else 0,
                        1 if tc.verified else 0,
                        json.dumps(tc.query, ensure_ascii=False, separators=(",", ":")),
                        json.dumps(
                            tc.answer,
                            ensure_ascii=False,
                            separators=(",", ":"),
                        ),
                        json.dumps(
                            merged_sources,
                            ensure_ascii=False,
                            separators=(",", ":"),
                        ),
                    ),
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
            (to_insert, to_delete_ids) where:
              - to_insert are rows that would be inserted/updated to add this source
                link
              - to_delete_ids are test_case_id values whose link to this source would be
                removed
        """
        self.create_schema()
        self.ensure_table(table_name)

        desired_list = list(desired)
        desired_by_id = {tc.test_case_id: tc for tc in desired_list}
        desired_ids = set(desired_by_id)

        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            existing_ids_rows = connection.execute(
                """SELECT test_case_id
                   FROM test_case_sources
                   WHERE table_name = ?
                     AND source_path = ?""",
                (table_name, source_path),
            ).fetchall()
            existing_ids = {str(r["test_case_id"]) for r in existing_ids_rows}

        to_insert_ids = sorted(desired_ids - existing_ids)
        to_delete_ids = sorted(existing_ids - desired_ids)

        to_insert = [desired_by_id[i] for i in to_insert_ids]
        if dry_run:
            return (to_insert, to_delete_ids)

        # Apply inserts/updates (also ensures source link present)
        self.upsert_table_test_cases(table_name, desired_list, source_path=source_path)

        # Apply deletions: remove source link, then prune orphaned rows.
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
                        f"SELECT source_paths FROM {table_name} WHERE test_case_id = ?",
                        (test_case_id,),
                    ).fetchone()
                    if row is None or row[0] is None:
                        continue
                    paths = json.loads(str(row[0]))
                    if isinstance(paths, list):
                        paths = [str(x) for x in paths if str(x) != source_path]
                    else:
                        paths = []
                    if not paths:
                        cursor.execute(
                            f"DELETE FROM {table_name} WHERE test_case_id = ?",
                            (test_case_id,),
                        )
                    else:
                        cursor.execute(
                            f"UPDATE {table_name} SET source_paths = ? "
                            "WHERE test_case_id = ?",
                            (
                                json.dumps(
                                    paths,
                                    ensure_ascii=False,
                                    separators=(",", ":"),
                                ),
                                test_case_id,
                            ),
                        )
                connection.commit()

        return (to_insert, to_delete_ids)

    @staticmethod
    def _create_test_case_table(cursor: sqlite3.Cursor, table_name: str):
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {table_name}(
                    test_case_id TEXT PRIMARY KEY,
                    difficulty INTEGER NOT NULL,
                    prompt INTEGER NOT NULL,
                    verified INTEGER NOT NULL,
                    query TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    source_paths TEXT NOT NULL
                )"""
        )

    @staticmethod
    def _get_source_paths(
        cursor: sqlite3.Cursor,
        table_name: str,
        test_case_id: str,
    ) -> list[str]:
        try:
            row = cursor.execute(
                f"SELECT source_paths FROM {table_name} WHERE test_case_id = ?",
                (test_case_id,),
            ).fetchone()
        except sqlite3.OperationalError:
            return []
        if row is None or row[0] is None:
            return []
        try:
            parsed = json.loads(str(row[0]))
        except json.JSONDecodeError:
            return []
        if not isinstance(parsed, list):
            return []
        return [str(x) for x in parsed]

    @staticmethod
    def _merge_source_paths(existing: list[str], incoming: list[str]) -> list[str]:
        merged = set(existing)
        merged.update(incoming)
        return sorted(merged)

    @staticmethod
    def _row_to_test_case(row: sqlite3.Row) -> PersistedTestCase:
        query = json.loads(str(row["query"]))
        answer = json.loads(str(row["answer"]))
        source_paths = json.loads(str(row["source_paths"]))
        return PersistedTestCase(
            test_case_id=str(row["test_case_id"]),
            difficulty=int(row["difficulty"]),
            prompt=bool(row["prompt"]),
            verified=bool(row["verified"]),
            query=query,
            answer=answer,
            source_paths=[str(x) for x in source_paths],
        )
