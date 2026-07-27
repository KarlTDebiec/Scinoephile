#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary scraping and parsing."""

from __future__ import annotations

import random
import re
from logging import getLogger
from pathlib import Path
from time import sleep
from typing import TypedDict
from urllib.parse import parse_qs, urljoin, urlparse

import opencc
import requests
from bs4 import BeautifulSoup, Tag
from pypinyin import Style, lazy_pinyin

from scinoephile.core import UnsupportedCharacterError
from scinoephile.core.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
)
from scinoephile.lang.yue.conversion import get_yue_converted

from .cache import CuhkResponseCache
from .constants import (
    BASE_URL,
    CUHK_HOSTNAME,
    CUHK_SOURCE,
    CUHK_TERMS_PATH,
    CUHK_WORD_RESULT_PATHS,
    INVALID_FILENAME_CHARS_REGEX,
    JYUTPING_LETTERS_ID_REGEX,
    JYUTPING_NUMBERS_ID_REGEX,
    JYUTPING_TONE_MAP,
    LABEL_ID_REGEX,
    MEANING_ID_REGEX,
    REMARK_ID_REGEX,
    TERMS_URL,
)

__all__ = ["CuhkDictionaryScraper", "CuhkDictionaryScraperKwargs"]

logger = getLogger(__name__)

CUHK_HEADWORD_ALTERNATE_REGEX = re.compile(r"\([^()]+\)")
CUHK_TONE_TOKEN_REGEX = re.compile(r"\d(?:\(\d(?:\*\d)?\)|\*\d)?")
CUHK_TONE_ALTERNATE_REGEX = re.compile(r"^(?P<primary>\d)\((?P<alternate>\d)\)$")
CUHK_TONE_SANDHI_REGEX = re.compile(r"^(?P<original>\d)\*(?P<changed>\d)$")
CUHK_TONE_SANDHI_ALTERNATE_REGEX = re.compile(
    r"^(?P<primary>\d)\((?P<original>\d)\*(?P<changed>\d)\)$"
)


class CuhkDictionaryScraperKwargs(TypedDict, total=False):
    """Keyword arguments for CuhkDictionaryScraper initialization."""

    cache_root_path: Path | None
    """Root directory beneath which to cache CUHK scrape artifacts."""
    min_delay_seconds: float
    """Minimum delay between HTTP requests."""
    max_delay_seconds: float
    """Maximum delay between HTTP requests."""
    request_timeout_seconds: float
    """Per-request timeout in seconds."""
    max_retries: int
    """Maximum attempts for failed requests."""
    overwrite_cache: bool
    """Whether to replace matching cached HTTP responses."""
    session: requests.Session | None
    """Requests session for dependency injection."""


class CuhkDictionaryScraper:
    """Scraper for CUHK dictionary cache and parsed entry data."""

    def __init__(
        self,
        cache_root_path: Path | None = None,
        *,
        min_delay_seconds: float = 1.0,
        max_delay_seconds: float = 5.0,
        request_timeout_seconds: float = 30.0,
        max_retries: int = 5,
        overwrite_cache: bool = False,
        session: requests.Session | None = None,
    ):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache scrape artifacts
            min_delay_seconds: minimum delay between HTTP requests
            max_delay_seconds: maximum delay between HTTP requests
            request_timeout_seconds: per-request timeout
            max_retries: max attempts for failed requests
            overwrite_cache: whether to replace matching cached HTTP responses
            session: requests session for dependency injection
        """
        self.discovery_cache = CuhkResponseCache(
            cache_root_path, "cuhk-discovery", overwrite_cache
        )
        """Cache of CUHK discovery pages."""
        self.scraped_cache = CuhkResponseCache(
            self.discovery_cache.cache_root_path, "cuhk-pages", overwrite_cache
        )
        """Cache of CUHK word pages."""

        if max_delay_seconds < min_delay_seconds:
            raise ValueError("max_delay_seconds must be >= min_delay_seconds")
        self.min_delay_seconds = min_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.request_timeout_seconds = request_timeout_seconds
        self.max_retries = max_retries
        self.session = session or requests.Session()
        self.opencc_converter = opencc.OpenCC("hk2s")

    def discover_word_links(
        self, max_words: int | None = None
    ) -> list[tuple[str, str]]:
        """Discover CUHK word pages.

        Arguments:
            max_words: optional max number of words to discover
        Returns:
            list of (word, url)
        """
        if max_words is not None and max_words <= 0:
            return []

        html = self._get_or_fetch_text(
            TERMS_URL, self.discovery_cache, "terms", cache_label="CUHK terms index"
        )
        soup = BeautifulSoup(html, "html.parser")
        main_panel = soup.find("div", id="MainContent_panelTermsIndex")
        if not isinstance(main_panel, Tag):
            raise RuntimeError("Unable to find CUHK terms index panel")

        category_links: list[str] = []
        for anchor in main_panel.find_all("a", href=True):
            category_url = urljoin(BASE_URL, str(anchor["href"]).strip())
            parsed_url = urlparse(category_url)
            query_params = parse_qs(parsed_url.query)
            if (
                parsed_url.netloc != CUHK_HOSTNAME
                or parsed_url.path != CUHK_TERMS_PATH
                or "target" not in query_params
            ):
                continue
            category_links.append(category_url)

        seen_word_links: set[tuple[str, str]] = set()
        word_links: list[tuple[str, str]] = []
        for category_link in category_links:
            category_html = self._get_or_fetch_text(
                category_link,
                self.discovery_cache,
                self._get_category_cache_stem(category_link),
                cache_label="CUHK category",
            )
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
                    continue
                if parsed_word_url.path not in CUHK_WORD_RESULT_PATHS:
                    continue
                pair = (item, url)
                if pair in seen_word_links:
                    continue
                seen_word_links.add(pair)
                word_links.append(pair)
                if max_words is not None and len(word_links) >= max_words:
                    logger.info(
                        f"Stopping CUHK discovery after {len(word_links)} word(s)"
                    )
                    return word_links

        return word_links

    def parse_scraped_pages(
        self, stems: list[str] | None = None
    ) -> list[DictionaryEntry]:
        """Parse scraped CUHK pages into normalized entries.

        Arguments:
            stems: response stems to parse, or None to parse all cached responses
        Returns:
            parsed dictionary entries
        """
        if stems is None:
            stems = self.scraped_cache.get_stems()
        entries: list[DictionaryEntry] = []
        for index, stem in enumerate(stems):
            if index and index % 100 == 0:
                logger.info(f"Parsed {index} CUHK entries")

            html = self.scraped_cache.load(stem)
            if html is None:
                continue
            html_path = self.scraped_cache.get_path(stem)
            entry = self.parse_word_html(html, html_path)
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
        html = html_path.read_text(encoding="utf-8")
        return self.parse_word_html(html, html_path)

    def parse_word_files(self, html_paths: list[Path]) -> list[DictionaryEntry]:
        """Parse selected scraped CUHK pages into normalized entries.

        Arguments:
            html_paths: scraped HTML paths to parse
        Returns:
            parsed dictionary entries
        """
        entries: list[DictionaryEntry] = []
        for html_path in html_paths:
            entry = self.parse_word_file(html_path)
            if entry is not None:
                entries.append(entry)

        return entries

    def parse_word_html(self, html: str, html_path: Path) -> DictionaryEntry | None:
        """Parse the contents of one CUHK word page.

        Arguments:
            html: CUHK word page HTML
            html_path: source path used for identity and logging
        Returns:
            parsed entry, if valid
        """
        soup = BeautifulSoup(html, "html.parser")

        text_span = soup.find("span", class_="ChiCharFix")
        if not isinstance(text_span, Tag):
            logger.warning(
                f"Skipping malformed CUHK page without ChiCharFix: {html_path}"
            )
            return None

        raw_traditional = self._strip_cuhk_headword_alternates(
            text_span.get_text(strip=True)
        )
        raw_file_word = self._strip_cuhk_headword_alternates(html_path.stem)
        try:
            traditional = get_yue_converted(raw_traditional)
            file_word = get_yue_converted(raw_file_word)
        except UnsupportedCharacterError as exc:
            logger.warning(f"Skipping CUHK page {html_path}: {exc}")
            return None
        if traditional != raw_traditional:
            logger.info(
                "HKSCS normalization changed text: "
                f"{raw_traditional!r} -> {traditional!r}"
            )
        if file_word != raw_file_word:
            logger.info(
                f"HKSCS normalization changed text: {raw_file_word!r} -> {file_word!r}"
            )

        simplified = self.opencc_converter.convert(traditional)

        if file_word != traditional:
            logger.warning(
                f"Parsed word '{traditional}' does not match filename "
                f"'{file_word}' ({html_path})"
            )

        label_span = soup.find("span", id=LABEL_ID_REGEX)
        label = label_span.get_text(strip=True) if isinstance(label_span, Tag) else ""

        jyutping_syllables_span = soup.find("span", id=JYUTPING_LETTERS_ID_REGEX)
        jyutping_syllables = (
            jyutping_syllables_span.get_text(strip=True).split()
            if isinstance(jyutping_syllables_span, Tag)
            else []
        )
        jyutping_numbers_span = soup.find("span", id=JYUTPING_NUMBERS_ID_REGEX)
        raw_numbers = (
            jyutping_numbers_span.get_text(" ", strip=True)
            if isinstance(jyutping_numbers_span, Tag)
            else ""
        )
        jyutping_numbers = self._parse_jyutping_numbers(raw_numbers)
        if len(jyutping_syllables) != len(jyutping_numbers):
            logger.warning(
                "Skipping CUHK page with mismatched jyutping syllables "
                f"({len(jyutping_syllables)}) and tones "
                f"({len(jyutping_numbers)}): {html_path}; "
                f"syllables={jyutping_syllables!r}; raw_tones={raw_numbers!r}; "
                f"parsed_tones={jyutping_numbers!r}"
            )
            return None
        jyutping = " ".join(
            f"{syllable}{number}"
            for syllable, number in zip(
                jyutping_syllables, jyutping_numbers, strict=False
            )
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
        self, max_words: int | None = None
    ) -> tuple[DictionarySource, list[DictionaryEntry]]:
        """Scrape CUHK data into source metadata and dictionary entries.

        Arguments:
            max_words: optional max number of discovered words to scrape
        Returns:
            source metadata and scraped dictionary entries
        """
        logger.info("Discovering CUHK word links")
        word_links = self.discover_word_links(max_words=max_words)
        logger.info(f"Discovered {len(word_links)} CUHK word link(s)")

        logger.info("Scraping CUHK word pages")
        self.scrape_word_pages(word_links)
        logger.info("Parsing scraped CUHK word pages")
        stems: list[str] | None = None
        if max_words is not None:
            stems = []
            for item, _ in word_links:
                for stem in self._get_variant_stems(item):
                    if stem not in stems:
                        stems.append(stem)
        entries = self.parse_scraped_pages(stems)
        logger.info(f"Parsed {len(entries)} CUHK entry(ies)")
        return CUHK_SOURCE, entries

    def scrape_word_pages(self, word_links: list[tuple[str, str]]):
        """Scrape CUHK word pages into cached HTML files.

        Arguments:
            word_links: list of (word, url)
        """
        for index, (item, url) in enumerate(word_links, start=1):
            if url == "?":
                logger.info(f"Skipping item {index} ({item}): invalid URL")
                continue

            variant_stems = self._get_variant_stems(item)
            cached_html = [self.scraped_cache.load(stem) for stem in variant_stems]
            if all(html is not None for html in cached_html):
                logger.info(f"Loaded word page from cache #{index}: {item}")
                continue

            html = self._fetch_text(url)
            for variant_stem in variant_stems:
                self.scraped_cache.save(variant_stem, html)
            logger.info(f"Scraped #{index}: {item}")

            if self.max_delay_seconds > 0:
                sleep(random.uniform(self.min_delay_seconds, self.max_delay_seconds))

    def _get_or_fetch_text(
        self,
        url: str,
        cache: CuhkResponseCache,
        cache_stem: str,
        cache_label: str | None = None,
    ) -> str:
        """Load a response from cache or fetch and cache it.

        Arguments:
            url: URL to fetch
            cache: response cache
            cache_stem: safe filename stem identifying the response
            cache_label: optional label to include in logs
        Returns:
            loaded or fetched response body
        """
        contents = cache.load(cache_stem)
        if contents is not None:
            description = url if cache_label is None else f"{cache_label}: {url}"
            logger.info(f"Loaded from cache: {description}")
            return contents

        contents = self._fetch_text(url, cache_label)
        cache.save(cache_stem, contents)
        return contents

    def _fetch_text(self, url: str, cache_label: str | None = None) -> str:
        """Fetch text with retry and timeout.

        Arguments:
            url: URL to fetch
            cache_label: optional label to include in cache logs
        Returns:
            fetched text content
        Raises:
            requests.RequestException: if all retry attempts fail
        """
        cache_description = url if cache_label is None else f"{cache_label}: {url}"
        last_exception: requests.RequestException | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Fetching: {cache_description}")
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

    def _get_category_cache_stem(self, category_url: str) -> str:
        """Get the cache stem for one CUHK category page.

        Arguments:
            category_url: CUHK category URL
        Returns:
            discovery cache stem
        """
        parsed_url = urlparse(category_url)
        target_name = parse_qs(parsed_url.query).get("target", [""])[0]
        stem = self._get_safe_filename_stem(target_name or "terms")
        return stem

    def _get_variant_stems(self, item: str) -> list[str]:
        """Get cache stems for one CUHK word item.

        Arguments:
            item: item string, potentially with slash-separated variants
        Returns:
            variant cache stems
        """
        stems: set[str] = set()
        for variant in item.split("/"):
            stem = self._get_safe_filename_stem(variant.strip())
            if stem:
                stems.add(stem)
        return sorted(stems)

    @classmethod
    def _parse_jyutping_numbers(cls, raw_numbers: str) -> list[str]:
        """Parse CUHK tone text into one normalized tone per syllable.

        Arguments:
            raw_numbers: raw CUHK tone text
        Returns:
            normalized tone numbers
        """
        condensed = raw_numbers.replace(" ", "")
        tokens = CUHK_TONE_TOKEN_REGEX.findall(condensed)
        return [cls._normalize_jyutping_tone_token(token) for token in tokens]

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

    @staticmethod
    def _normalize_jyutping_tone_token(token: str) -> str:
        """Normalize one CUHK tone token to a single output tone.

        Arguments:
            token: raw CUHK tone token
        Returns:
            normalized tone number
        """
        sandhi_alternate_match = CUHK_TONE_SANDHI_ALTERNATE_REGEX.fullmatch(token)
        if sandhi_alternate_match is not None:
            changed = sandhi_alternate_match.group("changed")
            logger.info(
                "Observed CUHK sandhi alternate tone token "
                f"{token!r}; using changed tone {changed!r}"
            )
            return JYUTPING_TONE_MAP.get(changed, changed)

        alternate_match = CUHK_TONE_ALTERNATE_REGEX.fullmatch(token)
        if alternate_match is not None:
            primary = alternate_match.group("primary")
            logger.info(
                "Observed CUHK alternate tone token "
                f"{token!r}; using primary tone {primary!r}"
            )
            return JYUTPING_TONE_MAP.get(primary, primary)

        sandhi_match = CUHK_TONE_SANDHI_REGEX.fullmatch(token)
        if sandhi_match is not None:
            changed = sandhi_match.group("changed")
            logger.info(
                "Observed CUHK sandhi tone token "
                f"{token!r}; using changed tone {changed!r}"
            )
            return JYUTPING_TONE_MAP.get(changed, changed)

        return JYUTPING_TONE_MAP.get(token, token)

    @staticmethod
    def _strip_cuhk_headword_alternates(text: str) -> str:
        """Remove CUHK parenthesized alternate spellings from a headword.

        Arguments:
            text: raw CUHK headword text
        Returns:
            headword text without parenthesized alternates
        """
        collapsed = CUHK_HEADWORD_ALTERNATE_REGEX.sub("", text)
        if collapsed != text:
            logger.info(
                "Removed CUHK parenthesized alternate spelling(s): "
                f"{text!r} -> {collapsed!r}"
            )
        return collapsed
