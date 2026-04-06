#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Schema-management class for CUHK dictionary SQLite data."""

from __future__ import annotations

import sqlite3
from logging import getLogger

__all__ = [
    "CuhkSQLiteSchemaManager",
]

logger = getLogger(__name__)


class CuhkSQLiteSchemaManager:
    """Schema manager for CUHK dictionary SQLite tables."""

    @staticmethod
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
        try:
            cursor.execute(
                "CREATE VIRTUAL TABLE entries_fts USING fts5(pinyin, jyutping)"
            )
        except sqlite3.OperationalError as exc:
            if CuhkSQLiteSchemaManager._is_missing_fts5(exc):
                logger.warning(
                    "SQLite FTS5 unavailable; continuing without "
                    f"entries_fts index: {exc}"
                )
            else:
                raise

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
        try:
            cursor.execute(
                """CREATE VIRTUAL TABLE definitions_fts
                   USING fts5(fk_entry_id UNINDEXED, definition)"""
            )
        except sqlite3.OperationalError as exc:
            if CuhkSQLiteSchemaManager._is_missing_fts5(exc):
                logger.warning(
                    "SQLite FTS5 unavailable; "
                    f"continuing without definitions_fts index: {exc}"
                )
            else:
                raise

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

    @staticmethod
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

    @staticmethod
    def generate_indices(cursor: sqlite3.Cursor):
        """Generate search indices for dictionary tables.

        Arguments:
            cursor: sqlite cursor
        """
        try:
            cursor.execute(
                """INSERT INTO entries_fts (rowid, pinyin, jyutping)
                   SELECT rowid, pinyin, jyutping FROM entries"""
            )
        except sqlite3.OperationalError as exc:
            if CuhkSQLiteSchemaManager._is_missing_fts5(exc):
                logger.warning(
                    "Skipping entries_fts population because FTS5 is "
                    f"unavailable: {exc}"
                )
            else:
                raise
        try:
            cursor.execute(
                """INSERT INTO definitions_fts (rowid, fk_entry_id, definition)
                   SELECT rowid, fk_entry_id, definition FROM definitions"""
            )
        except sqlite3.OperationalError as exc:
            if CuhkSQLiteSchemaManager._is_missing_fts5(exc):
                logger.warning(
                    "Skipping definitions_fts population because "
                    f"FTS5 is unavailable: {exc}"
                )
            else:
                raise
        cursor.execute("CREATE INDEX fk_entry_id_index ON definitions(fk_entry_id)")

    @staticmethod
    def write_database_version(cursor: sqlite3.Cursor, version: int = 3):
        """Write schema version.

        Arguments:
            cursor: sqlite cursor
            version: schema version integer
        """
        cursor.execute(f"PRAGMA user_version={version}")

    @staticmethod
    def _is_missing_fts5(exc: sqlite3.OperationalError) -> bool:
        """Check whether an OperationalError indicates unavailable FTS5 support.

        Arguments:
            exc: sqlite operational error
        Returns:
            whether error indicates missing FTS5 support
        """
        message = str(exc).lower()
        if "fts5" in message or "no such module" in message:
            return True
        return "no such table" in message and "_fts" in message
