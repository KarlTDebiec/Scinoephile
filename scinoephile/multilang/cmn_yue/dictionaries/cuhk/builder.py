#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary scraping, parsing, and storage orchestration."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

import opencc
import requests

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.paths import get_runtime_cache_dir_path

from .builder_links import CuhkDictionaryBuilderLinks
from .builder_parser import CuhkDictionaryBuilderParser
from .builder_writer import CuhkDictionaryBuilderWriter
from .constants import DEFAULT_DATABASE_PATH

__all__ = [
    "CuhkDictionaryBuilder",
]

logger = getLogger(__name__)


class CuhkDictionaryBuilder:
    """Builder for CUHK dictionary cache and SQLite data."""

    def __init__(
        self,
        cache_dir_path: Path | None = None,
        database_path: Path | None = None,
        *,
        min_delay_seconds: float = 5.0,
        max_delay_seconds: float = 10.0,
        request_timeout_seconds: float = 30.0,
        max_retries: int = 5,
        session: requests.Session | None = None,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: cache directory path for CUHK scrape artifacts
            database_path: SQLite database path
            min_delay_seconds: minimum delay between HTTP requests
            max_delay_seconds: maximum delay between HTTP requests
            request_timeout_seconds: per-request timeout
            max_retries: max attempts for failed requests
            session: requests session for dependency injection
        """
        configured_cache_dir_path = cache_dir_path
        if configured_cache_dir_path is None:
            configured_cache_dir_path = get_runtime_cache_dir_path(
                "dictionaries", "cuhk"
            )

        self.cache_dir_path = val_output_dir_path(configured_cache_dir_path)
        self.scraped_dir_path = self.cache_dir_path / "scraped"
        self.word_links_path = self.cache_dir_path / "word_links.tsv"
        if database_path is None:
            if cache_dir_path is None:
                database_path = DEFAULT_DATABASE_PATH
            else:
                database_path = self.cache_dir_path / "cuhk.db"
        self.database_path = database_path.expanduser().resolve()

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

    def build(
        self,
        force_rebuild: bool = False,
        max_words: int | None = None,
    ) -> Path:
        """Build the local CUHK SQLite dictionary.

        Arguments:
            force_rebuild: whether to ignore existing artifacts and rebuild
            max_words: optional max number of discovered words to build
        Returns:
            path to built SQLite database
        """
        if self.database_path.exists() and not force_rebuild and max_words is None:
            return self.database_path

        # Ensure cache directories exist before downloading or parsing artifacts.
        self.cache_dir_path.mkdir(parents=True, exist_ok=True)
        self.scraped_dir_path.mkdir(parents=True, exist_ok=True)

        # When rebuilding or limiting the build scope, remove stale scraped pages first.
        if force_rebuild or max_words is not None:
            for scraped_path in self.scraped_dir_path.glob("*.html"):
                logger.info(f"Deleting stale scraped CUHK page: {scraped_path}")
                scraped_path.unlink()

        logger.info("Discovering CUHK word links")
        word_links = self.links.load_word_links(force_refresh=force_rebuild)
        logger.info(f"Discovered {len(word_links)} CUHK word link(s)")
        if max_words is not None:
            word_links = word_links[:max_words]
            logger.info(f"Limiting CUHK build to {len(word_links)} word(s)")

        logger.info("Scraping CUHK word pages")
        self.links.scrape_word_pages(
            word_links,
            skip_existing=not force_rebuild and max_words is None,
        )
        logger.info("Parsing scraped CUHK word pages")
        entries = self.parser.parse_scraped_pages()
        logger.info(f"Parsed {len(entries)} CUHK entry(ies)")
        logger.info("Writing CUHK SQLite database")
        self.writer.write_database(entries)
        return self.database_path
