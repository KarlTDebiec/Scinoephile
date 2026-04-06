#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary lookup service."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from scinoephile.common.validation import val_int
from scinoephile.multilang.cmn_yue.dictionaries.dictionary_definition import (
    DictionaryDefinition,
)
from scinoephile.multilang.cmn_yue.dictionaries.dictionary_entry import (
    DictionaryEntry,
)
from scinoephile.multilang.cmn_yue.dictionaries.lookup_direction import (
    LookupDirection,
)

from .constants import MAX_LOOKUP_LIMIT
from .scraper import CuhkDictionaryScraper

__all__ = [
    "CuhkDictionaryService",
]


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
        self.scraper = CuhkDictionaryScraper(
            cache_dir_path=cache_dir_path,
            min_delay_seconds=min_delay_seconds,
            max_delay_seconds=max_delay_seconds,
        )

    def lookup(
        self,
        query: str,
        direction: LookupDirection = LookupDirection.CMN_TO_YUE,
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
        query = query.strip()
        if not query:
            return []
        limit = val_int(limit, min_value=1, max_value=MAX_LOOKUP_LIMIT)

        database_path = self.scraper.database_path
        if not database_path.exists():
            if not self.auto_build_missing:
                raise FileNotFoundError(
                    "CUHK dictionary database not found. "
                    "Set auto_build_missing=True to build automatically, "
                    "or scrape explicitly with CuhkDictionaryScraper.scrape()."
                )
            database_path = self.scraper.scrape(force=False)

        if direction == LookupDirection.CMN_TO_YUE:
            return self._lookup_cmn_to_yue(database_path, query, limit)
        return self._lookup_yue_to_cmn(database_path, query, limit)

    @staticmethod
    def _aggregate_rows(rows: list[sqlite3.Row]) -> list[DictionaryEntry]:
        """Aggregate joined rows into dictionary entries.

        Arguments:
            rows: joined entry/definition rows
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
    def _build_like_query(query: str) -> str:
        """Build escaped LIKE pattern for literal substring search.

        Arguments:
            query: raw query text
        Returns:
            escaped pattern wrapped for substring search
        """
        escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        return f"%{escaped}%"

    @staticmethod
    def _fetch_entries(
        database_path: Path,
        entry_ids: list[int],
    ) -> list[DictionaryEntry]:
        """Fetch entry rows and definitions for selected entry IDs.

        Arguments:
            database_path: sqlite database path
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
        with sqlite3.connect(database_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(sql, params).fetchall()

        return CuhkDictionaryService._aggregate_rows(rows)

    @staticmethod
    def _lookup_cmn_to_yue(
        database_path: Path, query: str, limit: int
    ) -> list[DictionaryEntry]:
        """Lookup Mandarin query terms in CUHK data.

        Arguments:
            database_path: sqlite database path
            query: query string
            limit: max results
        Returns:
            dictionary entries
        """
        like_query = CuhkDictionaryService._build_like_query(query)

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
        entry_ids = CuhkDictionaryService._select_entry_ids(
            database_path,
            sql,
            params,
        )
        return CuhkDictionaryService._fetch_entries(database_path, entry_ids)

    @staticmethod
    def _lookup_yue_to_cmn(
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
        like_query = CuhkDictionaryService._build_like_query(query)

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
        entry_ids = CuhkDictionaryService._select_entry_ids(
            database_path,
            sql,
            params,
        )
        return CuhkDictionaryService._fetch_entries(database_path, entry_ids)

    @staticmethod
    def _select_entry_ids(
        database_path: Path,
        sql: str,
        params: tuple[str | int, ...],
    ) -> list[int]:
        """Run entry selection query.

        Arguments:
            database_path: sqlite database path
            sql: SQL query that returns entry_id
            params: SQL parameters
        Returns:
            ordered entry identifiers
        """
        with sqlite3.connect(database_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(sql, params).fetchall()
        return [int(row["entry_id"]) for row in rows]
