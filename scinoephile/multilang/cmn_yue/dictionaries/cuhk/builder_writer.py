#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Database-writing helpers for CUHK dictionary builder."""

from __future__ import annotations

import sqlite3
from logging import getLogger
from pathlib import Path

from scinoephile.multilang.cmn_yue.dictionaries.dictionary_entry import (
    DictionaryEntry,
)
from scinoephile.multilang.cmn_yue.dictionaries.dictionary_source import (
    DictionarySource,
)

from .sqlite_schema_manager import CuhkSQLiteSchemaManager
from .sqlite_schema_records import CuhkSQLiteSchemaRecords

__all__ = [
    "CuhkDictionaryBuilderWriter",
]

logger = getLogger(__name__)

CUHK_SOURCE = DictionarySource(
    name="現代標準漢語與粵語對照資料庫",
    shortname="CUHK",
    version="2014",
    description=(
        "Comparative Database of Modern Standard Chinese and Cantonese "
        "(Chinese University of Hong Kong)."
    ),
    legal="(c) 2014 保留版權 香港中文大學 中國語言及文學系",
    link="https://apps.itsc.cuhk.edu.hk/hanyu/Page/Cover.aspx",
    update_url="",
    other="words",
)


class CuhkDictionaryBuilderWriter:
    """Helper object for SQLite persistence behavior."""

    def __init__(self, cache_dir_path: Path, database_path: Path):
        """Initialize.

        Arguments:
            cache_dir_path: cache directory path
            database_path: SQLite database path
        """
        self.cache_dir_path = cache_dir_path
        self.database_path = database_path

    def write_database(self, entries: list[DictionaryEntry]):
        """Write entries to SQLite.

        Arguments:
            entries: normalized dictionary entries
        """
        self.cache_dir_path.mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        if self.database_path.exists():
            logger.info(f"Deleting existing CUHK SQLite database: {self.database_path}")
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
