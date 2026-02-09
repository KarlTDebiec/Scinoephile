#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary lookup service."""

from __future__ import annotations

import sqlite3
from enum import StrEnum
from pathlib import Path

from .builder import CuhkDictionaryBuilder
from .models import DictionaryDefinition, DictionaryEntry

__all__ = [
    "CuhkDictionaryService",
    "LookupDirection",
]


class LookupDirection(StrEnum):
    """Lookup direction for CUHK dictionary queries."""

    MANDARIN_TO_CANTONESE = "mandarin_to_cantonese"
    CANTONESE_TO_MANDARIN = "cantonese_to_mandarin"


class CuhkDictionaryService:
    """Runtime service for querying locally cached CUHK dictionary data."""

    def __init__(
        self,
        cache_dir_path: Path | None = None,
        *,
        auto_build_missing: bool = False,
        min_delay_seconds: float = 5.0,
        max_delay_seconds: float = 10.0,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: cache directory path for CUHK artifacts
            auto_build_missing: build CUHK data automatically if missing
            min_delay_seconds: minimum delay used if build is triggered
            max_delay_seconds: maximum delay used if build is triggered
        """
        self.auto_build_missing = auto_build_missing
        self.builder = CuhkDictionaryBuilder(
            cache_dir_path=cache_dir_path,
            min_delay_seconds=min_delay_seconds,
            max_delay_seconds=max_delay_seconds,
        )

    @property
    def database_path(self) -> Path:
        """Path to local SQLite database."""
        return self.builder.database_path

    def build(self, force_rebuild: bool = False) -> Path:
        """Build CUHK data cache.

        Arguments:
            force_rebuild: whether to force rebuild from source
        Returns:
            path to built SQLite database
        """
        return self.builder.build(force_rebuild=force_rebuild)

    def lookup(
        self,
        query: str,
        direction: LookupDirection = LookupDirection.MANDARIN_TO_CANTONESE,
        limit: int = 10,
    ) -> list[DictionaryEntry]:
        """Query local CUHK dictionary data.

        Arguments:
            query: input text to search
            direction: lookup direction
            limit: max results to return
        Returns:
            dictionary entries
        """
        normalized_query = query.strip()
        if not normalized_query:
            return []

        database_path = self._ensure_database_path()
        if direction == LookupDirection.MANDARIN_TO_CANTONESE:
            return self._lookup_mandarin_to_cantonese(
                database_path,
                normalized_query,
                limit,
            )
        return self._lookup_cantonese_to_mandarin(
            database_path,
            normalized_query,
            limit,
        )

    def _ensure_database_path(self) -> Path:
        """Ensure local database exists.

        Returns:
            database path
        Raises:
            FileNotFoundError: if database is missing and auto-build is disabled
        """
        if self.database_path.exists():
            return self.database_path

        if not self.auto_build_missing:
            raise FileNotFoundError(
                "CUHK dictionary database not found. "
                "Set auto_build_missing=True to build automatically, "
                "or build explicitly with CuhkDictionaryService.build()."
            )

        return self.build(force_rebuild=False)

    def _lookup_mandarin_to_cantonese(
        self,
        database_path: Path,
        query: str,
        limit: int,
    ) -> list[DictionaryEntry]:
        """Lookup Mandarin query terms in CUHK data.

        Arguments:
            database_path: sqlite database path
            query: query string
            limit: max results
        Returns:
            dictionary entries
        """
        like_query = f"%{query}%"

        sql = """
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
            WHERE e.simplified = ?
               OR e.traditional = ?
               OR e.pinyin LIKE ?
               OR d.definition LIKE ?
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
        return self._run_lookup_query(database_path, sql, params)

    def _lookup_cantonese_to_mandarin(
        self,
        database_path: Path,
        query: str,
        limit: int,
    ) -> list[DictionaryEntry]:
        """Lookup Cantonese query terms in CUHK data.

        Arguments:
            database_path: sqlite database path
            query: query string
            limit: max results
        Returns:
            dictionary entries
        """
        like_query = f"%{query}%"

        sql = """
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
            WHERE e.jyutping = ?
               OR e.jyutping LIKE ?
               OR e.traditional = ?
               OR e.simplified = ?
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
        return self._run_lookup_query(database_path, sql, params)

    def _run_lookup_query(
        self,
        database_path: Path,
        sql: str,
        params: tuple[str | int, ...],
    ) -> list[DictionaryEntry]:
        """Run lookup query and aggregate definitions by entry.

        Arguments:
            database_path: sqlite database path
            sql: SQL query
            params: SQL parameters
        Returns:
            dictionary entries
        """
        with sqlite3.connect(database_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(sql, params).fetchall()

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
