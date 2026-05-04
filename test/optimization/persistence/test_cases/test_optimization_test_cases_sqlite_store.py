#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SQLite test case store."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from scinoephile.optimization.persistence.test_cases import (
    PersistedTestCase,
    TestCaseSqliteStore,
)


def test_store_upsert_and_fetch(tmp_path: Path):
    """Upserting a row should allow fetching it back."""
    db_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(db_path)
    table_name = "test_cases__unit__basic"

    tc = PersistedTestCase(
        test_case_id="abc",
        difficulty=1,
        prompt=False,
        verified=True,
        query={"q": 1},
        answer={"a": 2},
        source_paths=["x.json"],
    )
    store.upsert_table_test_cases(table_name, [tc], source_path="x.json")

    loaded = store.get_test_case(table_name, "abc")
    assert loaded is not None
    assert loaded.test_case_id == "abc"
    assert loaded.query == {"q": 1}
    assert loaded.answer == {"a": 2}
    assert "x.json" in loaded.source_paths

    with sqlite3.connect(db_path) as connection:
        columns = {
            str(row[1])
            for row in connection.execute(f"PRAGMA table_info({table_name})")
        }
    assert "query" not in columns
    assert "answer" not in columns
    assert "source_paths" not in columns
    assert "query__q" in columns
    assert "answer__a" in columns


def test_store_does_not_create_parent_dir_on_init(tmp_path: Path):
    """Initializing a store should not create parent directories."""
    db_path = tmp_path / "missing" / "test_cases.sqlite"
    store = TestCaseSqliteStore(db_path)

    assert not db_path.parent.exists()
    assert store.get_test_case("test_cases__unit__basic", "abc") is None
    assert store.list_tables() == []
    assert not db_path.parent.exists()


def test_store_merges_duplicate_id_metadata_without_downgrading(tmp_path: Path):
    """Duplicate IDs from different sources should preserve curated metadata."""
    db_path = tmp_path / "test_cases.sqlite"
    table_name = "test_cases__unit__basic"
    query = {"q": "same"}
    answer = {"a": "same"}

    low_metadata = PersistedTestCase(
        test_case_id="same",
        difficulty=1,
        prompt=False,
        verified=False,
        query=query,
        answer=answer,
        source_paths=["low.json"],
    )
    high_metadata = PersistedTestCase(
        test_case_id="same",
        difficulty=3,
        prompt=True,
        verified=True,
        query=query,
        answer=answer,
        source_paths=["high.json"],
    )

    store = TestCaseSqliteStore(db_path)
    store.upsert_table_test_cases(table_name, [low_metadata], source_path="low.json")
    store.upsert_table_test_cases(table_name, [high_metadata], source_path="high.json")
    loaded = store.get_test_case(table_name, "same")
    assert loaded is not None
    assert loaded.difficulty == 3
    assert loaded.prompt
    assert loaded.verified

    reversed_store = TestCaseSqliteStore(tmp_path / "reversed.sqlite")
    reversed_store.upsert_table_test_cases(
        table_name, [high_metadata], source_path="high.json"
    )
    reversed_store.upsert_table_test_cases(
        table_name, [low_metadata], source_path="low.json"
    )
    reversed_loaded = reversed_store.get_test_case(table_name, "same")
    assert reversed_loaded is not None
    assert reversed_loaded.difficulty == 3
    assert reversed_loaded.prompt
    assert reversed_loaded.verified


def test_store_preserves_json_looking_strings(tmp_path: Path):
    """JSON-looking string fields should round-trip as strings."""
    db_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(db_path)
    table_name = "test_cases__unit__basic"

    tc = PersistedTestCase(
        test_case_id="abc",
        difficulty=1,
        prompt=False,
        verified=True,
        query={
            "literal_array": "[]",
            "literal_object": "{}",
        },
        answer={
            "literal_array": "[]",
            "literal_object": "{}",
        },
        source_paths=["x.json"],
    )
    store.upsert_table_test_cases(table_name, [tc], source_path="x.json")

    loaded = store.get_test_case(table_name, "abc")
    assert loaded is not None
    assert loaded.query["literal_array"] == "[]"
    assert loaded.query["literal_object"] == "{}"
    assert loaded.answer["literal_array"] == "[]"
    assert loaded.answer["literal_object"] == "{}"


def test_store_source_path_index(tmp_path: Path):
    """`test_case_sources` should support lookup by source path."""
    db_path = tmp_path / "test_cases.sqlite"
    store = TestCaseSqliteStore(db_path)
    table_name = "test_cases__unit__basic"

    tc1 = PersistedTestCase(
        test_case_id="a",
        difficulty=0,
        prompt=False,
        verified=False,
        query={"q": 1},
        answer={"a": 1},
        source_paths=["s1.json"],
    )
    tc2 = PersistedTestCase(
        test_case_id="b",
        difficulty=0,
        prompt=False,
        verified=False,
        query={"q": 2},
        answer={"a": 2},
        source_paths=["s2.json"],
    )
    store.upsert_table_test_cases(table_name, [tc1, tc2], source_path="s1.json")
    by_s1 = store.get_test_cases_by_source_path(table_name, "s1.json")
    assert {x.test_case_id for x in by_s1} == {"a", "b"}
