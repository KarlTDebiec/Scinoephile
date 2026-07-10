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
from scinoephile.core.llms import OperationSpec
from scinoephile.llms.review import REVIEW_OPERATION_SPEC
from scinoephile.llms.translation import TRANSLATION_OPERATION_SPEC
from scinoephile.optimization.persistence.test_cases import (
    PersistedTestCase,
    TestCaseSqliteStore,
)
from scinoephile.optimization.persistence.test_cases.id import get_test_case_id


def get_test_case(
    *,
    difficulty: int = 0,
    prompt: bool = False,
    verified: bool = False,
    query: dict[str, JsonValue] | None = None,
    answer: dict[str, JsonValue] | None = None,
    operation_spec: OperationSpec = TRANSLATION_OPERATION_SPEC,
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
            operation_spec,
        ),
        operation=operation_spec.operation,
        difficulty=difficulty,
        prompt=prompt,
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
        verified=True,
        query={
            "items": ["one", "two", {"nested": True}],
            "literal_array": "[]",
        },
        answer={"value": {"nested": [1, 2, 3]}},
    )

    store.sync_source_paths(
        {"x.json": [test_case]},
        operation_spec=TRANSLATION_OPERATION_SPEC,
        dry_run=False,
    )

    loaded = store.get_test_case(test_case.test_case_id)
    assert loaded is not None
    assert loaded.operation == "translation"
    assert loaded.query == test_case.query
    assert loaded.answer == test_case.answer
    assert loaded.source_paths == ("x.json",)

    with closing(sqlite3.connect(database_path)) as connection:
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
        "prompt",
        "query_json",
        "test_case_id",
        "verified",
    }
    assert source_columns == {"source_path", "test_case_id"}


def test_store_does_not_create_parent_dir_on_init(tmp_path: Path):
    """Initializing a store should not create parent directories."""
    database_path = tmp_path / "missing/test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)

    assert not database_path.parent.exists()
    assert store.get_test_case("missing") is None
    assert not database_path.parent.exists()


def test_store_keeps_sql_owned_metadata_when_source_is_removed(tmp_path: Path):
    """Removing provenance should not change SQL-owned curation metadata."""
    database_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)
    low_metadata = get_test_case(difficulty=1)
    high_metadata = get_test_case(
        difficulty=3,
        prompt=True,
        verified=True,
    )
    assert low_metadata.test_case_id == high_metadata.test_case_id

    store.sync_source_paths(
        {
            "low.json": [low_metadata],
            "high.json": [high_metadata],
        },
        operation_spec=TRANSLATION_OPERATION_SPEC,
        dry_run=False,
    )
    loaded = store.get_test_case(low_metadata.test_case_id)
    assert loaded is not None
    assert loaded.difficulty == 3
    assert loaded.prompt
    assert loaded.verified
    assert loaded.source_paths == ("high.json", "low.json")

    store.sync_source_paths(
        {"high.json": []},
        operation_spec=TRANSLATION_OPERATION_SPEC,
        dry_run=False,
    )
    retained = store.get_test_case(low_metadata.test_case_id)
    assert retained is not None
    assert retained.difficulty == 3
    assert retained.prompt
    assert retained.verified
    assert retained.source_paths == ("low.json",)


def test_store_filters_source_lookup_by_operation(tmp_path: Path):
    """Source lookup should support catalog operation filters."""
    database_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)
    first = get_test_case(
        operation_spec=REVIEW_OPERATION_SPEC,
        query={"input": "first"},
    )
    second = get_test_case(
        operation_spec=REVIEW_OPERATION_SPEC,
        query={"input": "second"},
    )
    third = get_test_case(
        operation_spec=TRANSLATION_OPERATION_SPEC,
        query={"input": "third"},
    )

    store.sync_source_paths(
        {
            "first.json": [first],
            "second.json": [second],
        },
        operation_spec=REVIEW_OPERATION_SPEC,
        dry_run=False,
    )
    store.sync_source_paths(
        {"third.json": [third]},
        operation_spec=TRANSLATION_OPERATION_SPEC,
        dry_run=False,
    )

    filtered = store.get_test_cases_by_source_path(
        "second.json",
        operation_spec=REVIEW_OPERATION_SPEC,
    )
    assert [test_case.test_case_id for test_case in filtered] == [second.test_case_id]
    assert (
        store.get_test_cases_by_source_path(
            "second.json",
            operation_spec=TRANSLATION_OPERATION_SPEC,
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
            operation_spec=TRANSLATION_OPERATION_SPEC,
            dry_run=False,
        )

    assert not database_path.exists()


def test_store_rejects_mismatched_operation_spec(tmp_path: Path):
    """Writes should reject test cases from another operation."""
    database_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)
    test_case = get_test_case(operation_spec=TRANSLATION_OPERATION_SPEC)

    with raises(ScinoephileError, match="does not match synchronized operation"):
        store.sync_source_paths(
            {"source.json": [test_case]},
            operation_spec=REVIEW_OPERATION_SPEC,
            dry_run=False,
        )

    assert not database_path.exists()


def test_store_syncs_shared_source_path_within_operation(tmp_path: Path):
    """Syncing one operation should preserve another operation's provenance."""
    database_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)
    review = get_test_case(operation_spec=REVIEW_OPERATION_SPEC)
    translation = get_test_case(operation_spec=TRANSLATION_OPERATION_SPEC)

    store.sync_source_paths(
        {"source.json": [review]},
        operation_spec=REVIEW_OPERATION_SPEC,
        dry_run=False,
    )
    store.sync_source_paths(
        {"source.json": [translation]},
        operation_spec=TRANSLATION_OPERATION_SPEC,
        dry_run=False,
    )
    store.sync_source_paths(
        {"source.json": []},
        operation_spec=REVIEW_OPERATION_SPEC,
        dry_run=False,
    )

    loaded_review = store.get_test_case(review.test_case_id)
    loaded_translation = store.get_test_case(translation.test_case_id)
    assert loaded_review is not None
    assert loaded_review.source_paths == ()
    assert loaded_translation is not None
    assert loaded_translation.source_paths == ("source.json",)


def test_store_rejects_legacy_schema(tmp_path: Path):
    """Writing should reject rather than silently relabel a legacy schema."""
    database_path = tmp_path / "test_cases.sqlite"
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute("PRAGMA user_version=3")
    store = TestCaseSqliteStore(database_path)

    with raises(ScinoephileError, match="schema version 3 is unsupported"):
        store.create_schema()
