#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.dictionaries.DictionarySqliteStore."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from pytest import fixture, raises

from scinoephile.core.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
    DictionarySqliteStore,
)


@fixture
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


@fixture
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

    with closing(sqlite3.connect(database_path)) as connection:
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


def test_sqlite_store_literal_like_lookups(
    database_path: Path,
    sample_source: DictionarySource,
):
    """Test literal matching of LIKE wildcard characters in romanization."""
    entries = [
        DictionaryEntry(
            traditional="百分號",
            simplified="百分号",
            pinyin="percent% sign",
            jyutping="percent% sign",
            definitions=[DictionaryDefinition(text="percent sign")],
        ),
        DictionaryEntry(
            traditional="底線",
            simplified="底线",
            pinyin="under_score",
            jyutping="under_score",
            definitions=[DictionaryDefinition(text="underscore")],
        ),
        DictionaryEntry(
            traditional="反斜線",
            simplified="反斜线",
            pinyin=r"back\\slash",
            jyutping=r"back\\slash",
            definitions=[DictionaryDefinition(text="backslash")],
        ),
    ]
    store = DictionarySqliteStore(database_path=database_path)
    store.persist((sample_source, entries))

    assert store.lookup_by_pinyin("%", limit=5) == [entries[0]]
    assert store.lookup_by_pinyin("_", limit=5) == [entries[1]]
    assert store.lookup_by_pinyin("\\", limit=5) == [entries[2]]
    assert store.lookup_by_jyutping("%", limit=5) == [entries[0]]
    assert store.lookup_by_jyutping("_", limit=5) == [entries[1]]
    assert store.lookup_by_jyutping("\\", limit=5) == [entries[2]]


def test_sqlite_store_preserves_existing_database_when_rebuild_fails(
    database_path: Path,
    sample_entries: list[DictionaryEntry],
    sample_source: DictionarySource,
):
    """Test a failed rebuild leaves the existing database unchanged."""
    store = DictionarySqliteStore(database_path=database_path)
    store.persist((sample_source, sample_entries))
    original_database = database_path.read_bytes()

    with (
        patch.object(
            store,
            "_generate_indices",
            side_effect=RuntimeError("index generation failed"),
        ),
        raises(RuntimeError, match="index generation failed"),
    ):
        store.persist((sample_source, sample_entries[:1]))

    assert database_path.read_bytes() == original_database
    assert store.lookup_by_traditional("山坑水", limit=5) == [sample_entries[1]]
    assert list(database_path.parent.glob(f".{database_path.name}.*")) == []


def test_sqlite_store_collapses_duplicate_entries_and_definitions(
    database_path: Path,
    sample_source: DictionarySource,
):
    """Test duplicate entries and definitions collapse through uniqueness rules."""
    definition = DictionaryDefinition(text="duplicate definition", label="noun")
    duplicate = DictionaryEntry(
        traditional="重複",
        simplified="重复",
        pinyin="chong2 fu4",
        jyutping="cung4 fuk1",
        frequency=1.0,
        definitions=[definition, definition],
    )
    store = DictionarySqliteStore(database_path=database_path)
    store.persist((sample_source, [duplicate, duplicate]))

    assert store.lookup_by_traditional("重複", limit=5) == [
        DictionaryEntry(
            traditional="重複",
            simplified="重复",
            pinyin="chong2 fu4",
            jyutping="cung4 fuk1",
            frequency=1.0,
            definitions=[definition],
        )
    ]
