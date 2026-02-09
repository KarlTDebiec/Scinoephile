#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""SQLite schema helpers for dictionary imports.

The core table layout is intentionally close to the schema used in
`external/jyut-dict/src/dictionaries/database/database.py` so that future
dictionary ports can reuse this storage layer with minimal translation.
"""

from __future__ import annotations

import sqlite3

from .models import DictionarySource

__all__ = [
    "create_tables",
    "drop_tables",
    "generate_indices",
    "get_entry_id",
    "insert_definition",
    "insert_entry",
    "insert_source",
    "write_database_version",
]


def create_tables(cursor: sqlite3.Cursor):
    """Create dictionary tables.

    Arguments:
        cursor: sqlite cursor
    """
    cursor.execute(
        """CREATE TABLE entries(
                entry_id INTEGER PRIMARY KEY,
                traditional TEXT,
                simplified TEXT,
                pinyin TEXT,
                jyutping TEXT,
                frequency REAL,
                UNIQUE(traditional, simplified, pinyin, jyutping)
                    ON CONFLICT IGNORE
            )"""
    )
    cursor.execute("CREATE VIRTUAL TABLE entries_fts USING fts5(pinyin, jyutping)")

    cursor.execute(
        """CREATE TABLE sources(
                source_id INTEGER PRIMARY KEY,
                sourcename TEXT UNIQUE ON CONFLICT ABORT,
                sourceshortname TEXT,
                version TEXT,
                description TEXT,
                legal TEXT,
                link TEXT,
                update_url TEXT,
                other TEXT
            )"""
    )

    cursor.execute(
        """CREATE TABLE definitions(
                definition_id INTEGER PRIMARY KEY,
                definition TEXT,
                label TEXT,
                fk_entry_id INTEGER,
                fk_source_id INTEGER,
                FOREIGN KEY(fk_entry_id) REFERENCES entries(entry_id)
                    ON UPDATE CASCADE,
                FOREIGN KEY(fk_source_id) REFERENCES sources(source_id)
                    ON DELETE CASCADE,
                UNIQUE(definition, label, fk_entry_id, fk_source_id)
                    ON CONFLICT IGNORE
            )"""
    )
    cursor.execute(
        "CREATE VIRTUAL TABLE definitions_fts "
        "USING fts5(fk_entry_id UNINDEXED, definition)"
    )

    # The following tables are retained for schema-compatibility with jyut-dict.
    cursor.execute(
        """CREATE TABLE chinese_sentences(
                chinese_sentence_id INTEGER PRIMARY KEY ON CONFLICT IGNORE,
                traditional TEXT,
                simplified TEXT,
                pinyin TEXT,
                jyutping TEXT,
                language TEXT,
                UNIQUE(traditional, simplified, pinyin, jyutping, language)
                    ON CONFLICT IGNORE
            )"""
    )
    cursor.execute(
        """CREATE TABLE nonchinese_sentences(
                non_chinese_sentence_id INTEGER PRIMARY KEY ON CONFLICT IGNORE,
                sentence TEXT,
                language TEXT,
                UNIQUE(non_chinese_sentence_id, sentence)
                    ON CONFLICT IGNORE
            )"""
    )
    cursor.execute(
        """CREATE TABLE sentence_links(
                fk_chinese_sentence_id INTEGER,
                fk_non_chinese_sentence_id INTEGER,
                fk_source_id INTEGER,
                direct BOOLEAN,
                FOREIGN KEY(fk_chinese_sentence_id)
                    REFERENCES chinese_sentences(chinese_sentence_id),
                FOREIGN KEY(fk_non_chinese_sentence_id)
                    REFERENCES nonchinese_sentences(non_chinese_sentence_id),
                FOREIGN KEY(fk_source_id)
                    REFERENCES sources(source_id) ON DELETE CASCADE,
                UNIQUE(fk_chinese_sentence_id, fk_non_chinese_sentence_id)
                    ON CONFLICT IGNORE
            )"""
    )
    cursor.execute(
        """CREATE TABLE definitions_chinese_sentences_links(
                fk_definition_id INTEGER,
                fk_chinese_sentence_id INTEGER,
                FOREIGN KEY(fk_definition_id)
                    REFERENCES definitions(definition_id) ON DELETE CASCADE,
                FOREIGN KEY(fk_chinese_sentence_id)
                    REFERENCES chinese_sentences(chinese_sentence_id),
                UNIQUE(fk_definition_id, fk_chinese_sentence_id)
                    ON CONFLICT IGNORE
            )"""
    )


def drop_tables(cursor: sqlite3.Cursor):
    """Drop dictionary tables.

    Arguments:
        cursor: sqlite cursor
    """
    cursor.execute("DROP TABLE IF EXISTS entries")
    cursor.execute("DROP TABLE IF EXISTS entries_fts")
    cursor.execute("DROP TABLE IF EXISTS sources")
    cursor.execute("DROP TABLE IF EXISTS definitions")
    cursor.execute("DROP TABLE IF EXISTS definitions_fts")
    cursor.execute("DROP INDEX IF EXISTS fk_entry_id_index")

    cursor.execute("DROP TABLE IF EXISTS chinese_sentences")
    cursor.execute("DROP TABLE IF EXISTS nonchinese_sentences")
    cursor.execute("DROP TABLE IF EXISTS sentence_links")

    cursor.execute("DROP TABLE IF EXISTS definitions_chinese_sentences_links")


def write_database_version(cursor: sqlite3.Cursor, version: int = 3):
    """Write schema version.

    Arguments:
        cursor: sqlite cursor
        version: schema version integer
    """
    cursor.execute(f"PRAGMA user_version={version}")


def generate_indices(cursor: sqlite3.Cursor):
    """Generate search indices for dictionary tables.

    Arguments:
        cursor: sqlite cursor
    """
    cursor.execute(
        "INSERT INTO entries_fts (rowid, pinyin, jyutping) "
        "SELECT rowid, pinyin, jyutping FROM entries"
    )
    cursor.execute(
        "INSERT INTO definitions_fts (rowid, fk_entry_id, definition) "
        "SELECT rowid, fk_entry_id, definition FROM definitions"
    )
    cursor.execute("CREATE INDEX fk_entry_id_index ON definitions(fk_entry_id)")


def insert_source(cursor: sqlite3.Cursor, source: DictionarySource) -> int:
    """Insert a source and return its identifier.

    Arguments:
        cursor: sqlite cursor
        source: source metadata
    Returns:
        source identifier
    """
    cursor.execute(
        "INSERT INTO sources ("
        "sourcename, sourceshortname, version, description, legal, link, "
        "update_url, other"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            source.name,
            source.shortname,
            source.version,
            source.description,
            source.legal,
            source.link,
            source.update_url,
            source.other,
        ),
    )
    source_id = cursor.lastrowid
    if source_id is None:
        raise RuntimeError("Failed to insert source")
    return source_id


def insert_entry(
    cursor: sqlite3.Cursor,
    traditional: str,
    simplified: str,
    pinyin: str,
    jyutping: str,
    frequency: float,
) -> int:
    """Insert a dictionary entry and return its identifier.

    Arguments:
        cursor: sqlite cursor
        traditional: traditional Chinese text
        simplified: simplified Chinese text
        pinyin: pinyin pronunciation
        jyutping: jyutping pronunciation
        frequency: frequency score
    Returns:
        entry identifier
    """
    cursor.execute(
        "INSERT INTO entries (traditional, simplified, pinyin, jyutping, frequency) "
        "VALUES (?, ?, ?, ?, ?)",
        (traditional, simplified, pinyin, jyutping, frequency),
    )
    if cursor.rowcount == 1:
        entry_id = cursor.lastrowid
        if entry_id is None:
            raise RuntimeError("Failed to insert entry")
        return int(entry_id)

    cursor.execute(
        "SELECT entry_id FROM entries "
        "WHERE traditional = ? AND simplified = ? AND pinyin = ? AND jyutping = ?",
        (traditional, simplified, pinyin, jyutping),
    )
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError("Failed to insert or load existing entry")
    return int(row[0])


def insert_definition(
    cursor: sqlite3.Cursor,
    definition: str,
    label: str,
    entry_id: int,
    source_id: int,
) -> int:
    """Insert a dictionary definition and return its identifier.

    Arguments:
        cursor: sqlite cursor
        definition: definition text
        label: definition label
        entry_id: related entry identifier
        source_id: related source identifier
    Returns:
        definition identifier
    """
    cursor.execute(
        "INSERT INTO definitions (definition, label, fk_entry_id, fk_source_id) "
        "VALUES (?, ?, ?, ?)",
        (definition, label, entry_id, source_id),
    )
    if cursor.rowcount == 1:
        definition_id = cursor.lastrowid
        if definition_id is None:
            raise RuntimeError("Failed to insert definition")
        return int(definition_id)

    cursor.execute(
        "SELECT definition_id FROM definitions "
        "WHERE definition = ? AND label = ? AND fk_entry_id = ? AND fk_source_id = ?",
        (definition, label, entry_id, source_id),
    )
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError("Failed to insert or load existing definition")
    return int(row[0])


def get_entry_id(
    cursor: sqlite3.Cursor,
    traditional: str,
    simplified: str,
    pinyin: str,
    jyutping: str,
    frequency: float,
) -> int | None:
    """Get an existing entry identifier if present.

    Arguments:
        cursor: sqlite cursor
        traditional: traditional Chinese text
        simplified: simplified Chinese text
        pinyin: pinyin pronunciation
        jyutping: jyutping pronunciation
        frequency: frequency score (unused for identity; retained for compatibility)
    Returns:
        existing entry identifier if found
    """
    cursor.execute(
        "SELECT entry_id FROM entries "
        "WHERE traditional = ? AND simplified = ? AND pinyin = ? AND jyutping = ?",
        (traditional, simplified, pinyin, jyutping),
    )
    row = cursor.fetchone()
    return None if row is None else int(row[0])
