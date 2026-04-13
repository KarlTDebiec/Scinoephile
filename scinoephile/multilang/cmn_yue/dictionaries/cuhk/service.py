#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary service."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from scinoephile.common.validation import val_int, val_output_path
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.lang.cmn.romanization import get_cmn_pinyin_query_strings
from scinoephile.lang.id import LanguageIDResult
from scinoephile.lang.yue.romanization import get_yue_jyutping_query_strings
from scinoephile.multilang.dictionaries import (
    DictionaryEntry,
    DictionarySqliteStore,
    LookupDirection,
)

from .constants import MAX_LOOKUP_LIMIT
from .scraper import CuhkDictionaryScraper, CuhkDictionaryScraperKwargs

__all__ = [
    "CuhkDictionaryService",
]


class CuhkDictionaryService:
    """Runtime service for querying locally cached CUHK dictionary data."""

    def __init__(
        self,
        database_path: Path | None = None,
        *,
        auto_build_missing: bool = False,
        scraper_kwargs: CuhkDictionaryScraperKwargs | None = None,
    ):
        """Initialize.

        Arguments:
            database_path: SQLite database path
            auto_build_missing: build CUHK data automatically if missing
            scraper_kwargs: keyword arguments forwarded to CuhkDictionaryScraper
        """
        if database_path is None:
            database_path = (
                get_runtime_cache_dir_path("dictionaries", "cuhk") / "cuhk.db"
            )
        self.database_path = val_output_path(database_path, exist_ok=True)
        self.auto_build_missing = auto_build_missing
        if scraper_kwargs is None:
            scraper_kwargs = {}
        self.database = DictionarySqliteStore(database_path=self.database_path)
        self.scraper = CuhkDictionaryScraper(**scraper_kwargs)
        self.cache_dir_path = self.scraper.cache_dir_path

    def build(self, overwrite: bool = False, max_words: int | None = None) -> Path:
        """Build or rebuild the local CUHK SQLite dictionary.

        Arguments:
            overwrite: whether to overwrite an existing SQLite database
            max_words: optional max number of discovered words to scrape
        Returns:
            SQLite database path
        """
        if self.database_path.exists() and not overwrite:
            return self.database_path

        scrape_data = self.scraper.scrape(max_words=max_words)
        return self.database.persist(scrape_data)

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

        self._ensure_database()

        for lookup_query in self._get_lookup_queries(query, direction):
            if entries := self.database.lookup(lookup_query, direction, limit):
                return entries
        return []

    def lookup_inferred(
        self,
        query: str,
        limit: int = 10,
    ) -> list[DictionaryEntry]:
        """Query local CUHK dictionary data using inferred query formats.

        Arguments:
            query: input text to search
            limit: max results to return
        Returns:
            dictionary entries
        """
        query = query.strip()
        if not query:
            return []
        limit = val_int(limit, min_value=1, max_value=MAX_LOOKUP_LIMIT)

        self._ensure_database()

        entries: list[DictionaryEntry] = []
        seen_keys: set[tuple[str, str, str, str]] = set()
        for direction, lookup_query in self._get_inferred_lookup_queries(query):
            for entry in self.database.lookup(lookup_query, direction, limit):
                entry_key = (
                    entry.traditional,
                    entry.simplified,
                    entry.pinyin,
                    entry.jyutping,
                )
                if entry_key in seen_keys:
                    continue
                seen_keys.add(entry_key)
                entries.append(entry)
                if len(entries) >= limit:
                    return entries

        return entries

    @staticmethod
    def _deduplicate_lookup_queries(
        queries: Iterable[tuple[LookupDirection, str]],
    ) -> list[tuple[LookupDirection, str]]:
        """Deduplicate ordered lookup query pairs.

        Arguments:
            queries: ordered direction/query pairs
        Returns:
            deduplicated direction/query pairs
        """
        ordered_queries: list[tuple[LookupDirection, str]] = []
        seen_queries: set[tuple[LookupDirection, str]] = set()
        for direction, query in queries:
            normalized_query = query.strip()
            if not normalized_query:
                continue
            query_key = (direction, normalized_query)
            if query_key not in seen_queries:
                seen_queries.add(query_key)
                ordered_queries.append(query_key)
        return ordered_queries

    def _ensure_database(self):
        """Ensure the SQLite database exists, building it if configured."""
        if self.database_path.exists():
            return
        if not self.auto_build_missing:
            raise FileNotFoundError(
                "CUHK dictionary database not found. "
                "Set auto_build_missing=True to build automatically, "
                "or build explicitly with CuhkDictionaryService.build()."
            )
        self.build(overwrite=False)

    @classmethod
    def _get_inferred_lookup_queries(
        cls, query: str
    ) -> list[tuple[LookupDirection, str]]:
        """Get ordered lookup direction/query pairs inferred from query format.

        Arguments:
            query: raw query text
        Returns:
            ordered lookup direction/query pairs
        """
        query_id = LanguageIDResult(query)
        lookup_queries: list[tuple[LookupDirection, str]] = []

        if query_id.is_numbered_pinyin or query_id.is_accented_pinyin:
            lookup_queries.extend(
                (LookupDirection.CMN_TO_YUE, one_query)
                for one_query in cls._get_lookup_queries(
                    query, LookupDirection.CMN_TO_YUE
                )
            )
        if query_id.is_numbered_jyutping or query_id.is_accented_yale:
            lookup_queries.extend(
                (LookupDirection.YUE_TO_CMN, one_query)
                for one_query in cls._get_lookup_queries(
                    query, LookupDirection.YUE_TO_CMN
                )
            )
        if query_id.is_simplified or query_id.is_traditional:
            lookup_queries.extend(
                [
                    (LookupDirection.YUE_TO_CMN, query),
                    (LookupDirection.CMN_TO_YUE, query),
                ]
            )
        if not lookup_queries:
            lookup_queries.append((LookupDirection.CMN_TO_YUE, query))

        return cls._deduplicate_lookup_queries(lookup_queries)

    @staticmethod
    def _get_lookup_queries(query: str, direction: LookupDirection) -> list[str]:
        """Get ordered query variants for dictionary lookup.

        Arguments:
            query: raw query text
            direction: lookup direction
        Returns:
            ordered query variants
        """
        if direction == LookupDirection.CMN_TO_YUE:
            query_variants = get_cmn_pinyin_query_strings(query)
        else:
            query_variants = get_yue_jyutping_query_strings(query)

        ordered_queries: list[str] = []
        seen_queries: set[str] = set()
        for one_query in [*query_variants, query]:
            if one_query and one_query not in seen_queries:
                seen_queries.add(one_query)
                ordered_queries.append(one_query)
        return ordered_queries
