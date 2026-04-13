#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.multilang.dictionaries.DictionarySqliteStore."""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from pathlib import Path

import pytest

from scinoephile.common.file import get_temp_file_path
from scinoephile.multilang.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
    DictionarySqliteStore,
)


@pytest.fixture
def database_path() -> Generator[Path]:
    """Provide a temporary SQLite database path."""
    with get_temp_file_path(".db") as temp_path:
        yield temp_path


@pytest.fixture
def sample_entries() -> list[DictionaryEntry]:
    """Provide deterministic dictionary entries for SQLite tests."""
    return [
        DictionaryEntry(
            traditional="山坑",
            simplified="山坑",
            pinyin="shan1 keng1",
            jyutping="saan1 haang1",
            frequency=2.0,
            definitions=[
                DictionaryDefinition(text="gully"),
                DictionaryDefinition(text="mountain stream", label="noun"),
            ],
        ),
        DictionaryEntry(
            traditional="山坑水",
            simplified="山坑水",
            pinyin="shan1 keng1 shui3",
            jyutping="saan1 haang1 seoi2",
            frequency=1.0,
            definitions=[
                DictionaryDefinition(text="stream water"),
            ],
        ),
    ]


@pytest.fixture
def sample_source() -> DictionarySource:
    """Provide deterministic dictionary source metadata."""
    return DictionarySource(
        name="Test Dictionary",
        shortname="test",
        version="2026.04",
        description="Dictionary source used for SQLite tests.",
        legal="BSD",
        link="https://example.com/dictionary",
        update_url="https://example.com/dictionary/update",
        other="fixture",
    )


def test_sqlite_store_field_lookups(
    database_path: Path,
    sample_entries: list[DictionaryEntry],
    sample_source: DictionarySource,
):
    """Test direct field-specific SQLite lookup helpers."""
    store = DictionarySqliteStore(database_path=database_path)
    store.persist((sample_source, sample_entries))

    assert store.lookup_by_traditional("山坑", limit=5) == [sample_entries[0]]
    assert store.lookup_by_simplified("山坑", limit=5) == [sample_entries[0]]
    assert store.lookup_by_pinyin("shan1 keng1", limit=5) == [
        sample_entries[0],
        sample_entries[1],
    ]
    assert store.lookup_by_jyutping("saan1 haang1", limit=5) == [
        sample_entries[0],
        sample_entries[1],
    ]


def test_sqlite_store_preserves_expected_schema(
    database_path: Path,
    sample_entries: list[DictionaryEntry],
    sample_source: DictionarySource,
):
    """Test SQLite schema compatibility details are preserved."""
    store = DictionarySqliteStore(database_path=database_path)
    store.persist((sample_source, sample_entries))

    with sqlite3.connect(database_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        user_version = connection.execute("PRAGMA user_version").fetchone()[0]

    assert {
        "chinese_sentences",
        "definitions",
        "definitions_chinese_sentences_links",
        "definitions_fts",
        "entries",
        "entries_fts",
        "nonchinese_sentences",
        "sentence_links",
        "sources",
    }.issubset(table_names)
    assert user_version == 3
