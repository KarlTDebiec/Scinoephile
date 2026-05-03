#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SQLite test case store."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from scinoephile.optimization.persistence.test_cases.persisted_test_case import (
    PersistedTestCase,
)
from scinoephile.optimization.persistence.test_cases.sqlite_store import (
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
