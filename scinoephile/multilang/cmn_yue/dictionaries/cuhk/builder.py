#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary scraping, parsing, and storage orchestration."""

from __future__ import annotations

from os.path import expandvars
from pathlib import Path

import opencc
import requests

from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.multilang.cmn_yue.dictionaries.dictionary_entry import (
    DictionaryEntry,
)

from .builder_links import CuhkDictionaryBuilderLinks
from .builder_parser import CuhkDictionaryBuilderParser
from .builder_writer import CuhkDictionaryBuilderWriter

__all__ = [
    "CuhkDictionaryBuilder",
]


class CuhkDictionaryBuilder:
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
        self.links = CuhkDictionaryBuilderLinks(
            cache_dir_path=self.cache_dir_path,
            scraped_dir_path=self.scraped_dir_path,
            word_links_path=self.word_links_path,
            min_delay_seconds=self.min_delay_seconds,
            max_delay_seconds=self.max_delay_seconds,
            max_retries=self.max_retries,
            request_timeout_seconds=self.request_timeout_seconds,
            session=self.session,
        )
        self.parser = CuhkDictionaryBuilderParser(
            scraped_dir_path=self.scraped_dir_path,
            opencc_converter=self.opencc_converter,
        )
        self.writer = CuhkDictionaryBuilderWriter(
            cache_dir_path=self.cache_dir_path,
            database_path=self.database_path,
        )

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

    def load_word_links(self, force_refresh: bool = False) -> list[tuple[str, str]]:
        """Load or fetch CUHK word links.

        Arguments:
            force_refresh: whether to ignore cached link file
        Returns:
            list of (word, url)
        """
        return self.links.load_word_links(force_refresh=force_refresh)

    def discover_word_links(self) -> list[tuple[str, str]]:
        """Discover all CUHK word pages.

        Returns:
            list of (word, url)
        """
        return self.links.discover_word_links()

    def scrape_word_pages(
        self,
        word_links: list[tuple[str, str]],
        *,
        skip_existing: bool = True,
    ):
        """Scrape CUHK word pages into cached HTML files.

        Arguments:
            word_links: list of (word, url)
            skip_existing: whether to skip files already present
        """
        self.links.scrape_word_pages(word_links, skip_existing=skip_existing)

    def parse_scraped_pages(self) -> list[DictionaryEntry]:
        """Parse scraped CUHK pages into normalized entries.

        Returns:
            parsed dictionary entries
        """
        return self.parser.parse_scraped_pages()

    def parse_word_file(self, html_path: Path):
        """Parse one scraped CUHK word page.

        Arguments:
            html_path: path to scraped HTML page
        Returns:
            parsed entry, if valid
        """
        return self.parser.parse_word_file(html_path)

    def write_database(self, entries: list[DictionaryEntry]) -> None:
        """Write parsed entries to the SQLite cache.

        Arguments:
            entries: normalized dictionary entries
        """
        self.writer.write_database(entries)
