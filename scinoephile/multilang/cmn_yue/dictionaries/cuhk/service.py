#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary service."""

from __future__ import annotations

from pathlib import Path

import requests

from scinoephile.common.validation import val_int, val_output_path
from scinoephile.core.dictionaries import DictionaryEntry, LookupDirection

from .constants import DEFAULT_DATABASE_PATH, MAX_LOOKUP_LIMIT
from .database import CuhkDictionaryDatabase
from .scraper import CuhkDictionaryScraper

__all__ = [
    "CuhkDictionaryService",
]


class CuhkDictionaryService:
    """Runtime service for querying locally cached CUHK dictionary data."""

    def __init__(
        self,
        cache_dir_path: Path | None = None,
        database_path: Path | None = None,
        *,
        auto_build_missing: bool = False,
        min_delay_seconds: float = 5.0,
        max_delay_seconds: float = 10.0,
        request_timeout_seconds: float = 30.0,
        max_retries: int = 5,
        session: requests.Session | None = None,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: cache directory path for CUHK artifacts
            database_path: SQLite database path
            auto_build_missing: build CUHK data automatically if missing
            min_delay_seconds: minimum delay used if build is triggered
            max_delay_seconds: maximum delay used if build is triggered
            request_timeout_seconds: per-request timeout
            max_retries: max attempts for failed requests
            session: requests session for dependency injection
        """
        if database_path is None:
            database_path = DEFAULT_DATABASE_PATH
        self.database_path = val_output_path(database_path, exist_ok=True)
        self.auto_build_missing = auto_build_missing
        self.database = CuhkDictionaryDatabase(database_path=self.database_path)
        self.scraper = CuhkDictionaryScraper(
            cache_dir_path=cache_dir_path,
            min_delay_seconds=min_delay_seconds,
            max_delay_seconds=max_delay_seconds,
            request_timeout_seconds=request_timeout_seconds,
            max_retries=max_retries,
            session=session,
        )
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

        return self.database.lookup(query, direction, limit)
