#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary service."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.validation import val_int, val_output_path
from scinoephile.core.dictionaries import DictionaryEntry, LookupDirection
from scinoephile.lang.cmn.romanization import get_cmn_pinyin_query_strings
from scinoephile.lang.yue.romanization import get_yue_jyutping_variants

from .constants import DEFAULT_DATABASE_PATH, MAX_LOOKUP_LIMIT
from .database import CuhkDictionaryDatabase
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
            database_path = DEFAULT_DATABASE_PATH
        self.database_path = val_output_path(database_path, exist_ok=True)
        self.auto_build_missing = auto_build_missing
        if scraper_kwargs is None:
            scraper_kwargs = {}
        self.database = CuhkDictionaryDatabase(database_path=self.database_path)
        self.scraper = CuhkDictionaryScraper(**scraper_kwargs)
        self.cache_dir_path = self.scraper.cache_dir_path

    def build(self, force: bool = False, max_words: int | None = None) -> Path:
        """Build or rebuild the local CUHK SQLite dictionary.

        Arguments:
            force: whether to ignore existing artifacts and rebuild
            max_words: optional max number of discovered words to scrape
        Returns:
            SQLite database path
        """
        if self.database_path.exists() and not force and max_words is None:
            return self.database_path

        scrape_data = self.scraper.scrape(force=force, max_words=max_words)
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

        if not self.database_path.exists():
            if not self.auto_build_missing:
                raise FileNotFoundError(
                    "CUHK dictionary database not found. "
                    "Set auto_build_missing=True to build automatically, "
                    "or build explicitly with CuhkDictionaryService.build()."
                )
            self.build(force=False)

        for lookup_query in self._get_lookup_queries(query, direction):
            if entries := self.database.lookup(lookup_query, direction, limit):
                return entries
        return []

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
            query_variants = get_yue_jyutping_variants(query)

        ordered_queries: list[str] = []
        seen_queries: set[str] = set()
        for one_query in [*query_variants, query]:
            if one_query and one_query not in seen_queries:
                seen_queries.add(one_query)
                ordered_queries.append(one_query)
        return ordered_queries
