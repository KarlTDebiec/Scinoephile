#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared SQLite persistence and lookup for dictionary data."""

from __future__ import annotations

import sqlite3
from logging import getLogger
from pathlib import Path

from scinoephile.common.validation import val_output_path

from .dictionary_definition import DictionaryDefinition
from .dictionary_entry import DictionaryEntry
from .dictionary_source import DictionarySource
from .lookup_direction import LookupDirection

__all__ = [
    "DictionarySqliteStore",
]

logger = getLogger(__name__)


class DictionarySqliteStore:
    """SQLite schema, persistence, and lookup for dictionary data."""

    def __init__(self, database_path: Path):
        """Initialize.

        Arguments:
            database_path: SQLite database path
        """
        self.database_path = val_output_path(database_path, exist_ok=True)

    def lookup(
        self,
        query: str,
        direction: LookupDirection,
        limit: int,
    ) -> list[DictionaryEntry]:
        """Lookup entries from the persisted dictionary data.

        Arguments:
            query: query string
            direction: lookup direction
            limit: max results
        Returns:
            dictionary entries
        """
        if direction == LookupDirection.CMN_TO_YUE:
            return self._lookup_cmn_to_yue(query, limit)
        return self._lookup_yue_to_cmn(query, limit)

    def lookup_by_jyutping(self, query: str, limit: int) -> list[DictionaryEntry]:
        """Lookup entries by Jyutping.

        Arguments:
            query: query string
            limit: max results
        Returns:
            dictionary entries
        """
        like_query = f"%{self._get_escaped_query(query)}%"

        sql = """
            SELECT
                e.entry_id
            FROM entries AS e
            WHERE e.jyutping = ?
               OR e.jyutping LIKE ? ESCAPE '\\'
            GROUP BY e.entry_id
            ORDER BY
                CASE
                    WHEN e.jyutping = ? THEN 0
                    ELSE 1
                END,
                LENGTH(e.traditional),
                e.entry_id
            LIMIT ?
        """
        params: tuple[str | int, ...] = (
            query,
            like_query,
            query,
            limit,
        )
        entry_ids = self._select_entry_ids(sql, params)
        return self._fetch_entries(entry_ids)

    def lookup_by_pinyin(self, query: str, limit: int) -> list[DictionaryEntry]:
        """Lookup entries by pinyin.

        Arguments:
            query: query string
            limit: max results
        Returns:
            dictionary entries
        """
        like_query = f"%{self._get_escaped_query(query)}%"

        sql = """
            SELECT
                e.entry_id
            FROM entries AS e
            WHERE e.pinyin = ?
               OR e.pinyin LIKE ? ESCAPE '\\'
            GROUP BY e.entry_id
            ORDER BY
                CASE
                    WHEN e.pinyin = ? THEN 0
                    ELSE 1
                END,
                LENGTH(e.traditional),
                e.entry_id
            LIMIT ?
        """
        params: tuple[str | int, ...] = (
            query,
            like_query,
            query,
            limit,
        )
        entry_ids = self._select_entry_ids(sql, params)
        return self._fetch_entries(entry_ids)

    def lookup_by_simplified(self, query: str, limit: int) -> list[DictionaryEntry]:
        """Lookup entries by simplified Chinese headword.

        Arguments:
            query: query string
            limit: max results
        Returns:
            dictionary entries
        """
        sql = """
            SELECT
                e.entry_id
            FROM entries AS e
            WHERE e.simplified = ?
            GROUP BY e.entry_id
            ORDER BY
                LENGTH(e.traditional),
                e.entry_id
            LIMIT ?
        """
        params: tuple[str | int, ...] = (
            query,
            limit,
        )
        entry_ids = self._select_entry_ids(sql, params)
        return self._fetch_entries(entry_ids)

    def lookup_by_traditional(self, query: str, limit: int) -> list[DictionaryEntry]:
        """Lookup entries by traditional Chinese headword.

        Arguments:
            query: query string
            limit: max results
        Returns:
            dictionary entries
        """
        sql = """
            SELECT
                e.entry_id
            FROM entries AS e
            WHERE e.traditional = ?
            GROUP BY e.entry_id
            ORDER BY
                LENGTH(e.traditional),
                e.entry_id
            LIMIT ?
        """
        params: tuple[str | int, ...] = (
            query,
            limit,
        )
        entry_ids = self._select_entry_ids(sql, params)
        return self._fetch_entries(entry_ids)

    def persist(
        self,
        source_data: tuple[DictionarySource, list[DictionaryEntry]],
    ) -> Path:
        """Persist dictionary data to SQLite.

        Arguments:
            source_data: source metadata and normalized dictionary entries
        Returns:
            SQLite database path
        """
        source, entries = source_data
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        if self.database_path.exists():
            logger.info(f"Deleting existing SQLite database: {self.database_path}")
            self.database_path.unlink()

        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()

            self._write_database_version(cursor)
            self._drop_tables(cursor)
            self._create_tables(cursor)

            source_id = self._insert_source(cursor, source)
            for entry in entries:
                entry_id = self._insert_entry(
                    cursor,
                    entry.traditional,
                    entry.simplified,
                    entry.pinyin,
                    entry.jyutping,
                    entry.frequency,
                )
                for definition in entry.definitions:
                    self._insert_definition(
                        cursor,
                        definition.text,
                        definition.label,
                        entry_id,
                        source_id,
                    )

            self._generate_indices(cursor)
            connection.commit()

        return self.database_path

    @staticmethod
    def _aggregate_rows(rows: list[sqlite3.Row]) -> list[DictionaryEntry]:
        """Aggregate joined rows into dictionary entries.

        Arguments:
            rows: joined entry and definition rows
        Returns:
            dictionary entries
        """
        aggregated: dict[int, DictionaryEntry] = {}
        definitions_map: dict[int, list[DictionaryDefinition]] = {}

        for row in rows:
            entry_id = int(row["entry_id"])
            if entry_id not in aggregated:
                aggregated[entry_id] = DictionaryEntry(
                    traditional=str(row["traditional"]),
                    simplified=str(row["simplified"]),
                    pinyin=str(row["pinyin"]),
                    jyutping=str(row["jyutping"]),
                    frequency=float(row["frequency"] or 0.0),
                    definitions=[],
                )
                definitions_map[entry_id] = []

            definition = row["definition"]
            label = row["label"]
            if definition is not None:
                definitions_map[entry_id].append(
                    DictionaryDefinition(
                        text=str(definition),
                        label="" if label is None else str(label),
                    )
                )

        output: list[DictionaryEntry] = []
        for entry_id, entry in aggregated.items():
            output.append(
                DictionaryEntry(
                    traditional=entry.traditional,
                    simplified=entry.simplified,
                    pinyin=entry.pinyin,
                    jyutping=entry.jyutping,
                    frequency=entry.frequency,
                    definitions=definitions_map[entry_id],
                )
            )
        return output

    @staticmethod
    def _get_escaped_query(query: str) -> str:
        """Escape a query string for literal LIKE matching.

        Arguments:
            query: raw query text
        Returns:
            escaped query string
        """
        return query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    def _create_tables(self, cursor: sqlite3.Cursor):
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
            if self._is_missing_fts5(exc):
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
            if self._is_missing_fts5(exc):
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

    def _drop_tables(self, cursor: sqlite3.Cursor):
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

    def _fetch_entries(
        self,
        entry_ids: list[int],
    ) -> list[DictionaryEntry]:
        """Fetch entry rows and definitions for selected entry IDs.

        Arguments:
            entry_ids: ordered entry identifiers
        Returns:
            dictionary entries
        """
        if not entry_ids:
            return []

        in_placeholders = ", ".join("?" for _ in entry_ids)
        case_clauses = " ".join(
            f"WHEN ? THEN {rank}" for rank, _ in enumerate(entry_ids)
        )
        params = tuple([*entry_ids, *entry_ids])

        sql = f"""
            SELECT
                e.entry_id,
                e.traditional,
                e.simplified,
                e.pinyin,
                e.jyutping,
                e.frequency,
                d.label,
                d.definition
            FROM entries AS e
            LEFT JOIN definitions AS d
                ON d.fk_entry_id = e.entry_id
            WHERE e.entry_id IN ({in_placeholders})
            ORDER BY
                CASE e.entry_id
                    {case_clauses}
                    ELSE {len(entry_ids)}
                END,
                d.definition_id
        """
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(sql, params).fetchall()

        return self._aggregate_rows(rows)

    def _generate_indices(self, cursor: sqlite3.Cursor):
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
            if self._is_missing_fts5(exc):
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
            if self._is_missing_fts5(exc):
                logger.warning(
                    "Skipping definitions_fts population because "
                    f"FTS5 is unavailable: {exc}"
                )
            else:
                raise
        cursor.execute("CREATE INDEX fk_entry_id_index ON definitions(fk_entry_id)")

    @staticmethod
    def _insert_definition(
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
            """INSERT INTO definitions (
                   definition,
                   label,
                   fk_entry_id,
                   fk_source_id
               ) VALUES (?, ?, ?, ?)""",
            (definition, label, entry_id, source_id),
        )
        if cursor.rowcount == 1:
            definition_id = cursor.lastrowid
            if definition_id is None:
                raise RuntimeError("Failed to insert definition")
            return int(definition_id)

        cursor.execute(
            """SELECT definition_id FROM definitions
               WHERE definition = ?
                 AND label = ?
                 AND fk_entry_id = ?
                 AND fk_source_id = ?""",
            (definition, label, entry_id, source_id),
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError("Failed to insert or load existing definition")
        return int(row[0])

    @staticmethod
    def _insert_entry(
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
            """INSERT INTO entries (
                   traditional,
                   simplified,
                   pinyin,
                   jyutping,
                   frequency
               ) VALUES (?, ?, ?, ?, ?)""",
            (traditional, simplified, pinyin, jyutping, frequency),
        )
        if cursor.rowcount == 1:
            entry_id = cursor.lastrowid
            if entry_id is None:
                raise RuntimeError("Failed to insert entry")
            return int(entry_id)

        cursor.execute(
            """SELECT entry_id FROM entries
               WHERE traditional = ?
                 AND simplified = ?
                 AND pinyin = ?
                 AND jyutping = ?""",
            (traditional, simplified, pinyin, jyutping),
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError("Failed to insert or load existing entry")
        return int(row[0])

    @staticmethod
    def _insert_source(cursor: sqlite3.Cursor, source: DictionarySource) -> int:
        """Insert a source and return its identifier.

        Arguments:
            cursor: sqlite cursor
            source: source metadata
        Returns:
            source identifier
        """
        cursor.execute(
            """INSERT INTO sources (
                   sourcename,
                   sourceshortname,
                   version,
                   description,
                   legal,
                   link,
                   update_url,
                   other
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
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
        return int(source_id)

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

    def _lookup_cmn_to_yue(self, query: str, limit: int) -> list[DictionaryEntry]:
        """Lookup Mandarin query terms in dictionary data.

        Arguments:
            query: query string
            limit: max results
        Returns:
            dictionary entries
        """
        like_query = f"%{self._get_escaped_query(query)}%"

        sql = """
            SELECT
                e.entry_id
            FROM entries AS e
            LEFT JOIN definitions AS d
                ON d.fk_entry_id = e.entry_id
            WHERE e.simplified = ?
               OR e.traditional = ?
               OR e.pinyin LIKE ? ESCAPE '\\'
               OR d.definition LIKE ? ESCAPE '\\'
            GROUP BY e.entry_id
            ORDER BY
                CASE
                    WHEN e.simplified = ? THEN 0
                    WHEN e.traditional = ? THEN 1
                    WHEN e.pinyin = ? THEN 2
                    ELSE 3
                END,
                LENGTH(e.traditional),
                e.entry_id
            LIMIT ?
        """
        params: tuple[str | int, ...] = (
            query,
            query,
            like_query,
            like_query,
            query,
            query,
            query,
            limit,
        )
        entry_ids = self._select_entry_ids(sql, params)
        return self._fetch_entries(entry_ids)

    def _lookup_yue_to_cmn(
        self,
        query: str,
        limit: int,
    ) -> list[DictionaryEntry]:
        """Lookup Cantonese query terms in dictionary data.

        Arguments:
            query: query string
            limit: max results
        Returns:
            dictionary entries
        """
        like_query = f"%{self._get_escaped_query(query)}%"

        sql = """
            SELECT
                e.entry_id
            FROM entries AS e
            WHERE e.jyutping = ?
               OR e.jyutping LIKE ? ESCAPE '\\'
               OR e.traditional = ?
               OR e.simplified = ?
            GROUP BY e.entry_id
            ORDER BY
                CASE
                    WHEN e.jyutping = ? THEN 0
                    WHEN e.traditional = ? THEN 1
                    WHEN e.simplified = ? THEN 2
                    ELSE 3
                END,
                LENGTH(e.traditional),
                e.entry_id
            LIMIT ?
        """
        params: tuple[str | int, ...] = (
            query,
            like_query,
            query,
            query,
            query,
            query,
            query,
            limit,
        )
        entry_ids = self._select_entry_ids(sql, params)
        return self._fetch_entries(entry_ids)

    def _select_entry_ids(
        self,
        sql: str,
        params: tuple[str | int, ...],
    ) -> list[int]:
        """Run entry selection query.

        Arguments:
            sql: SQL query that returns entry_id
            params: SQL parameters
        Returns:
            ordered entry identifiers
        """
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(sql, params).fetchall()
        return [int(row["entry_id"]) for row in rows]

    @staticmethod
    def _write_database_version(cursor: sqlite3.Cursor, version: int = 3):
        """Write schema version.

        Arguments:
            cursor: sqlite cursor
            version: schema version integer
        """
        cursor.execute(f"PRAGMA user_version={version}")
