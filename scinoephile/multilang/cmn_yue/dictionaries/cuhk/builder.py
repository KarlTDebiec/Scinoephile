#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary scraping, parsing, and storage orchestration."""

from __future__ import annotations

from os.path import expandvars
from pathlib import Path

import opencc
import requests

from scinoephile.core.paths import get_runtime_cache_dir_path

from .builder_links import CuhkDictionaryBuilderLinksMixin
from .builder_parser import CuhkDictionaryBuilderParserMixin
from .builder_writer import CuhkDictionaryBuilderWriterMixin

__all__ = [
    "CuhkDictionaryBuilder",
]


class CuhkDictionaryBuilder(
    CuhkDictionaryBuilderLinksMixin,
    CuhkDictionaryBuilderParserMixin,
    CuhkDictionaryBuilderWriterMixin,
):
    """Builder for CUHK dictionary cache and SQLite data."""

    def __init__(
        self,
        cache_dir_path: Path | None = None,
        *,
        min_delay_seconds: float = 5.0,
        max_delay_seconds: float = 10.0,
        request_timeout_seconds: float = 30.0,
        max_retries: int = 5,
        session: requests.Session | None = None,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: cache directory path for CUHK artifacts
            min_delay_seconds: minimum delay between HTTP requests
            max_delay_seconds: maximum delay between HTTP requests
            request_timeout_seconds: per-request timeout
            max_retries: max attempts for failed requests
            session: requests session for dependency injection
        """
        if cache_dir_path is None:
            cache_dir_path = get_runtime_cache_dir_path("dictionaries", "cuhk")

        self.cache_dir_path = (
            Path(expandvars(str(cache_dir_path))).expanduser().resolve()
        )
        self.scraped_dir_path = self.cache_dir_path / "scraped"
        self.word_links_path = self.cache_dir_path / "word_links.tsv"
        self.database_path = self.cache_dir_path / "cuhk.db"

        if max_delay_seconds < min_delay_seconds:
            raise ValueError("max_delay_seconds must be >= min_delay_seconds")

        self.min_delay_seconds = min_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.request_timeout_seconds = request_timeout_seconds
        self.max_retries = max_retries

        self.session = session or requests.Session()
        self.opencc_converter = opencc.OpenCC("hk2s")

    def build(self, force_rebuild: bool = False) -> Path:
        """Build the local CUHK SQLite dictionary.

        Arguments:
            force_rebuild: whether to ignore existing artifacts and rebuild
        Returns:
            path to built SQLite database
        """
        if self.database_path.exists() and not force_rebuild:
            return self.database_path

        self._ensure_cache_directories()
        if force_rebuild:
            self._clear_scraped_pages()

        word_links = self.load_word_links(force_refresh=force_rebuild)
        self.scrape_word_pages(word_links, skip_existing=not force_rebuild)
        entries = self.parse_scraped_pages()
        self.write_database(entries)
        return self.database_path

    def _ensure_cache_directories(self):
        """Ensure cache directories exist for scraping/build operations."""
        self.cache_dir_path.mkdir(parents=True, exist_ok=True)
        self.scraped_dir_path.mkdir(parents=True, exist_ok=True)

    def _clear_scraped_pages(self):
        """Delete cached scraped HTML pages."""
        if not self.scraped_dir_path.exists():
            return
        for scraped_path in self.scraped_dir_path.glob("*.html"):
            scraped_path.unlink()
