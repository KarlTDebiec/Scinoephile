#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for normalized SQLite test-case persistence."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import replace
from pathlib import Path

from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.optimization.persistence.test_cases import (
    PersistedTestCase,
    TestCaseSqliteStore,
)


def get_test_case(
    *,
    difficulty: int = 0,
    prompt: bool = False,
    verified: bool = False,
    query: dict[str, object] | None = None,
    answer: dict[str, object] | None = None,
    operation: str = "unit",
    variant: str = "basic",
) -> PersistedTestCase:
    """Get a persisted test case with provided values."""
    if query is None:
        query = {"input": "same"}
    if answer is None:
        answer = {"output": "same"}
    return PersistedTestCase.from_json_data(
        {
            "query": query,
            "answer": answer,
            "difficulty": difficulty,
            "prompt": prompt,
            "verified": verified,
        },
        operation=operation,
        variant=variant,
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

    store.sync_source_paths({"x.json": [test_case]}, dry_run=False)

    loaded = store.get_test_case(test_case.test_case_id)
    assert loaded is not None
    assert loaded.operation == "unit"
    assert loaded.variant == "basic"
    assert loaded.query == test_case.query
    assert loaded.answer == test_case.answer
    assert loaded.source_paths == ["x.json"]

    with closing(sqlite3.connect(database_path)) as connection:
        columns = {
            str(row[1]) for row in connection.execute("PRAGMA table_info(test_cases)")
        }
    assert columns == {
        "answer_json",
        "operation",
        "query_json",
        "test_case_id",
        "variant",
    }


def test_store_does_not_create_parent_dir_on_init(tmp_path: Path):
    """Initializing a store should not create parent directories."""
    database_path = tmp_path / "missing/test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)

    assert not database_path.parent.exists()
    assert store.get_test_case("missing") is None
    assert store.list_tables() == []
    assert not database_path.parent.exists()


def test_store_aggregates_and_recalculates_source_metadata(tmp_path: Path):
    """Removing a source should recalculate aggregated curation metadata."""
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
        dry_run=False,
    )
    loaded = store.get_test_case(low_metadata.test_case_id)
    assert loaded is not None
    assert loaded.difficulty == 3
    assert loaded.prompt
    assert loaded.verified
    assert loaded.source_paths == ["high.json", "low.json"]

    store.sync_source_paths({"high.json": []}, dry_run=False)
    recalculated = store.get_test_case(low_metadata.test_case_id)
    assert recalculated is not None
    assert recalculated.difficulty == 1
    assert not recalculated.prompt
    assert not recalculated.verified
    assert recalculated.source_paths == ["low.json"]


def test_store_filters_source_paths_by_operation_and_variant(tmp_path: Path):
    """Source lookup should support catalog operation and variant filters."""
    database_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)
    first = get_test_case(operation="review", variant="eng")
    second = get_test_case(operation="review", variant="zho-hant")
    third = get_test_case(operation="translation", variant="eng-zho")

    store.sync_source_paths(
        {
            "first.json": [first],
            "second.json": [second],
            "third.json": [third],
        },
        dry_run=False,
    )

    assert store.list_source_paths(operation="review") == [
        "first.json",
        "second.json",
    ]
    assert store.list_source_paths(
        operation="review",
        variant="zho-hant",
    ) == ["second.json"]
    filtered = store.get_test_cases_by_source_path(
        "second.json",
        operation="review",
        variant="zho-hant",
    )
    assert [test_case.test_case_id for test_case in filtered] == [second.test_case_id]


def test_store_rejects_mismatched_content_addressed_id(tmp_path: Path):
    """Writes should reject test cases whose ID does not match their content."""
    database_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(database_path)
    test_case = replace(get_test_case(), test_case_id="incorrect")

    with raises(ScinoephileError, match="does not match its content-addressed ID"):
        store.sync_source_paths({"source.json": [test_case]}, dry_run=False)

    assert not database_path.exists()


def test_store_rejects_legacy_schema(tmp_path: Path):
    """Writing should reject rather than silently relabel a legacy schema."""
    database_path = tmp_path / "test_cases.sqlite"
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute("PRAGMA user_version=2")
    store = TestCaseSqliteStore(database_path)

    with raises(ScinoephileError, match="schema version 2 is unsupported"):
        store.create_schema()
