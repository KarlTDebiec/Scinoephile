#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Normalized SQLite persistence for LLM test cases."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace
from logging import getLogger

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    Table,
    Text,
    select,
)
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Connection, RowMapping

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.llms import Manager
from scinoephile.optimization.persistence.sqlite import (
    OptimizationSqliteStore,
    load_json_object,
    metadata,
    serialize_json_object,
)

from .id import get_test_case_id
from .persisted_test_case import PersistedTestCase

__all__ = ["TestCaseSqliteStore"]

logger = getLogger(__name__)


class TestCaseSqliteStore(OptimizationSqliteStore):
    """Normalized SQLite persistence and lookup for test cases."""

    __test__ = False
    """Inform pytest not to collect this class as a test."""

    _test_cases = Table(
        "test_cases",
        metadata,
        Column("test_case_id", Text, primary_key=True),
        Column("operation", Text, nullable=False),
        Column("difficulty", Integer, nullable=False),
        Column("prompt", Boolean, nullable=False),
        Column("verified", Boolean, nullable=False),
        Column("query_json", Text, nullable=False),
        Column("answer_json", Text, nullable=False),
        CheckConstraint("json_valid(query_json)", name="test_cases_query_json_valid"),
        CheckConstraint("json_valid(answer_json)", name="test_cases_answer_json_valid"),
        Index("test_cases_operation", "operation"),
    )
    """Content-addressed test cases and SQL-owned curation metadata."""

    _test_case_sources = Table(
        "test_case_sources",
        metadata,
        Column(
            "test_case_id",
            Text,
            ForeignKey("test_cases.test_case_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        Column("source_path", Text, primary_key=True),
        Index("test_case_sources_source_path", "source_path"),
    )
    """JSON source provenance for imported test cases."""

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
        manager_cls: type[Manager] | None = None,
    ) -> list[PersistedTestCase]:
        """Fetch test cases associated with a source path.

        Arguments:
            source_path: original JSON path recorded during import
            manager_cls: optional manager defining the operation filter
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
            if manager_cls is not None:
                statement = statement.where(
                    self._test_cases.c.operation == manager_cls.operation
                )
            rows = (
                connection.execute(statement.order_by(self._test_cases.c.test_case_id))
                .mappings()
                .all()
            )
            return [self._row_to_test_case(connection, row) for row in rows]

    def sync_source_paths(
        self,
        source_test_cases: Mapping[str, Iterable[PersistedTestCase]],
        *,
        manager_cls: type[Manager],
        dry_run: bool,
    ) -> tuple[set[str], set[str]]:
        """Synchronize provenance links for one or more source paths.

        New test cases initialize their SQL-owned curation metadata from the maximum
        difficulty and union of prompt and verified flags across this import. Existing
        SQL metadata is not changed by later JSON synchronization.

        Arguments:
            source_test_cases: desired test cases keyed by canonical source path
            manager_cls: manager defining the synchronized operation
            dry_run: if True, compute changes without writing
        Returns:
            test case IDs whose source association was inserted or removed
        """
        desired_by_source: dict[str, dict[str, PersistedTestCase]] = {}
        canonical_by_id: dict[str, PersistedTestCase] = {}
        for source_path in sorted(source_test_cases):
            desired_by_id: dict[str, PersistedTestCase] = {}
            for test_case in source_test_cases[source_path]:
                if test_case.operation != manager_cls.operation:
                    raise ScinoephileError(
                        f"Test case operation {test_case.operation} does not match "
                        f"synchronized operation {manager_cls.operation}."
                    )
                expected_id = get_test_case_id(
                    test_case.query,
                    test_case.answer,
                    manager_cls,
                )
                if test_case.test_case_id != expected_id:
                    raise ScinoephileError(
                        f"Test case {test_case.test_case_id} does not match its "
                        "content-addressed ID."
                    )
                desired_by_id[test_case.test_case_id] = test_case
                existing = canonical_by_id.get(test_case.test_case_id)
                if existing is None:
                    canonical_by_id[test_case.test_case_id] = test_case
                else:
                    canonical_by_id[test_case.test_case_id] = replace(
                        existing,
                        difficulty=max(existing.difficulty, test_case.difficulty),
                        prompt=existing.prompt or test_case.prompt,
                        verified=existing.verified or test_case.verified,
                    )
            desired_by_source[source_path] = desired_by_id

        all_desired_ids = {
            test_case_id
            for desired_by_id in desired_by_source.values()
            for test_case_id in desired_by_id
        }
        if dry_run and not self.database_path.exists():
            return (all_desired_ids, set())

        if dry_run:
            with self.engine.connect() as connection:
                version = self._get_schema_version(connection)
                if version == 0:
                    return (all_desired_ids, set())
                self._require_current_schema(version)
                return self._sync_source_paths(
                    connection,
                    desired_by_source,
                    canonical_by_id,
                    operation=manager_cls.operation,
                    dry_run=True,
                )

        self.create_schema()
        with self.engine.begin() as connection:
            changes = self._sync_source_paths(
                connection,
                desired_by_source,
                canonical_by_id,
                operation=manager_cls.operation,
                dry_run=False,
            )
        logger.info(f"Synchronized {len(desired_by_source)} test-case source paths")
        return changes

    def _get_source_paths(
        self,
        connection: Connection,
        test_case_id: str,
    ) -> tuple[str, ...]:
        """Get source paths for a test case.

        Arguments:
            connection: SQLAlchemy connection
            test_case_id: test case identifier
        Returns:
            ordered source paths
        """
        return tuple(
            str(source_path)
            for source_path in connection.execute(
                select(self._test_case_sources.c.source_path)
                .where(self._test_case_sources.c.test_case_id == test_case_id)
                .order_by(self._test_case_sources.c.source_path)
            ).scalars()
        )

    def _row_to_test_case(
        self,
        connection: Connection,
        row: RowMapping,
    ) -> PersistedTestCase:
        """Convert a test-case row to a model.

        Arguments:
            connection: SQLAlchemy connection
            row: test-case row
        Returns:
            persisted test case
        """
        test_case_id = str(row["test_case_id"])
        return PersistedTestCase(
            test_case_id=test_case_id,
            operation=str(row["operation"]),
            difficulty=int(row["difficulty"]),
            prompt=bool(row["prompt"]),
            verified=bool(row["verified"]),
            query=load_json_object(row["query_json"], "Persisted test case query"),
            answer=load_json_object(row["answer_json"], "Persisted test case answer"),
            source_paths=self._get_source_paths(connection, test_case_id),
        )

    def _sync_source_paths(
        self,
        connection: Connection,
        desired_by_source: Mapping[str, Mapping[str, PersistedTestCase]],
        canonical_by_id: Mapping[str, PersistedTestCase],
        *,
        operation: str,
        dry_run: bool,
    ) -> tuple[set[str], set[str]]:
        """Synchronize source paths using an existing connection.

        Arguments:
            connection: SQLAlchemy connection
            desired_by_source: desired cases keyed by source path and test case ID
            canonical_by_id: new test cases with aggregated initial metadata
            operation: operation whose source associations are synchronized
            dry_run: if True, compute changes without writing
        Returns:
            test case IDs whose source association was inserted or removed
        """
        inserted: set[str] = set()
        deleted: set[str] = set()
        for source_path in sorted(desired_by_source):
            desired_ids = set(desired_by_source[source_path])
            existing_ids = set(
                connection.execute(
                    select(self._test_case_sources.c.test_case_id)
                    .join(self._test_cases)
                    .where(self._test_case_sources.c.source_path == source_path)
                    .where(self._test_cases.c.operation == operation)
                ).scalars()
            )
            insert_ids = desired_ids - existing_ids
            delete_ids = existing_ids - desired_ids
            inserted.update(insert_ids)
            deleted.update(delete_ids)

            if dry_run:
                continue

            for test_case_id in sorted(insert_ids):
                test_case = canonical_by_id[test_case_id]
                connection.execute(
                    sqlite_insert(self._test_cases)
                    .values(
                        test_case_id=test_case.test_case_id,
                        operation=test_case.operation,
                        difficulty=test_case.difficulty,
                        prompt=test_case.prompt,
                        verified=test_case.verified,
                        query_json=serialize_json_object(test_case.query),
                        answer_json=serialize_json_object(test_case.answer),
                    )
                    .on_conflict_do_nothing(
                        index_elements=[self._test_cases.c.test_case_id]
                    )
                )
                connection.execute(
                    sqlite_insert(self._test_case_sources)
                    .values(test_case_id=test_case_id, source_path=source_path)
                    .on_conflict_do_nothing(
                        index_elements=[
                            self._test_case_sources.c.test_case_id,
                            self._test_case_sources.c.source_path,
                        ]
                    )
                )

            if delete_ids:
                connection.execute(
                    self._test_case_sources.delete().where(
                        (self._test_case_sources.c.source_path == source_path)
                        & (self._test_case_sources.c.test_case_id.in_(delete_ids))
                    )
                )
        return (inserted, deleted)
