#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for normalized SQLite test-case persistence."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import replace
from pathlib import Path

from pydantic import JsonValue
from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import Manager
from scinoephile.llms.review import ReviewManager
from scinoephile.llms.translation import TranslationManager
from scinoephile.optimization.persistence.test_cases import (
    PersistedTestCase,
    TestCaseSqliteStore,
)
from scinoephile.optimization.persistence.test_cases.id import get_test_case_id


def get_test_case(
    *,
    difficulty: int = 0,
    few_shot: bool = False,
    verified: bool = False,
    query: dict[str, JsonValue] | None = None,
    answer: dict[str, JsonValue] | None = None,
    manager_cls: type[Manager] = TranslationManager,
) -> PersistedTestCase:
    """Get a persisted test case with provided values."""
    if query is None:
        query = {"input": "same"}
    if answer is None:
        answer = {"output": "same"}
    return PersistedTestCase(
        test_case_id=get_test_case_id(
            query,
            answer,
            manager_cls,
        ),
        operation=manager_cls.operation,
        difficulty=difficulty,
        few_shot=few_shot,
        verified=verified,
        query=query,
        answer=answer,
        source_paths=(),
    )


def test_store_round_trips_normalized_json(tmp_path: Path):
    """JSON payloads should round-trip without operation-specific columns."""
    database_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)
    test_case = get_test_case(
        difficulty=1,
        few_shot=True,
        verified=True,
        query={
            "items": ["one", "two", {"nested": True}],
            "literal_array": "[]",
        },
        answer={"value": {"nested": [1, 2, 3]}},
    )

    store.sync_source_paths(
        {"x.json": [test_case]},
        manager_cls=TranslationManager,
        dry_run=False,
    )

    loaded = store.get_test_case(test_case.test_case_id)
    assert loaded is not None
    assert loaded.operation == "translation"
    assert loaded.few_shot
    assert loaded.query == test_case.query
    assert loaded.answer == test_case.answer
    assert loaded.source_paths == ("x.json",)

    with closing(sqlite3.connect(database_path)) as connection:
        few_shot = connection.execute("SELECT few_shot FROM test_cases").fetchone()[0]
        columns = {
            str(row[1]) for row in connection.execute("PRAGMA table_info(test_cases)")
        }
        source_columns = {
            str(row[1])
            for row in connection.execute("PRAGMA table_info(test_case_sources)")
        }
    assert columns == {
        "answer_json",
        "difficulty",
        "operation",
        "few_shot",
        "query_json",
        "test_case_id",
        "verified",
    }
    assert source_columns == {"source_path", "test_case_id"}
    assert few_shot == 1


def test_store_defers_parent_dir_creation_until_schema_creation(tmp_path: Path):
    """Initializing and reading should not create parent directories."""
    database_path = tmp_path / "missing/test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)

    assert not database_path.parent.exists()
    assert store.get_test_case("missing") is None
    assert not database_path.parent.exists()

    store.create_schema()

    assert database_path.is_file()


def test_store_keeps_sql_owned_metadata_when_source_is_removed(tmp_path: Path):
    """Removing provenance should not change SQL-owned curation metadata."""
    database_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)
    low_metadata = get_test_case(difficulty=1)
    high_metadata = get_test_case(difficulty=3, few_shot=True, verified=True)
    assert low_metadata.test_case_id == high_metadata.test_case_id

    store.sync_source_paths(
        {
            "low.json": [low_metadata],
            "high.json": [high_metadata],
        },
        manager_cls=TranslationManager,
        dry_run=False,
    )
    loaded = store.get_test_case(low_metadata.test_case_id)
    assert loaded is not None
    assert loaded.difficulty == 3
    assert loaded.few_shot
    assert loaded.verified
    assert loaded.source_paths == ("high.json", "low.json")

    store.sync_source_paths(
        {"high.json": []},
        manager_cls=TranslationManager,
        dry_run=False,
    )
    retained = store.get_test_case(low_metadata.test_case_id)
    assert retained is not None
    assert retained.difficulty == 3
    assert retained.few_shot
    assert retained.verified
    assert retained.source_paths == ("low.json",)


def test_store_filters_source_lookup_by_operation(tmp_path: Path):
    """Source lookup should support catalog operation filters."""
    database_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)
    first = get_test_case(
        manager_cls=ReviewManager,
        query={"input": "first"},
    )
    second = get_test_case(
        manager_cls=ReviewManager,
        query={"input": "second"},
    )
    third = get_test_case(
        manager_cls=TranslationManager,
        query={"input": "third"},
    )

    store.sync_source_paths(
        {
            "first.json": [first],
            "second.json": [second],
        },
        manager_cls=ReviewManager,
        dry_run=False,
    )
    store.sync_source_paths(
        {"third.json": [third]},
        manager_cls=TranslationManager,
        dry_run=False,
    )

    filtered = store.get_test_cases_by_source_path(
        "second.json",
        manager_cls=ReviewManager,
    )
    assert [test_case.test_case_id for test_case in filtered] == [second.test_case_id]
    assert (
        store.get_test_cases_by_source_path(
            "second.json",
            manager_cls=TranslationManager,
        )
        == []
    )


def test_store_rejects_mismatched_content_addressed_id(tmp_path: Path):
    """Writes should reject test cases whose ID does not match their content."""
    database_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)
    test_case = replace(get_test_case(), test_case_id="incorrect")

    with raises(ScinoephileError, match="does not match its content-addressed ID"):
        store.sync_source_paths(
            {"source.json": [test_case]},
            manager_cls=TranslationManager,
            dry_run=False,
        )

    assert not database_path.exists()


def test_store_rejects_mismatched_manager(tmp_path: Path):
    """Writes should reject test cases from another manager's operation."""
    database_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)
    test_case = get_test_case(manager_cls=TranslationManager)

    with raises(ScinoephileError, match="does not match synchronized operation"):
        store.sync_source_paths(
            {"source.json": [test_case]},
            manager_cls=ReviewManager,
            dry_run=False,
        )

    assert not database_path.exists()


def test_store_syncs_shared_source_path_within_operation(tmp_path: Path):
    """Syncing one operation should preserve another operation's provenance."""
    database_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)
    review = get_test_case(manager_cls=ReviewManager)
    translation = get_test_case(manager_cls=TranslationManager)

    store.sync_source_paths(
        {"source.json": [review]},
        manager_cls=ReviewManager,
        dry_run=False,
    )
    store.sync_source_paths(
        {"source.json": [translation]},
        manager_cls=TranslationManager,
        dry_run=False,
    )
    store.sync_source_paths(
        {"source.json": []},
        manager_cls=ReviewManager,
        dry_run=False,
    )

    loaded_review = store.get_test_case(review.test_case_id)
    loaded_translation = store.get_test_case(translation.test_case_id)
    assert loaded_review is not None
    assert loaded_review.source_paths == ()
    assert loaded_translation is not None
    assert loaded_translation.source_paths == ("source.json",)


def test_store_does_not_manage_a_global_schema_version(tmp_path: Path):
    """Component table creation should leave SQLite user versions untouched."""
    database_path = tmp_path / "test_cases.sqlite"
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute("PRAGMA user_version=3")
    store = TestCaseSqliteStore(database_path)

    store.create_schema()

    with closing(sqlite3.connect(database_path)) as connection:
        version = connection.execute("PRAGMA user_version").fetchone()[0]
    assert version == 3
