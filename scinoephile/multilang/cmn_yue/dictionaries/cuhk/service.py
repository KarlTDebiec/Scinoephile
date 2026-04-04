#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary lookup service."""

from __future__ import annotations

from pathlib import Path

from scinoephile.multilang.cmn_yue.dictionaries.dictionary_entry import (
    DictionaryEntry,
)
from scinoephile.multilang.cmn_yue.dictionaries.lookup_direction import (
    LookupDirection,
)

from .builder import CuhkDictionaryBuilder
from .service_lookup import CuhkDictionaryLookupMixin

__all__ = [
    "CuhkDictionaryService",
]

MAX_LOOKUP_LIMIT = 400


class CuhkDictionaryService(CuhkDictionaryLookupMixin):
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
        normalized_limit = min(MAX_LOOKUP_LIMIT, max(1, int(limit)))

        database_path = self._ensure_database_path()
        if direction == LookupDirection.MANDARIN_TO_CANTONESE:
            return self._lookup_mandarin_to_cantonese(
                database_path,
                normalized_query,
                normalized_limit,
            )
        return self._lookup_cantonese_to_mandarin(
            database_path,
            normalized_query,
            normalized_limit,
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
