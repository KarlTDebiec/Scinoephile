#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Parsing helpers for CUHK dictionary builder."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag
from hkscs_unicode_converter import converter as hkscs_converter
from pypinyin import Style, lazy_pinyin

from scinoephile.multilang.cmn_yue.dictionaries.dictionary_definition import (
    DictionaryDefinition,
)
from scinoephile.multilang.cmn_yue.dictionaries.dictionary_entry import (
    DictionaryEntry,
)

from .constants import (
    JYUTPING_LETTERS_ID_REGEX,
    JYUTPING_NUMBERS_ID_REGEX,
    JYUTPING_NUMBERS_REGEX,
    JYUTPING_TONE_MAP,
    LABEL_ID_REGEX,
    MEANING_ID_REGEX,
    PRIVATE_USE_AREA_REGEX,
    PRIVATE_USE_AREA_REPLACEMENT_STRING,
    REMARK_ID_REGEX,
)

logger = getLogger(__name__)

__all__ = [
    "CuhkDictionaryBuilderParser",
]


class CuhkDictionaryBuilderParser:
    """Helper object for page-parsing and text-normalization behavior."""

    def __init__(self, scraped_dir_path: Path, opencc_converter: Any):
        """Initialize.

        Arguments:
            scraped_dir_path: directory path for scraped HTML pages
            opencc_converter: OpenCC converter used for traditional->simplified text
        """
        self.scraped_dir_path = scraped_dir_path
        self.opencc_converter = opencc_converter

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

    def _normalize_hanzi(self, text: str) -> str:
        """Normalize characters and replace private-use area code points.

        Arguments:
            text: text to normalize
        Returns:
            normalized text
        """
        normalized = text
        normalized = hkscs_converter.convert_string(normalized)

        if PRIVATE_USE_AREA_REGEX.search(normalized):
            logger.warning("Replacing private-use character(s) in %s", normalized)
            normalized = PRIVATE_USE_AREA_REGEX.sub(
                PRIVATE_USE_AREA_REPLACEMENT_STRING,
                normalized,
            )
        return normalized
