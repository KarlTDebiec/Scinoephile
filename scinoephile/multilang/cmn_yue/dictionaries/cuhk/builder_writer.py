#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Database-writing mixin for CUHK dictionary builder."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ..dictionary_entry import DictionaryEntry
from .builder_constants import CUHK_SOURCE
from .sqlite_schema_manager import CuhkSQLiteSchemaManager
from .sqlite_schema_records import CuhkSQLiteSchemaRecords

__all__ = [
    "CuhkDictionaryBuilderWriterMixin",
]


class CuhkDictionaryBuilderWriterMixin:
    """Mixin containing SQLite persistence behavior."""

    cache_dir_path: Path
    database_path: Path

    def write_database(self, entries: list[DictionaryEntry]):
        """Write entries to SQLite.

        Arguments:
            entries: normalized dictionary entries
        """
        self.cache_dir_path.mkdir(parents=True, exist_ok=True)
        if self.database_path.exists():
            self.database_path.unlink()

        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()

            CuhkSQLiteSchemaManager.write_database_version(cursor)
            CuhkSQLiteSchemaManager.drop_tables(cursor)
            CuhkSQLiteSchemaManager.create_tables(cursor)

            source_id = CuhkSQLiteSchemaRecords.insert_source(cursor, CUHK_SOURCE)

            for entry in entries:
                entry_id = CuhkSQLiteSchemaRecords.insert_entry(
                    cursor,
                    entry.traditional,
                    entry.simplified,
                    entry.pinyin,
                    entry.jyutping,
                    entry.frequency,
                )

                for definition in entry.definitions:
                    CuhkSQLiteSchemaRecords.insert_definition(
                        cursor,
                        definition.text,
                        definition.label,
                        entry_id,
                        source_id,
                    )

            CuhkSQLiteSchemaManager.generate_indices(cursor)
            connection.commit()
