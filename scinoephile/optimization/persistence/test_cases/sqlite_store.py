#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""SQLite schema and persistence for LLM test cases."""

from __future__ import annotations

from collections.abc import Iterable
from logging import getLogger
from pathlib import Path

from sqlalchemy import (
    Column,
    Index,
    Integer,
    MetaData,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    func,
    inspect,
    select,
    text,
)
from sqlalchemy.dialects.sqlite import Insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import URL, Connection, RowMapping
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import NullPool

from scinoephile.common.validation import val_output_path
from scinoephile.core.llms.operation_spec import OperationSpec
from scinoephile.core.optimization import get_prefixed_payload, get_unprefixed_payload

from .persisted_test_case import PersistedTestCase

__all__ = ["TestCaseSqliteStore"]

logger = getLogger(__name__)


class TestCaseSqliteStore:
    """SQLite schema, persistence, and lookup for test cases."""

    __test__ = False
    """Inform pytest not to collect this class as a test."""

    schema_version = 2
    """SQLite schema version."""

    _metadata = MetaData()
    """SQLAlchemy Core metadata for this store's fixed schema objects."""

    _test_case_sources = Table(
        "test_case_sources",
        _metadata,
        Column("table_name", Text, nullable=False),
        Column("test_case_id", Text, nullable=False),
        Column("source_path", Text, nullable=False),
        UniqueConstraint(
            "table_name",
            "test_case_id",
            "source_path",
            sqlite_on_conflict="IGNORE",
        ),
        Index("test_case_sources_source_path", "source_path"),
        Index("test_case_sources_table_name", "table_name"),
    )
    """Source-link table shared by all dynamic test case tables."""

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
        if operation_spec:
            self.list_fields = dict(operation_spec.list_fields)
        else:
            self.list_fields = {}
        self.engine = create_engine(
            URL.create("sqlite", database=str(self.database_path)),
            future=True,
            poolclass=NullPool,
        )

    def create_schema(self):
        """Create SQLite schema if needed."""
        self.database_path = val_output_path(self.database_path, exist_ok=True)
        with self.engine.begin() as connection:
            connection.execute(text(f"PRAGMA user_version={self.schema_version}"))
            self._test_case_sources.create(connection, checkfirst=True)

    def ensure_table(self, table_name: str):
        """Ensure a test case table exists.

        Arguments:
            table_name: SQLite table name
        """
        self.create_schema()
        with self.engine.begin() as connection:
            self._create_test_case_table(connection, table_name)

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
        with self.engine.connect() as connection:
            table = self._get_test_case_table(table_name, connection=connection)
            try:
                row = (
                    connection.execute(
                        select(table).where(table.c.test_case_id == test_case_id)
                    )
                    .mappings()
                    .first()
                )
            except OperationalError:
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
        with self.engine.connect() as connection:
            table = self._get_test_case_table(table_name, connection=connection)
            try:
                rows = (
                    connection.execute(
                        select(table)
                        .join(
                            self._test_case_sources,
                            (self._test_case_sources.c.table_name == table_name)
                            & (
                                self._test_case_sources.c.test_case_id
                                == table.c.test_case_id
                            ),
                        )
                        .where(self._test_case_sources.c.source_path == source_path)
                        .order_by(table.c.test_case_id)
                    )
                    .mappings()
                    .all()
                )
            except OperationalError:
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
        with self.engine.connect() as connection:
            try:
                rows = (
                    connection.execute(
                        select(self._test_case_sources.c.source_path)
                        .distinct()
                        .where(self._test_case_sources.c.table_name == table_name)
                        .order_by(self._test_case_sources.c.source_path)
                    )
                    .scalars()
                    .all()
                )
            except OperationalError:
                return []
        return [str(row) for row in rows]

    def list_tables(self) -> list[str]:
        """List tables currently present in the database.

        Returns:
            ordered table names
        """
        if not self.database_path.exists():
            return []
        return sorted(inspect(self.engine).get_table_names())

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
            table = self._get_test_case_table(table_name)
            with self.engine.begin() as connection:
                connection.execute(
                    self._test_case_sources.delete().where(
                        (self._test_case_sources.c.table_name == table_name)
                        & (self._test_case_sources.c.source_path == source_path)
                        & (self._test_case_sources.c.test_case_id.in_(to_delete_ids))
                    )
                )
                orphaned_ids = self._get_orphaned_test_case_ids(
                    connection,
                    table_name,
                    to_delete_ids,
                )
                connection.execute(
                    table.delete().where(table.c.test_case_id.in_(orphaned_ids))
                )

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
        with self.engine.begin() as connection:
            self._create_test_case_table(connection, table_name)
            self._ensure_test_case_columns(connection, table_name, test_cases)
            table = self._get_test_case_table(table_name, connection=connection)

            for tc in test_cases:
                existing = self._get_source_paths(
                    connection, table_name, tc.test_case_id
                )
                merged_sources = self._merge_source_paths(existing, tc.source_paths)
                if source_path not in merged_sources:
                    merged_sources.append(source_path)
                merged_sources = sorted(set(merged_sources))

                payload: dict[str, object] = {
                    "test_case_id": tc.test_case_id,
                    "difficulty": int(tc.difficulty),
                    "prompt": int(tc.prompt),
                    "verified": int(tc.verified),
                }
                payload.update(self._get_prefixed_payload("query", tc.query))
                payload.update(self._get_prefixed_payload("answer", tc.answer))
                insert_statement = sqlite_insert(table).values(payload)
                connection.execute(
                    insert_statement.on_conflict_do_update(
                        index_elements=[table.c.test_case_id],
                        set_=self._get_upsert_update_values(
                            table, insert_statement, payload
                        ),
                    )
                )
                touched += 1

                for sp in merged_sources:
                    connection.execute(
                        sqlite_insert(self._test_case_sources)
                        .values(
                            table_name=table_name,
                            test_case_id=tc.test_case_id,
                            source_path=sp,
                        )
                        .on_conflict_do_nothing()
                    )
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
        with self.engine.connect() as connection:
            try:
                rows = (
                    connection.execute(
                        select(self._test_case_sources.c.test_case_id).where(
                            (self._test_case_sources.c.table_name == table_name)
                            & (self._test_case_sources.c.source_path == source_path)
                        )
                    )
                    .scalars()
                    .all()
                )
            except OperationalError:
                return set()
        return {str(row) for row in rows}

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
        with self.engine.connect() as connection:
            table = self._get_test_case_table(table_name, connection=connection)
            try:
                rows = (
                    connection.execute(
                        select(table).where(table.c.test_case_id.in_(ids))
                    )
                    .mappings()
                    .all()
                )
            except OperationalError:
                return {}
            test_cases = [
                self._row_to_test_case(connection, table_name, r) for r in rows
            ]
        return {tc.test_case_id: tc for tc in test_cases}

    def _ensure_test_case_columns(
        self,
        connection: Connection,
        table_name: str,
        test_cases: Iterable[PersistedTestCase],
    ):
        """Ensure query and answer payload columns exist.

        Arguments:
            connection: SQLAlchemy connection
            table_name: SQLite table name
            test_cases: test cases whose payload fields should be represented
        """
        existing_columns = {
            str(column["name"])
            for column in inspect(connection).get_columns(table_name)
        }
        desired_columns = set[str]()
        for test_case in test_cases:
            desired_columns.update(self._get_prefixed_payload("query", test_case.query))
            desired_columns.update(
                self._get_prefixed_payload("answer", test_case.answer)
            )
        for column in sorted(desired_columns - existing_columns):
            preparer = connection.dialect.identifier_preparer
            connection.execute(
                text(
                    f"ALTER TABLE {preparer.quote(table_name)} "
                    f"ADD COLUMN {preparer.quote(column)}"
                )
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
        connection: Connection,
        table_name: str,
        test_case_ids: Iterable[str],
    ) -> list[str]:
        """Get test case IDs that no longer have source path links.

        Arguments:
            connection: SQLAlchemy connection
            table_name: SQLite table name
            test_case_ids: candidate test case identifiers
        Returns:
            orphaned test case identifiers
        """
        ids = tuple(sorted(set(test_case_ids)))
        if not ids:
            return []
        rows = (
            connection.execute(
                select(TestCaseSqliteStore._test_case_sources.c.test_case_id)
                .distinct()
                .where(
                    (TestCaseSqliteStore._test_case_sources.c.table_name == table_name)
                    & (TestCaseSqliteStore._test_case_sources.c.test_case_id.in_(ids))
                )
            )
            .scalars()
            .all()
        )
        remaining_ids = {str(row) for row in rows}
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

    def _get_unprefixed_payload(self, row: RowMapping, prefix: str) -> dict:
        """Get a nested payload from row columns matching a prefix.

        Arguments:
            row: SQLAlchemy row mapping
            prefix: column prefix
        Returns:
            nested payload
        """
        payload = get_unprefixed_payload(dict(row), prefix)
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

    def _row_to_test_case(
        self,
        connection: Connection,
        table_name: str,
        row: RowMapping,
    ) -> PersistedTestCase:
        """Convert a SQLAlchemy row mapping to a persisted test case.

        Arguments:
            connection: SQLAlchemy connection
            table_name: SQLite table name
            row: SQLAlchemy row mapping
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
    def _create_test_case_table(connection: Connection, table_name: str):
        """Create a test-case table if it does not exist.

        Arguments:
            connection: SQLAlchemy connection
            table_name: SQLite table name
        """
        TestCaseSqliteStore._get_test_case_table(table_name).create(
            connection, checkfirst=True
        )

    @staticmethod
    def _get_source_paths(
        connection: Connection,
        table_name: str,
        test_case_id: str,
    ) -> list[str]:
        """Get source paths associated with a test case.

        Arguments:
            connection: SQLAlchemy connection
            table_name: SQLite table name
            test_case_id: test case identifier
        Returns:
            source paths associated with the test case
        """
        try:
            rows = (
                connection.execute(
                    select(TestCaseSqliteStore._test_case_sources.c.source_path)
                    .where(
                        (
                            TestCaseSqliteStore._test_case_sources.c.table_name
                            == table_name
                        )
                        & (
                            TestCaseSqliteStore._test_case_sources.c.test_case_id
                            == test_case_id
                        )
                    )
                    .order_by(TestCaseSqliteStore._test_case_sources.c.source_path)
                )
                .scalars()
                .all()
            )
        except OperationalError:
            return []
        return [str(row) for row in rows]

    @staticmethod
    def _get_source_paths_for_row(
        connection: Connection,
        table_name: str,
        test_case_id: str,
    ) -> list[str]:
        """Get source paths associated with a row.

        Arguments:
            connection: SQLAlchemy connection
            table_name: SQLite table name
            test_case_id: test case identifier
        Returns:
            source paths associated with the row
        """
        return TestCaseSqliteStore._get_source_paths(
            connection, table_name, test_case_id
        )

    @staticmethod
    def _get_test_case_table(
        table_name: str,
        *,
        connection: Connection | None = None,
    ) -> Table:
        """Get SQLAlchemy Core table metadata for a test case table.

        Arguments:
            table_name: SQLite table name
            connection: optional connection used to reflect existing columns
        Returns:
            test case table
        """
        table_metadata = MetaData()
        if connection is not None and inspect(connection).has_table(table_name):
            return Table(table_name, table_metadata, autoload_with=connection)

        table = Table(
            table_name,
            table_metadata,
            Column("test_case_id", Text, primary_key=True),
            Column("difficulty", Integer, nullable=False),
            Column("prompt", Integer, nullable=False),
            Column("verified", Integer, nullable=False),
        )
        return table

    @staticmethod
    def _get_upsert_update_values(
        table: Table,
        insert_statement: Insert,
        payload: dict[str, object],
    ) -> dict:
        """Get update values for a SQLite upsert.

        Arguments:
            table: SQLAlchemy Core table
            insert_statement: SQLite insert statement
            payload: payload being inserted
        Returns:
            update value mapping
        """
        update_values = {}
        for column_name in payload:
            if column_name == "test_case_id":
                continue
            column = table.c[column_name]
            if column.name in {"difficulty", "prompt", "verified"}:
                update_values[column.name] = func.max(
                    column, insert_statement.excluded[column.name]
                )
            else:
                update_values[column.name] = insert_statement.excluded[column.name]
        return update_values

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
