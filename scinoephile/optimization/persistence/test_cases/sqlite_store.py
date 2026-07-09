#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Normalized SQLite persistence for LLM test cases."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from logging import getLogger
from pathlib import Path
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Table,
    Text,
    create_engine,
    inspect,
    select,
    text,
)
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import URL, Connection, RowMapping
from sqlalchemy.event import listen
from sqlalchemy.pool import NullPool

from scinoephile.common.validation import val_output_path
from scinoephile.core.exceptions import ScinoephileError

from .id import get_test_case_id
from .persisted_test_case import PersistedTestCase

__all__ = ["TestCaseSqliteStore"]

logger = getLogger(__name__)

type _SourceMetadata = tuple[int, bool, bool]
"""Difficulty, prompt, and verified metadata for one source association."""


def _enable_sqlite_foreign_keys(
    dbapi_connection: Any,
    _connection_record: object,
):
    """Enable SQLite foreign-key enforcement on a new DB-API connection."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class TestCaseSqliteStore:
    """Normalized SQLite persistence and lookup for test cases."""

    __test__ = False
    """Inform pytest not to collect this class as a test."""

    schema_version = 3
    """SQLite schema version."""

    _metadata = MetaData()
    """SQLAlchemy Core metadata for the test-case catalog."""

    _test_cases = Table(
        "test_cases",
        _metadata,
        Column("test_case_id", Text, primary_key=True),
        Column("operation", Text, nullable=False),
        Column("variant", Text, nullable=False),
        Column("query_json", Text, nullable=False),
        Column("answer_json", Text, nullable=False),
        CheckConstraint("json_valid(query_json)", name="test_cases_query_json_valid"),
        CheckConstraint("json_valid(answer_json)", name="test_cases_answer_json_valid"),
        Index("test_cases_operation_variant", "operation", "variant"),
    )
    """Content-addressed test cases shared by all operations and variants."""

    _test_case_sources = Table(
        "test_case_sources",
        _metadata,
        Column(
            "test_case_id",
            Text,
            ForeignKey("test_cases.test_case_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        Column("source_path", Text, primary_key=True),
        Column("difficulty", Integer, nullable=False),
        Column("prompt", Integer, nullable=False),
        Column("verified", Integer, nullable=False),
        Index("test_case_sources_source_path", "source_path"),
    )
    """Source associations and source-specific curation metadata."""

    def __init__(self, database_path: Path):
        """Initialize.

        Arguments:
            database_path: SQLite database path
        """
        self.database_path = val_output_path(
            database_path,
            exist_ok=True,
            create=False,
        )
        self.engine = create_engine(
            URL.create("sqlite", database=str(self.database_path)),
            future=True,
            poolclass=NullPool,
        )
        listen(self.engine, "connect", _enable_sqlite_foreign_keys)

    def create_schema(self):
        """Create the normalized SQLite schema if needed.

        Raises:
            ScinoephileError: if the database uses an unsupported schema version
        """
        self.database_path = val_output_path(self.database_path, exist_ok=True)
        with self.engine.begin() as connection:
            version = self._get_schema_version(connection)
            if version not in {0, self.schema_version}:
                raise ScinoephileError(
                    f"SQLite test-case schema version {version} is unsupported; "
                    "create a new database."
                )
            self._metadata.create_all(connection)
            connection.execute(text(f"PRAGMA user_version={self.schema_version}"))

    def get_test_case(self, test_case_id: str) -> PersistedTestCase | None:
        """Fetch a single test case by ID.

        Arguments:
            test_case_id: test case identifier
        Returns:
            persisted test case, if present
        """
        if not self.database_path.exists():
            return None
        with self.engine.connect() as connection:
            version = self._get_schema_version(connection)
            if version == 0:
                return None
            self._require_current_schema(version)
            row = (
                connection.execute(
                    select(self._test_cases).where(
                        self._test_cases.c.test_case_id == test_case_id
                    )
                )
                .mappings()
                .first()
            )
            if row is None:
                return None
            return self._row_to_test_case(connection, row)

    def get_test_cases_by_source_path(
        self,
        source_path: str,
        *,
        operation: str | None = None,
        variant: str | None = None,
    ) -> list[PersistedTestCase]:
        """Fetch test cases associated with a source path.

        Arguments:
            source_path: original JSON path recorded during import
            operation: optional operation filter
            variant: optional variant filter
        Returns:
            persisted test cases
        """
        if not self.database_path.exists():
            return []
        with self.engine.connect() as connection:
            version = self._get_schema_version(connection)
            if version == 0:
                return []
            self._require_current_schema(version)
            statement = (
                select(self._test_cases)
                .join(self._test_case_sources)
                .where(self._test_case_sources.c.source_path == source_path)
            )
            if operation is not None:
                statement = statement.where(self._test_cases.c.operation == operation)
            if variant is not None:
                statement = statement.where(self._test_cases.c.variant == variant)
            rows = (
                connection.execute(statement.order_by(self._test_cases.c.test_case_id))
                .mappings()
                .all()
            )
            return [self._row_to_test_case(connection, row) for row in rows]

    def list_source_paths(
        self,
        *,
        operation: str | None = None,
        variant: str | None = None,
    ) -> list[str]:
        """List source paths, optionally filtered by operation and variant.

        Arguments:
            operation: optional operation filter
            variant: optional variant filter
        Returns:
            ordered source paths
        """
        if not self.database_path.exists():
            return []
        with self.engine.connect() as connection:
            version = self._get_schema_version(connection)
            if version == 0:
                return []
            self._require_current_schema(version)
            statement = select(self._test_case_sources.c.source_path).distinct()
            if operation is not None or variant is not None:
                statement = statement.join(self._test_cases)
            if operation is not None:
                statement = statement.where(self._test_cases.c.operation == operation)
            if variant is not None:
                statement = statement.where(self._test_cases.c.variant == variant)
            rows = (
                connection.execute(
                    statement.order_by(self._test_case_sources.c.source_path)
                )
                .scalars()
                .all()
            )
        return [str(row) for row in rows]

    def list_tables(self) -> list[str]:
        """List tables currently present in the database.

        Returns:
            ordered table names
        """
        if not self.database_path.exists():
            return []
        return sorted(inspect(self.engine).get_table_names())

    def sync_source_paths(
        self,
        source_test_cases: Mapping[str, Iterable[PersistedTestCase]],
        *,
        dry_run: bool,
    ) -> tuple[list[PersistedTestCase], list[PersistedTestCase], list[str]]:
        """Synchronize complete test-case sets for one or more source paths.

        All source sets are written in one transaction. Metadata is stored on each
        source association and aggregated when a test case is read.

        Arguments:
            source_test_cases: desired test cases keyed by canonical source path
            dry_run: if True, compute changes without writing
        Returns:
            inserted associations, updated associations, and removed association IDs
        """
        desired_by_source: dict[str, dict[str, PersistedTestCase]] = {}
        for source_path, test_cases in source_test_cases.items():
            desired_by_id: dict[str, PersistedTestCase] = {}
            for test_case in test_cases:
                expected_id = get_test_case_id(
                    test_case.query,
                    test_case.answer,
                    operation=test_case.operation,
                    variant=test_case.variant,
                )
                if test_case.test_case_id != expected_id:
                    raise ScinoephileError(
                        f"Test case {test_case.test_case_id} does not match its "
                        "content-addressed ID."
                    )
                desired_by_id[test_case.test_case_id] = test_case
            desired_by_source[source_path] = desired_by_id

        if dry_run and not self.database_path.exists():
            inserted = [
                test_case
                for source_path in sorted(desired_by_source)
                for test_case in desired_by_source[source_path].values()
            ]
            return (inserted, [], [])

        if dry_run:
            with self.engine.connect() as connection:
                version = self._get_schema_version(connection)
                if version == 0:
                    inserted = [
                        test_case
                        for source_path in sorted(desired_by_source)
                        for test_case in desired_by_source[source_path].values()
                    ]
                    return (inserted, [], [])
                self._require_current_schema(version)
                return self._sync_source_paths(
                    connection,
                    desired_by_source,
                    dry_run=True,
                )

        self.create_schema()
        with self.engine.begin() as connection:
            changes = self._sync_source_paths(
                connection,
                desired_by_source,
                dry_run=False,
            )
        logger.info(f"Synchronized {len(desired_by_source)} test-case source paths")
        return changes

    @staticmethod
    def _get_schema_version(connection: Connection) -> int:
        """Get the SQLite user schema version.

        Arguments:
            connection: SQLAlchemy connection
        Returns:
            SQLite user schema version
        """
        return int(connection.execute(text("PRAGMA user_version")).scalar_one())

    def _get_source_metadata(
        self,
        connection: Connection,
        source_path: str,
    ) -> dict[str, _SourceMetadata]:
        """Get persisted metadata for one source path.

        Arguments:
            connection: SQLAlchemy connection
            source_path: canonical source path
        Returns:
            source metadata keyed by test case ID
        """
        rows = connection.execute(
            select(
                self._test_case_sources.c.test_case_id,
                self._test_case_sources.c.difficulty,
                self._test_case_sources.c.prompt,
                self._test_case_sources.c.verified,
            ).where(self._test_case_sources.c.source_path == source_path)
        ).all()
        return {
            str(row.test_case_id): (
                int(row.difficulty),
                bool(row.prompt),
                bool(row.verified),
            )
            for row in rows
        }

    def _get_source_rows(
        self,
        connection: Connection,
        test_case_id: str,
    ) -> list[RowMapping]:
        """Get source association rows for a test case.

        Arguments:
            connection: SQLAlchemy connection
            test_case_id: test case identifier
        Returns:
            source association rows
        """
        return list(
            connection.execute(
                select(self._test_case_sources)
                .where(self._test_case_sources.c.test_case_id == test_case_id)
                .order_by(self._test_case_sources.c.source_path)
            )
            .mappings()
            .all()
        )

    @staticmethod
    def _get_test_case_metadata(test_case: PersistedTestCase) -> _SourceMetadata:
        """Get source metadata from a persisted test case.

        Arguments:
            test_case: persisted test case
        Returns:
            source metadata tuple
        """
        return (test_case.difficulty, test_case.prompt, test_case.verified)

    @staticmethod
    def _load_json_object(value: object, field_name: str) -> dict[str, object]:
        """Load a JSON object stored in a SQLite text column.

        Arguments:
            value: SQLite column value
            field_name: field name used in corruption errors
        Returns:
            loaded JSON object
        Raises:
            ScinoephileError: if the stored value is not a JSON object
        """
        if not isinstance(value, str):
            raise ScinoephileError(
                f"Persisted test case {field_name} is not JSON text."
            )
        loaded = json.loads(value)
        if not isinstance(loaded, dict):
            raise ScinoephileError(
                f"Persisted test case {field_name} is not a JSON object."
            )
        return loaded

    @staticmethod
    def _require_current_schema(version: int):
        """Require the current normalized schema version.

        Arguments:
            version: SQLite user schema version
        Raises:
            ScinoephileError: if the schema version is unsupported
        """
        if version != TestCaseSqliteStore.schema_version:
            raise ScinoephileError(
                f"SQLite test-case schema version {version} is unsupported; "
                "create a new database."
            )

    def _row_to_test_case(
        self,
        connection: Connection,
        row: RowMapping,
    ) -> PersistedTestCase:
        """Convert a test-case row and its source metadata to a model.

        Arguments:
            connection: SQLAlchemy connection
            row: test-case row
        Returns:
            persisted test case
        Raises:
            ScinoephileError: if the row has no source associations
        """
        test_case_id = str(row["test_case_id"])
        source_rows = self._get_source_rows(connection, test_case_id)
        if not source_rows:
            raise ScinoephileError(
                f"Persisted test case {test_case_id} has no source associations."
            )
        return PersistedTestCase(
            test_case_id=test_case_id,
            operation=str(row["operation"]),
            variant=str(row["variant"]),
            difficulty=max(int(source_row["difficulty"]) for source_row in source_rows),
            prompt=any(bool(source_row["prompt"]) for source_row in source_rows),
            verified=any(bool(source_row["verified"]) for source_row in source_rows),
            query=self._load_json_object(row["query_json"], "query"),
            answer=self._load_json_object(row["answer_json"], "answer"),
            source_paths=[str(source_row["source_path"]) for source_row in source_rows],
        )

    @staticmethod
    def _serialize_json_object(value: dict[str, object]) -> str:
        """Serialize a JSON object canonically for SQLite storage.

        Arguments:
            value: JSON object
        Returns:
            canonical JSON text
        """
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def _sync_source_paths(
        self,
        connection: Connection,
        desired_by_source: Mapping[str, Mapping[str, PersistedTestCase]],
        *,
        dry_run: bool,
    ) -> tuple[list[PersistedTestCase], list[PersistedTestCase], list[str]]:
        """Synchronize source paths using an existing connection.

        Arguments:
            connection: SQLAlchemy connection
            desired_by_source: desired cases keyed by source path and test case ID
            dry_run: if True, compute changes without writing
        Returns:
            inserted associations, updated associations, and removed association IDs
        """
        inserted: list[PersistedTestCase] = []
        updated: list[PersistedTestCase] = []
        deleted: list[str] = []
        for source_path in sorted(desired_by_source):
            desired_by_id = desired_by_source[source_path]
            existing_metadata = self._get_source_metadata(connection, source_path)
            existing_ids = set(existing_metadata)
            desired_ids = set(desired_by_id)

            insert_ids = sorted(desired_ids - existing_ids)
            update_ids = sorted(
                test_case_id
                for test_case_id in desired_ids & existing_ids
                if existing_metadata[test_case_id]
                != self._get_test_case_metadata(desired_by_id[test_case_id])
            )
            delete_ids = sorted(existing_ids - desired_ids)
            inserted.extend(desired_by_id[test_case_id] for test_case_id in insert_ids)
            updated.extend(desired_by_id[test_case_id] for test_case_id in update_ids)
            deleted.extend(delete_ids)

            if dry_run:
                continue

            for test_case in desired_by_id.values():
                connection.execute(
                    sqlite_insert(self._test_cases)
                    .values(
                        test_case_id=test_case.test_case_id,
                        operation=test_case.operation,
                        variant=test_case.variant,
                        query_json=self._serialize_json_object(test_case.query),
                        answer_json=self._serialize_json_object(test_case.answer),
                    )
                    .on_conflict_do_nothing(
                        index_elements=[self._test_cases.c.test_case_id]
                    )
                )
                source_insert = sqlite_insert(self._test_case_sources).values(
                    test_case_id=test_case.test_case_id,
                    source_path=source_path,
                    difficulty=test_case.difficulty,
                    prompt=int(test_case.prompt),
                    verified=int(test_case.verified),
                )
                connection.execute(
                    source_insert.on_conflict_do_update(
                        index_elements=[
                            self._test_case_sources.c.test_case_id,
                            self._test_case_sources.c.source_path,
                        ],
                        set_={
                            "difficulty": source_insert.excluded.difficulty,
                            "prompt": source_insert.excluded.prompt,
                            "verified": source_insert.excluded.verified,
                        },
                    )
                )

            if delete_ids:
                connection.execute(
                    self._test_case_sources.delete().where(
                        (self._test_case_sources.c.source_path == source_path)
                        & (self._test_case_sources.c.test_case_id.in_(delete_ids))
                    )
                )
                remaining_source = (
                    select(self._test_case_sources.c.test_case_id)
                    .where(
                        self._test_case_sources.c.test_case_id
                        == self._test_cases.c.test_case_id
                    )
                    .exists()
                )
                connection.execute(
                    self._test_cases.delete().where(
                        self._test_cases.c.test_case_id.in_(delete_ids),
                        ~remaining_source,
                    )
                )
        return (inserted, updated, deleted)
