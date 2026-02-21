#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary scraping, parsing, and storage.

This module ports the CUHK dictionary ingestion flow from `external/jyut-dict`
while aligning with Scinoephile style and runtime conventions.
"""

from __future__ import annotations

import csv
import importlib
import random
import re
import sqlite3
from logging import getLogger
from os.path import expandvars
from pathlib import Path
from time import sleep
from urllib.parse import parse_qs, urljoin, urlparse

import opencc
import requests
from bs4 import BeautifulSoup, Tag
from pypinyin import Style, lazy_pinyin

from scinoephile.core.paths import get_runtime_cache_dir_path

from .models import DictionaryDefinition, DictionaryEntry, DictionarySource
from .sqlite_schema import (
    create_tables,
    drop_tables,
    generate_indices,
    insert_definition,
    insert_entry,
    insert_source,
    write_database_version,
)

hkscs_converter = None
try:  # pragma: no cover - optional dependency
    hkscs_converter = importlib.import_module("hkscs_unicode_converter").converter
except ImportError:
    # Fallback to raw CUHK text when HK-SCS converter is unavailable.
    pass

__all__ = [
    "CuhkDictionaryBuilder",
]

logger = getLogger(__name__)

BASE_URL = "https://apps.itsc.cuhk.edu.hk/hanyu/Page/"
TERMS_URL = "https://apps.itsc.cuhk.edu.hk/hanyu/Page/Terms.aspx"
CUHK_HOSTNAME = "apps.itsc.cuhk.edu.hk"
CUHK_TERMS_PATH = "/hanyu/Page/Terms.aspx"
CUHK_WORD_PATH = "/hanyu/Page/Word.aspx"
CUHK_SEARCH_PATH = "/hanyu/Page/Search.aspx"
CUHK_WORD_RESULT_PATHS = {CUHK_WORD_PATH, CUHK_SEARCH_PATH}

PRIVATE_USE_AREA_REGEX = re.compile(r"[\ue000-\uf8ff]")
PRIVATE_USE_AREA_REPLACEMENT_STRING = "☒"

LABEL_ID_REGEX = re.compile(r"MainContent_repeaterRecord_lbl詞彙類別_.*")
JYUTPING_LETTERS_ID_REGEX = re.compile(r"MainContent_repeaterRecord_lbl粵語拼音_.*")
JYUTPING_NUMBERS_ID_REGEX = re.compile(r"MainContent_repeaterRecord_lbl聲調_.*")
JYUTPING_NUMBERS_REGEX = re.compile(r"(?:\d\*)*(\d+)")
MEANING_ID_REGEX = re.compile(
    r"MainContent_repeaterRecord_repeaterTranslation_\d+_lblTranslation_.*"
)
REMARK_ID_REGEX = re.compile(r"MainContent_repeaterRecord_lblRemark_.*")

JYUTPING_TONE_MAP = {"7": "1", "8": "3", "9": "6"}
INVALID_FILENAME_CHARS_REGEX = re.compile(r"[\\/:*?\"<>|]")

CUHK_SOURCE = DictionarySource(
    name="現代標準漢語與粵語對照資料庫",
    shortname="CUHK",
    version="2014",
    description=(
        "Comparative Database of Modern Standard Chinese and Cantonese "
        "(Chinese University of Hong Kong)."
    ),
    legal="(c) 2014 保留版權 香港中文大學 中國語言及文學系",
    link="https://apps.itsc.cuhk.edu.hk/hanyu/Page/Cover.aspx",
    update_url="",
    other="words",
)


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

    def load_word_links(self, force_refresh: bool = False) -> list[tuple[str, str]]:
        """Load or fetch CUHK word links.

        Arguments:
            force_refresh: whether to ignore cached link file
        Returns:
            list of (word, url)
        """
        if self.word_links_path.exists() and not force_refresh:
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

    def parse_scraped_pages(self) -> list[DictionaryEntry]:
        """Parse scraped CUHK pages into normalized entries.

        Returns:
            parsed dictionary entries
        """
        entries: list[DictionaryEntry] = []
        for index, html_path in enumerate(sorted(self.scraped_dir_path.glob("*.html"))):
            if index and index % 100 == 0:
                logger.info("Parsed %s CUHK entries", index)

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
                "Skipping malformed CUHK page without ChiCharFix: %s", html_path
            )
            return None

        traditional = self._normalize_hanzi(text_span.get_text(strip=True))
        simplified = self.opencc_converter.convert(traditional)

        file_word = self._normalize_hanzi(html_path.stem)
        if file_word != traditional:
            logger.warning(
                "Parsed word '%s' does not match filename '%s' (%s)",
                traditional,
                file_word,
                html_path,
            )
            # Keep parsing: filename stems are cache keys and may be sanitized.

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
                "Skipping CUHK page with mismatched jyutping letters (%s) "
                "and tones (%s): %s",
                len(jyutping_letters),
                len(jyutping_numbers),
                html_path,
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

    def write_database(self, entries: list[DictionaryEntry]):
        """Write entries to SQLite.

        Arguments:
            entries: normalized dictionary entries
        """
        self.cache_dir_path.mkdir(parents=True, exist_ok=True)
        if self.database_path.exists():
            self.database_path.unlink()

        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()

            write_database_version(cursor)
            drop_tables(cursor)
            create_tables(cursor)

            source_id = insert_source(cursor, CUHK_SOURCE)

            for entry in entries:
                entry_id = insert_entry(
                    cursor,
                    entry.traditional,
                    entry.simplified,
                    entry.pinyin,
                    entry.jyutping,
                    entry.frequency,
                )

                for definition in entry.definitions:
                    insert_definition(
                        cursor,
                        definition.text,
                        definition.label,
                        entry_id,
                        source_id,
                    )

            generate_indices(cursor)
            connection.commit()

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

    def _normalize_hanzi(self, text: str) -> str:
        """Normalize characters and replace private-use area code points.

        Arguments:
            text: text to normalize
        Returns:
            normalized text
        """
        normalized = text
        if hkscs_converter is not None:
            normalized = hkscs_converter.convert_string(normalized)

        if PRIVATE_USE_AREA_REGEX.search(normalized):
            logger.warning("Replacing private-use character(s) in %s", normalized)
            normalized = PRIVATE_USE_AREA_REGEX.sub(
                PRIVATE_USE_AREA_REPLACEMENT_STRING,
                normalized,
            )
        return normalized

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
