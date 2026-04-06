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

from .constants import DEFAULT_DATABASE_PATH
from .scraper_links import CuhkDictionaryScraperLinks
from .scraper_parser import CuhkDictionaryScraperParser
from .scraper_writer import CuhkDictionaryScraperWriter

__all__ = [
    "CuhkDictionaryScraper",
]

logger = getLogger(__name__)


class CuhkDictionaryScraper:
    """Scraper for CUHK dictionary cache and SQLite data."""

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

        # Configure requests
        if max_delay_seconds < min_delay_seconds:
            raise ValueError("max_delay_seconds must be >= min_delay_seconds")
        self.min_delay_seconds = min_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.request_timeout_seconds = request_timeout_seconds
        self.max_retries = max_retries

        # Initialize tools
        self.session = session or requests.Session()
        self.opencc_converter = opencc.OpenCC("hk2s")
        self.links = CuhkDictionaryScraperLinks(
            cache_dir_path=self.cache_dir_path,
            scraped_dir_path=self.scraped_dir_path,
            word_links_path=self.word_links_path,
            min_delay_seconds=self.min_delay_seconds,
            max_delay_seconds=self.max_delay_seconds,
            max_retries=self.max_retries,
            request_timeout_seconds=self.request_timeout_seconds,
            session=self.session,
        )
        self.parser = CuhkDictionaryScraperParser(
            scraped_dir_path=self.scraped_dir_path,
            opencc_converter=self.opencc_converter,
        )
        self.writer = CuhkDictionaryScraperWriter(
            cache_dir_path=self.cache_dir_path,
            database_path=self.database_path,
        )

    def scrape(
        self,
        force: bool = False,
        max_words: int | None = None,
    ) -> Path:
        """Scrape CUHK data into a local SQLite dictionary.

        Arguments:
            force: whether to ignore existing artifacts and rebuild
            max_words: optional max number of discovered words to scrape
        Returns:
            path to scraped SQLite database
        """
        if self.database_path.exists() and not force and max_words is None:
            return self.database_path

        # Clear cache if applicable
        if force or max_words is not None:
            for scraped_path in self.scraped_dir_path.glob("*.html"):
                scraped_path.unlink()
                logger.info(f"Removed stale scraped page: {scraped_path}")

        # Scrape word links
        logger.info("Discovering CUHK word links")
        word_links = self.links.load_word_links(force=force)
        logger.info(f"Discovered {len(word_links)} CUHK word link(s)")
        if max_words is not None:
            word_links = word_links[:max_words]
            logger.info(f"Limiting CUHK scrape to {len(word_links)} word(s)")

        # Scrape words
        logger.info("Scraping CUHK word pages")
        self.links.scrape_word_pages(
            word_links, skip_existing=not force and max_words is None
        )
        logger.info("Parsing scraped CUHK word pages")
        entries = self.parser.parse_scraped_pages()
        logger.info(f"Parsed {len(entries)} CUHK entry(ies)")
        logger.info("Writing CUHK SQLite database")

        # Write database
        self.writer.write_database(entries)
        return self.database_path
