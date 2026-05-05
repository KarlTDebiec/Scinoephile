#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared SQLite persistence and lookup for dictionary data."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Table,
    Text,
    UniqueConstraint,
    case,
    create_engine,
    func,
    select,
    text,
)
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import URL, Connection, RowMapping
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import Select

from scinoephile.common.validation import val_output_path

from .dictionary_definition import DictionaryDefinition
from .dictionary_entry import DictionaryEntry
from .dictionary_source import DictionarySource

__all__ = ["DictionarySqliteStore"]

logger = getLogger(__name__)


class DictionarySqliteStore:
    """SQLite schema, persistence, and lookup for dictionary data."""

    schema_version = 3
    """SQLite schema version."""

    _metadata = MetaData()
    """SQLAlchemy Core metadata for dictionary tables."""

    _entries = Table(
        "entries",
        _metadata,
        Column("entry_id", Integer, primary_key=True),
        Column("traditional", Text),
        Column("simplified", Text),
        Column("pinyin", Text),
        Column("jyutping", Text),
        Column("frequency", Float),
        UniqueConstraint(
            "traditional",
            "simplified",
            "pinyin",
            "jyutping",
            sqlite_on_conflict="IGNORE",
        ),
    )
    """Dictionary entry table."""

    _sources = Table(
        "sources",
        _metadata,
        Column("source_id", Integer, primary_key=True),
        Column("sourcename", Text, unique=True, sqlite_on_conflict_unique="ABORT"),
        Column("sourceshortname", Text),
        Column("version", Text),
        Column("description", Text),
        Column("legal", Text),
        Column("link", Text),
        Column("update_url", Text),
        Column("other", Text),
    )
    """Dictionary source metadata table."""

    _definitions = Table(
        "definitions",
        _metadata,
        Column("definition_id", Integer, primary_key=True),
        Column("definition", Text),
        Column("label", Text),
        Column(
            "fk_entry_id",
            Integer,
            ForeignKey("entries.entry_id", onupdate="CASCADE"),
        ),
        Column(
            "fk_source_id",
            Integer,
            ForeignKey("sources.source_id", ondelete="CASCADE"),
        ),
        UniqueConstraint(
            "definition",
            "label",
            "fk_entry_id",
            "fk_source_id",
            sqlite_on_conflict="IGNORE",
        ),
        Index("fk_entry_id_index", "fk_entry_id"),
    )
    """Dictionary definition table."""

    _chinese_sentences = Table(
        "chinese_sentences",
        _metadata,
        Column(
            "chinese_sentence_id",
            Integer,
            primary_key=True,
            sqlite_on_conflict_primary_key="IGNORE",
        ),
        Column("traditional", Text),
        Column("simplified", Text),
        Column("pinyin", Text),
        Column("jyutping", Text),
        Column("language", Text),
        UniqueConstraint(
            "traditional",
            "simplified",
            "pinyin",
            "jyutping",
            "language",
            sqlite_on_conflict="IGNORE",
        ),
    )
    """Chinese sentence compatibility table."""

    _nonchinese_sentences = Table(
        "nonchinese_sentences",
        _metadata,
        Column(
            "non_chinese_sentence_id",
            Integer,
            primary_key=True,
            sqlite_on_conflict_primary_key="IGNORE",
        ),
        Column("sentence", Text),
        Column("language", Text),
        UniqueConstraint(
            "non_chinese_sentence_id",
            "sentence",
            sqlite_on_conflict="IGNORE",
        ),
    )
    """Non-Chinese sentence compatibility table."""

    _sentence_links = Table(
        "sentence_links",
        _metadata,
        Column(
            "fk_chinese_sentence_id",
            Integer,
            ForeignKey("chinese_sentences.chinese_sentence_id"),
        ),
        Column(
            "fk_non_chinese_sentence_id",
            Integer,
            ForeignKey("nonchinese_sentences.non_chinese_sentence_id"),
        ),
        Column(
            "fk_source_id",
            Integer,
            ForeignKey("sources.source_id", ondelete="CASCADE"),
        ),
        Column("direct", Boolean),
        UniqueConstraint(
            "fk_chinese_sentence_id",
            "fk_non_chinese_sentence_id",
            sqlite_on_conflict="IGNORE",
        ),
    )
    """Sentence-link compatibility table."""

    _definitions_chinese_sentences_links = Table(
        "definitions_chinese_sentences_links",
        _metadata,
        Column(
            "fk_definition_id",
            Integer,
            ForeignKey("definitions.definition_id", ondelete="CASCADE"),
        ),
        Column(
            "fk_chinese_sentence_id",
            Integer,
            ForeignKey("chinese_sentences.chinese_sentence_id"),
        ),
        UniqueConstraint(
            "fk_definition_id",
            "fk_chinese_sentence_id",
            sqlite_on_conflict="IGNORE",
        ),
    )
    """Definition-to-sentence compatibility table."""

    def __init__(self, database_path: Path):
        """Initialize.

        Arguments:
            database_path: SQLite database path
        """
        self.database_path = val_output_path(database_path, exist_ok=True)
        self.engine = create_engine(
            URL.create("sqlite", database=str(self.database_path)),
            future=True,
            poolclass=NullPool,
        )

    def lookup_by_jyutping(self, query: str, limit: int) -> list[DictionaryEntry]:
        """Lookup entries by Jyutping.

        Arguments:
            query: query string
            limit: max results
        Returns:
            dictionary entries
        """
        like_query = f"%{self._get_escaped_query(query)}%"
        statement = (
            select(self._entries.c.entry_id)
            .where(
                (self._entries.c.jyutping == query)
                | self._entries.c.jyutping.like(like_query, escape="\\")
            )
            .group_by(self._entries.c.entry_id)
            .order_by(
                case((self._entries.c.jyutping == query, 0), else_=1),
                func.length(self._entries.c.traditional),
                self._entries.c.entry_id,
            )
            .limit(limit)
        )
        entry_ids = self._select_entry_ids(statement)
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
        statement = (
            select(self._entries.c.entry_id)
            .where(
                (self._entries.c.pinyin == query)
                | self._entries.c.pinyin.like(like_query, escape="\\")
            )
            .group_by(self._entries.c.entry_id)
            .order_by(
                case((self._entries.c.pinyin == query, 0), else_=1),
                func.length(self._entries.c.traditional),
                self._entries.c.entry_id,
            )
            .limit(limit)
        )
        entry_ids = self._select_entry_ids(statement)
        return self._fetch_entries(entry_ids)

    def lookup_by_simplified(self, query: str, limit: int) -> list[DictionaryEntry]:
        """Lookup entries by simplified Chinese headword.

        Arguments:
            query: query string
            limit: max results
        Returns:
            dictionary entries
        """
        statement = (
            select(self._entries.c.entry_id)
            .where(self._entries.c.simplified == query)
            .group_by(self._entries.c.entry_id)
            .order_by(
                func.length(self._entries.c.traditional), self._entries.c.entry_id
            )
            .limit(limit)
        )
        entry_ids = self._select_entry_ids(statement)
        return self._fetch_entries(entry_ids)

    def lookup_by_traditional(self, query: str, limit: int) -> list[DictionaryEntry]:
        """Lookup entries by traditional Chinese headword.

        Arguments:
            query: query string
            limit: max results
        Returns:
            dictionary entries
        """
        statement = (
            select(self._entries.c.entry_id)
            .where(self._entries.c.traditional == query)
            .group_by(self._entries.c.entry_id)
            .order_by(
                func.length(self._entries.c.traditional), self._entries.c.entry_id
            )
            .limit(limit)
        )
        entry_ids = self._select_entry_ids(statement)
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

        with self.engine.begin() as connection:
            self._write_database_version(connection)
            self._drop_tables(connection)
            self._create_tables(connection)

            source_id = self._insert_source(connection, source)
            for entry in entries:
                entry_id = self._insert_entry(connection, entry)
                for definition in entry.definitions:
                    self._insert_definition(connection, definition, entry_id, source_id)

            self._generate_indices(connection)

        return self.database_path

    @staticmethod
    def _aggregate_rows(rows: list[RowMapping]) -> list[DictionaryEntry]:
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

    def _create_tables(self, connection: Connection):
        """Create dictionary tables.

        Arguments:
            connection: SQLAlchemy connection
        """
        self._metadata.create_all(connection)
        try:
            connection.execute(
                text("CREATE VIRTUAL TABLE entries_fts USING fts5(pinyin, jyutping)")
            )
        except OperationalError as exc:
            if self._is_missing_fts5(exc):
                logger.warning(
                    "SQLite FTS5 unavailable; continuing without "
                    f"entries_fts index: {exc}"
                )
            else:
                raise

        try:
            connection.execute(
                text(
                    """CREATE VIRTUAL TABLE definitions_fts
                       USING fts5(fk_entry_id UNINDEXED, definition)"""
                )
            )
        except OperationalError as exc:
            if self._is_missing_fts5(exc):
                logger.warning(
                    "SQLite FTS5 unavailable; "
                    f"continuing without definitions_fts index: {exc}"
                )
            else:
                raise

    @staticmethod
    def _drop_tables(connection: Connection):
        """Drop dictionary tables.

        Arguments:
            connection: SQLAlchemy connection
        """
        connection.execute(text("DROP TABLE IF EXISTS entries_fts"))
        connection.execute(text("DROP TABLE IF EXISTS definitions_fts"))
        connection.execute(text("DROP INDEX IF EXISTS fk_entry_id_index"))

        connection.execute(
            text("DROP TABLE IF EXISTS definitions_chinese_sentences_links")
        )
        connection.execute(text("DROP TABLE IF EXISTS sentence_links"))
        connection.execute(text("DROP TABLE IF EXISTS definitions"))
        connection.execute(text("DROP TABLE IF EXISTS entries"))
        connection.execute(text("DROP TABLE IF EXISTS sources"))

        connection.execute(text("DROP TABLE IF EXISTS chinese_sentences"))
        connection.execute(text("DROP TABLE IF EXISTS nonchinese_sentences"))

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

        rank_by_id = {entry_id: rank for rank, entry_id in enumerate(entry_ids)}
        statement = (
            select(
                self._entries.c.entry_id,
                self._entries.c.traditional,
                self._entries.c.simplified,
                self._entries.c.pinyin,
                self._entries.c.jyutping,
                self._entries.c.frequency,
                self._definitions.c.label,
                self._definitions.c.definition,
            )
            .outerjoin(
                self._definitions,
                self._definitions.c.fk_entry_id == self._entries.c.entry_id,
            )
            .where(self._entries.c.entry_id.in_(entry_ids))
            .order_by(
                case(rank_by_id, value=self._entries.c.entry_id, else_=len(entry_ids)),
                self._definitions.c.definition_id,
            )
        )
        with self.engine.connect() as connection:
            rows = connection.execute(statement).mappings().all()

        return self._aggregate_rows(list(rows))

    @staticmethod
    def _generate_indices(connection: Connection):
        """Generate search indices for dictionary tables.

        Arguments:
            connection: SQLAlchemy connection
        """
        try:
            connection.execute(
                text(
                    """INSERT INTO entries_fts (rowid, pinyin, jyutping)
                       SELECT rowid, pinyin, jyutping FROM entries"""
                )
            )
        except OperationalError as exc:
            if DictionarySqliteStore._is_missing_fts5(exc):
                logger.warning(
                    "Skipping entries_fts population because FTS5 is "
                    f"unavailable: {exc}"
                )
            else:
                raise
        try:
            connection.execute(
                text(
                    """INSERT INTO definitions_fts (rowid, fk_entry_id, definition)
                       SELECT rowid, fk_entry_id, definition FROM definitions"""
                )
            )
        except OperationalError as exc:
            if DictionarySqliteStore._is_missing_fts5(exc):
                logger.warning(
                    "Skipping definitions_fts population because "
                    f"FTS5 is unavailable: {exc}"
                )
            else:
                raise

    @staticmethod
    def _insert_definition(
        connection: Connection,
        definition: DictionaryDefinition,
        entry_id: int,
        source_id: int,
    ) -> int:
        """Insert a dictionary definition and return its identifier.

        Arguments:
            connection: SQLAlchemy connection
            definition: definition text
            entry_id: related entry identifier
            source_id: related source identifier
        Returns:
            definition identifier
        """
        result = connection.execute(
            sqlite_insert(DictionarySqliteStore._definitions)
            .values(
                definition=definition.text,
                label=definition.label,
                fk_entry_id=entry_id,
                fk_source_id=source_id,
            )
            .on_conflict_do_nothing()
        )
        if result.rowcount == 1:
            inserted_primary_key = result.inserted_primary_key
            if not inserted_primary_key:
                raise RuntimeError("Failed to insert definition")
            return int(inserted_primary_key[0])

        row = connection.execute(
            select(DictionarySqliteStore._definitions.c.definition_id).where(
                (DictionarySqliteStore._definitions.c.definition == definition.text)
                & (DictionarySqliteStore._definitions.c.label == definition.label)
                & (DictionarySqliteStore._definitions.c.fk_entry_id == entry_id)
                & (DictionarySqliteStore._definitions.c.fk_source_id == source_id)
            )
        ).first()
        if row is None:
            raise RuntimeError("Failed to insert or load existing definition")
        return int(row[0])

    @staticmethod
    def _insert_entry(connection: Connection, entry: DictionaryEntry) -> int:
        """Insert a dictionary entry and return its identifier.

        Arguments:
            connection: SQLAlchemy connection
            entry: dictionary entry
        Returns:
            entry identifier
        """
        result = connection.execute(
            sqlite_insert(DictionarySqliteStore._entries)
            .values(
                traditional=entry.traditional,
                simplified=entry.simplified,
                pinyin=entry.pinyin,
                jyutping=entry.jyutping,
                frequency=entry.frequency,
            )
            .on_conflict_do_nothing()
        )
        if result.rowcount == 1:
            inserted_primary_key = result.inserted_primary_key
            if not inserted_primary_key:
                raise RuntimeError("Failed to insert entry")
            return int(inserted_primary_key[0])

        row = connection.execute(
            select(DictionarySqliteStore._entries.c.entry_id).where(
                (DictionarySqliteStore._entries.c.traditional == entry.traditional)
                & (DictionarySqliteStore._entries.c.simplified == entry.simplified)
                & (DictionarySqliteStore._entries.c.pinyin == entry.pinyin)
                & (DictionarySqliteStore._entries.c.jyutping == entry.jyutping)
            )
        ).first()
        if row is None:
            raise RuntimeError("Failed to insert or load existing entry")
        return int(row[0])

    @staticmethod
    def _insert_source(connection: Connection, source: DictionarySource) -> int:
        """Insert a source and return its identifier.

        Arguments:
            connection: SQLAlchemy connection
            source: source metadata
        Returns:
            source identifier
        """
        result = connection.execute(
            DictionarySqliteStore._sources.insert().values(
                sourcename=source.name,
                sourceshortname=source.shortname,
                version=source.version,
                description=source.description,
                legal=source.legal,
                link=source.link,
                update_url=source.update_url,
                other=source.other,
            ),
        )
        inserted_primary_key = result.inserted_primary_key
        if not inserted_primary_key:
            raise RuntimeError("Failed to insert source")
        return int(inserted_primary_key[0])

    @staticmethod
    def _is_missing_fts5(exc: OperationalError) -> bool:
        """Check whether an operational error indicates unavailable FTS5 support.

        Arguments:
            exc: SQLAlchemy operational error
        Returns:
            whether error indicates missing FTS5 support
        """
        message = str(exc).lower()
        if "fts5" in message or "no such module" in message:
            return True
        return "no such table" in message and "_fts" in message

    def _select_entry_ids(self, statement: Select[tuple[int]]) -> list[int]:
        """Run entry selection query.

        Arguments:
            statement: SQLAlchemy query that returns entry identifiers
        Returns:
            ordered entry identifiers
        """
        with self.engine.connect() as connection:
            rows = connection.execute(statement).scalars().all()
        return [int(row) for row in rows]

    def _write_database_version(self, connection: Connection):
        """Write schema version.

        Arguments:
            connection: SQLAlchemy connection
        """
        connection.execute(text(f"PRAGMA user_version={self.schema_version}"))
