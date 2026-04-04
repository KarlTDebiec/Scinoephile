#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Record-level helper class for CUHK dictionary SQLite data."""

from __future__ import annotations

import sqlite3

from scinoephile.multilang.cmn_yue.dictionaries.dictionary_source import (
    DictionarySource,
)

__all__ = [
    "CuhkSQLiteSchemaRecords",
]


class CuhkSQLiteSchemaRecords:
    """Record helpers for CUHK dictionary SQLite tables."""

    @staticmethod
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

    @staticmethod
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
            "INSERT INTO entries "
            "(traditional, simplified, pinyin, jyutping, frequency) "
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

    @staticmethod
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
            "WHERE definition = ? AND label = ? "
            "AND fk_entry_id = ? AND fk_source_id = ?",
            (definition, label, entry_id, source_id),
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError("Failed to insert or load existing definition")
        return int(row[0])

    @staticmethod
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
        _ = frequency
        cursor.execute(
            "SELECT entry_id FROM entries "
            "WHERE traditional = ? AND simplified = ? AND pinyin = ? AND jyutping = ?",
            (traditional, simplified, pinyin, jyutping),
        )
        row = cursor.fetchone()
        return None if row is None else int(row[0])
