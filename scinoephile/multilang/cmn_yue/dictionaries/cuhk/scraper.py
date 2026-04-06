#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary scraping and parsing."""

from __future__ import annotations

import csv
import random
from logging import getLogger
from pathlib import Path
from time import sleep
from urllib.parse import parse_qs, urljoin, urlparse

import opencc
import requests
from bs4 import BeautifulSoup, Tag
from hkscs_unicode_converter import converter as hkscs_converter
from pypinyin import Style, lazy_pinyin

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
)
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.text import RE_PRIVATE_USE_AREA_BMP

from .constants import (
    BASE_URL,
    CUHK_HOSTNAME,
    CUHK_SOURCE,
    CUHK_TERMS_PATH,
    CUHK_WORD_RESULT_PATHS,
    INVALID_FILENAME_CHARS_REGEX,
    JYUTPING_LETTERS_ID_REGEX,
    JYUTPING_NUMBERS_ID_REGEX,
    JYUTPING_NUMBERS_REGEX,
    JYUTPING_TONE_MAP,
    LABEL_ID_REGEX,
    MEANING_ID_REGEX,
    PRIVATE_USE_AREA_REPLACEMENT_STRING,
    REMARK_ID_REGEX,
    TERMS_URL,
)

__all__ = [
    "CuhkDictionaryScraper",
]

logger = getLogger(__name__)


class CuhkDictionaryScraper:
    """Scraper for CUHK dictionary cache and parsed entry data."""

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
            cache_dir_path: cache directory path for CUHK scrape artifacts
            min_delay_seconds: minimum delay between HTTP requests
            max_delay_seconds: maximum delay between HTTP requests
            request_timeout_seconds: per-request timeout
            max_retries: max attempts for failed requests
            session: requests session for dependency injection
        """
        if cache_dir_path is None:
            cache_dir_path = get_runtime_cache_dir_path("dictionaries", "cuhk")
        self.cache_dir_path = val_output_dir_path(cache_dir_path)
        self.scraped_dir_path = self.cache_dir_path / "scraped"
        self.word_links_path = self.cache_dir_path / "word_links.tsv"

        if max_delay_seconds < min_delay_seconds:
            raise ValueError("max_delay_seconds must be >= min_delay_seconds")
        self.min_delay_seconds = min_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.request_timeout_seconds = request_timeout_seconds
        self.max_retries = max_retries

        self.session = session or requests.Session()
        self.opencc_converter = opencc.OpenCC("hk2s")

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
            logger.info(f"Discovering words from category: {category_link}")
            category_html = self._fetch_text(category_link)
            category_soup = BeautifulSoup(category_html, "html.parser")
            query_panel = category_soup.find("div", id="MainContent_panelTermsQuery")
            if not isinstance(query_panel, Tag):
                logger.warning(
                    f"Skipping category with missing query panel: {category_link}"
                )
                continue

            for anchor in query_panel.find_all("a", href=True):
                item = anchor.get_text(strip=True)
                if not item:
                    continue
                url = urljoin(BASE_URL, str(anchor["href"]))
                parsed_word_url = urlparse(url)
                if parsed_word_url.netloc != CUHK_HOSTNAME:
                    logger.warning(f"Skipping non-CUHK word URL: {url}")
                    continue
                if parsed_word_url.path not in CUHK_WORD_RESULT_PATHS:
                    logger.warning(f"Skipping unexpected CUHK word URL path: {url}")
                    continue
                pair = (item, url)
                if pair in seen_word_links:
                    continue
                seen_word_links.add(pair)
                word_links.append(pair)

        return word_links

    def load_word_links(self, force: bool = False) -> list[tuple[str, str]]:
        """Load or fetch CUHK word links.

        Arguments:
            force: whether to ignore cached link file
        Returns:
            list of (word, url)
        """
        if self.word_links_path.exists() and not force:
            return self._read_word_links(self.word_links_path)

        word_links = self.discover_word_links()
        self._write_word_links(self.word_links_path, word_links)
        return word_links

    def parse_scraped_pages(self) -> list[DictionaryEntry]:
        """Parse scraped CUHK pages into normalized entries.

        Returns:
            parsed dictionary entries
        """
        entries: list[DictionaryEntry] = []
        for index, html_path in enumerate(sorted(self.scraped_dir_path.glob("*.html"))):
            if index and index % 100 == 0:
                logger.info(f"Parsed {index} CUHK entries")

            entry = self.parse_word_file(html_path)
            if entry is not None:
                entries.append(entry)

        return entries

    def parse_word_file(self, html_path: Path) -> DictionaryEntry | None:
        """Parse one scraped CUHK word page.

        Arguments:
            html_path: path to scraped HTML page
        Returns:
            parsed entry, if valid
        """
        soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")

        text_span = soup.find("span", class_="ChiCharFix")
        if not isinstance(text_span, Tag):
            logger.warning(
                f"Skipping malformed CUHK page without ChiCharFix: {html_path}"
            )
            return None

        traditional = self._normalize_hanzi(text_span.get_text(strip=True))
        simplified = self.opencc_converter.convert(traditional)

        file_word = self._normalize_hanzi(html_path.stem)
        if file_word != traditional:
            logger.warning(
                f"Parsed word '{traditional}' does not match filename "
                f"'{file_word}' ({html_path})"
            )

        label_span = soup.find("span", id=LABEL_ID_REGEX)
        label = label_span.get_text(strip=True) if isinstance(label_span, Tag) else ""

        jyutping_letters_span = soup.find("span", id=JYUTPING_LETTERS_ID_REGEX)
        jyutping_letters = (
            jyutping_letters_span.get_text(strip=True).split()
            if isinstance(jyutping_letters_span, Tag)
            else []
        )
        jyutping_numbers_span = soup.find("span", id=JYUTPING_NUMBERS_ID_REGEX)
        raw_numbers = (
            jyutping_numbers_span.get_text(" ", strip=True)
            if isinstance(jyutping_numbers_span, Tag)
            else ""
        )
        jyutping_numbers = [
            JYUTPING_TONE_MAP.get(number, number)
            for number in JYUTPING_NUMBERS_REGEX.findall(raw_numbers)
        ]
        if len(jyutping_letters) != len(jyutping_numbers):
            logger.warning(
                "Skipping CUHK page with mismatched jyutping letters "
                f"({len(jyutping_letters)}) and tones "
                f"({len(jyutping_numbers)}): {html_path}"
            )
            return None
        jyutping = " ".join(
            f"{letter}{number}"
            for letter, number in zip(jyutping_letters, jyutping_numbers, strict=False)
        )

        pinyin = (
            " ".join(
                lazy_pinyin(
                    simplified,
                    style=Style.TONE3,
                    neutral_tone_with_five=True,
                    v_to_u=True,
                )
            )
            .lower()
            .replace("ü", "u:")
        )

        definitions: list[DictionaryDefinition] = []
        for meaning_span in soup.find_all("span", id=MEANING_ID_REGEX):
            if not isinstance(meaning_span, Tag):
                continue
            meaning = meaning_span.get_text(strip=True)
            if meaning:
                definitions.append(DictionaryDefinition(text=meaning, label=label))

        remark_span = soup.find("span", id=REMARK_ID_REGEX)
        if isinstance(remark_span, Tag):
            remark = remark_span.get_text(strip=True)
            if remark:
                definitions.append(DictionaryDefinition(text=remark, label="備註"))

        return DictionaryEntry(
            traditional=traditional,
            simplified=simplified,
            pinyin=pinyin,
            jyutping=jyutping,
            frequency=0.0,
            definitions=definitions,
        )

    def scrape(
        self,
        force: bool = False,
        max_words: int | None = None,
    ) -> tuple[DictionarySource, list[DictionaryEntry]]:
        """Scrape CUHK data into source metadata and dictionary entries.

        Arguments:
            force: whether to ignore existing artifacts and rebuild
            max_words: optional max number of discovered words to scrape
        Returns:
            source metadata and scraped dictionary entries
        """
        if force or max_words is not None:
            for scraped_path in self.scraped_dir_path.glob("*.html"):
                scraped_path.unlink()
                logger.info(f"Removed stale scraped page: {scraped_path}")

        logger.info("Discovering CUHK word links")
        word_links = self.load_word_links(force=force)
        logger.info(f"Discovered {len(word_links)} CUHK word link(s)")
        if max_words is not None:
            word_links = word_links[:max_words]
            logger.info(f"Limiting CUHK scrape to {len(word_links)} word(s)")

        logger.info("Scraping CUHK word pages")
        self.scrape_word_pages(
            word_links, skip_existing=not force and max_words is None
        )
        logger.info("Parsing scraped CUHK word pages")
        entries = self.parse_scraped_pages()
        logger.info(f"Parsed {len(entries)} CUHK entry(ies)")
        return CUHK_SOURCE, entries

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
                logger.info(f"Skipping item {index} ({item}): invalid URL")
                continue

            variant_file_paths = self._get_variant_file_paths(item)
            if skip_existing and all(path.exists() for path in variant_file_paths):
                continue

            html = self._fetch_text(url)
            for variant_file_path in variant_file_paths:
                variant_file_path.write_text(html, encoding="utf-8")
            logger.info(f"Scraped #{index}: {item}")

            if self.max_delay_seconds > 0:
                sleep(random.uniform(self.min_delay_seconds, self.max_delay_seconds))

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
                    f"CUHK request failed (attempt {attempt}/{self.max_retries}): {exc}"
                )
                if attempt < self.max_retries:
                    sleep(1.5)

        if last_exception is None:
            raise RuntimeError("Request failed without an exception")
        raise last_exception

    @staticmethod
    def _get_safe_filename_stem(value: str) -> str:
        """Get a safe filename stem for a dictionary key.

        Arguments:
            value: raw value to encode in path
        Returns:
            safe filename stem
        """
        cleaned = value.strip().replace(" ", "_")
        cleaned = INVALID_FILENAME_CHARS_REGEX.sub("_", cleaned)
        return cleaned

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

    @staticmethod
    def _normalize_hanzi(text: str) -> str:
        """Normalize characters and replace private-use area code points.

        Arguments:
            text: text to normalize
        Returns:
            normalized text
        """
        normalized = hkscs_converter.convert_string(text)
        if RE_PRIVATE_USE_AREA_BMP.search(normalized):
            logger.warning(f"Replacing private-use character(s) in {normalized}")
            normalized = RE_PRIVATE_USE_AREA_BMP.sub(
                PRIVATE_USE_AREA_REPLACEMENT_STRING,
                normalized,
            )
        return normalized

    @staticmethod
    def _read_word_links(word_links_path: Path) -> list[tuple[str, str]]:
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

    @staticmethod
    def _write_word_links(word_links_path: Path, word_links: list[tuple[str, str]]):
        """Write links to TSV.

        Arguments:
            word_links_path: TSV path
            word_links: links to write
        """
        with open(word_links_path, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.writer(outfile, delimiter="\t")
            for item, url in word_links:
                writer.writerow((item, url))
