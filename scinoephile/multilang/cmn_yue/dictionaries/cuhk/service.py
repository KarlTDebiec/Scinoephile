#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary lookup service."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.validation import val_int
from scinoephile.multilang.cmn_yue.dictionaries.dictionary_entry import (
    DictionaryEntry,
)
from scinoephile.multilang.cmn_yue.dictionaries.lookup_direction import (
    LookupDirection,
)

from .constants import MAX_LOOKUP_LIMIT
from .scraper import CuhkDictionaryScraper
from .service_lookup import CuhkDictionaryLookupStore

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
        self.lookup_store = CuhkDictionaryLookupStore()

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
            return self.lookup_store.lookup_cmn_to_yue(database_path, query, limit)
        return self.lookup_store.lookup_yue_to_cmn(database_path, query, limit)
