#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Link-discovery and scraping helpers for the CUHK dictionary scraper."""

from __future__ import annotations

import csv
import random
from logging import getLogger
from pathlib import Path
from time import sleep
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag

from .constants import (
    BASE_URL,
    CUHK_HOSTNAME,
    CUHK_TERMS_PATH,
    CUHK_WORD_RESULT_PATHS,
    INVALID_FILENAME_CHARS_REGEX,
    TERMS_URL,
)

logger = getLogger(__name__)

__all__ = [
    "CuhkDictionaryScraperLinks",
]


class CuhkDictionaryScraperLinks:
    """Helper object for link caching, discovery, and scraping behavior."""

    def __init__(
        self,
        cache_dir_path: Path,
        scraped_dir_path: Path,
        word_links_path: Path,
        *,
        min_delay_seconds: float,
        max_delay_seconds: float,
        max_retries: int,
        request_timeout_seconds: float,
        session: requests.Session,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: cache directory path
            scraped_dir_path: directory path for scraped HTML pages
            word_links_path: TSV cache path for discovered word links
            min_delay_seconds: minimum delay between HTTP requests
            max_delay_seconds: maximum delay between HTTP requests
            max_retries: max attempts for failed requests
            request_timeout_seconds: per-request timeout
            session: requests session used for HTTP requests
        """
        self.cache_dir_path = cache_dir_path
        self.scraped_dir_path = scraped_dir_path
        self.word_links_path = word_links_path
        self.min_delay_seconds = min_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.max_retries = max_retries
        self.request_timeout_seconds = request_timeout_seconds
        self.session = session

    def load_word_links(self, force: bool = False) -> list[tuple[str, str]]:
        """Load or fetch CUHK word links.

        Arguments:
            force: whether to ignore cached link file
        Returns:
            list of (word, url)
        """
        if self.word_links_path.exists() and not force:
            return self._read_word_links(self.word_links_path)

        self.cache_dir_path.mkdir(parents=True, exist_ok=True)
        word_links = self.discover_word_links()
        self._write_word_links(self.word_links_path, word_links)
        return word_links

    def discover_word_links(self) -> list[tuple[str, str]]:
        """Discover all CUHK word pages.

        Returns:
            list of (word, url)
        """
        html = self._fetch_text(TERMS_URL)
        soup = BeautifulSoup(html, "html.parser")

        main_panel = soup.find("div", id="MainContent_panelTermsIndex")
        if not isinstance(main_panel, Tag):
            raise RuntimeError("Unable to find CUHK terms index panel")

        category_links: list[str] = []
        for anchor in main_panel.find_all("a", href=True):
            category_url = urljoin(BASE_URL, str(anchor["href"]).strip())
            parsed_url = urlparse(category_url)
            query_params = parse_qs(parsed_url.query)

            # Keep only actual CUHK category links (Terms.aspx?target=...).
            if parsed_url.netloc != CUHK_HOSTNAME:
                continue
            if parsed_url.path != CUHK_TERMS_PATH:
                continue
            if "target" not in query_params:
                continue

            category_links.append(category_url)

        seen_word_links: set[tuple[str, str]] = set()
        word_links: list[tuple[str, str]] = []
        for category_link in category_links:
            logger.info("Discovering words from category: %s", category_link)
            category_html = self._fetch_text(category_link)
            category_soup = BeautifulSoup(category_html, "html.parser")
            query_panel = category_soup.find("div", id="MainContent_panelTermsQuery")
            if not isinstance(query_panel, Tag):
                logger.warning(
                    "Skipping category with missing query panel: %s", category_link
                )
                continue

            for anchor in query_panel.find_all("a", href=True):
                item = anchor.get_text(strip=True)
                if not item:
                    continue
                url = urljoin(BASE_URL, str(anchor["href"]))
                parsed_word_url = urlparse(url)
                if parsed_word_url.netloc != CUHK_HOSTNAME:
                    logger.warning("Skipping non-CUHK word URL: %s", url)
                    continue
                if parsed_word_url.path not in CUHK_WORD_RESULT_PATHS:
                    logger.warning("Skipping unexpected CUHK word URL path: %s", url)
                    continue
                pair = (item, url)
                if pair in seen_word_links:
                    continue
                seen_word_links.add(pair)
                word_links.append(pair)

        return word_links

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
        self.scraped_dir_path.mkdir(parents=True, exist_ok=True)
        for index, (item, url) in enumerate(word_links, start=1):
            if url == "?":
                logger.info("Skipping item %s (%s): invalid URL", index, item)
                continue

            variant_file_paths = self._get_variant_file_paths(item)
            if skip_existing and all(path.exists() for path in variant_file_paths):
                continue

            html = self._fetch_text(url)
            for variant_file_path in variant_file_paths:
                variant_file_path.write_text(html, encoding="utf-8")
            logger.info("Scraped #%s: %s", index, item)

            if self.max_delay_seconds > 0:
                sleep(random.uniform(self.min_delay_seconds, self.max_delay_seconds))

    def _read_word_links(self, word_links_path: Path) -> list[tuple[str, str]]:
        """Read links from TSV.

        Arguments:
            word_links_path: TSV path
        Returns:
            list of (word, url)
        """
        pairs: list[tuple[str, str]] = []
        with open(word_links_path, encoding="utf-8") as infile:
            reader = csv.reader(infile, delimiter="\t")
            for row in reader:
                if len(row) != 2:
                    continue
                pairs.append((row[0], row[1]))
        return pairs

    def _write_word_links(
        self,
        word_links_path: Path,
        word_links: list[tuple[str, str]],
    ):
        """Write links to TSV.

        Arguments:
            word_links_path: TSV path
            word_links: links to write
        """
        with open(word_links_path, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.writer(outfile, delimiter="\t")
            for item, url in word_links:
                writer.writerow((item, url))

    def _get_variant_file_paths(self, item: str) -> list[Path]:
        """Get output file paths for one CUHK word item.

        Arguments:
            item: item string, potentially with slash-separated variants
        Returns:
            variant file paths
        """
        stems: set[str] = set()
        for variant in item.split("/"):
            stem = self._get_safe_filename_stem(variant.strip())
            if stem:
                stems.add(stem)

        return [self.scraped_dir_path / f"{stem}.html" for stem in sorted(stems)]

    def _get_safe_filename_stem(self, value: str) -> str:
        """Get a safe filename stem for a dictionary key.

        Arguments:
            value: raw value to encode in path
        Returns:
            safe filename stem
        """
        cleaned = value.strip().replace(" ", "_")
        cleaned = INVALID_FILENAME_CHARS_REGEX.sub("_", cleaned)
        return cleaned

    def _fetch_text(self, url: str) -> str:
        """Fetch text with retry and timeout.

        Arguments:
            url: URL to fetch
        Returns:
            fetched text content
        Raises:
            requests.RequestException: if all retry attempts fail
        """
        last_exception: requests.RequestException | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(url, timeout=self.request_timeout_seconds)
                response.raise_for_status()
                response.encoding = "utf-8"
                return response.text
            except requests.RequestException as exc:
                last_exception = exc
                logger.warning(
                    "CUHK request failed (attempt %s/%s): %s",
                    attempt,
                    self.max_retries,
                    exc,
                )
                if attempt < self.max_retries:
                    sleep(1.5)

        if last_exception is None:
            raise RuntimeError("Request failed without an exception")
        raise last_exception
