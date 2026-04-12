#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Detect dictionary query language for 中文/粤文 lookups."""

from __future__ import annotations

import re
import unicodedata
from enum import StrEnum

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.lang.cmn.romanization import get_cmn_pinyin_query_strings
from scinoephile.lang.yue.romanization import get_yue_jyutping_query_strings
from scinoephile.lang.zho.conversion import OpenCCConfig, get_zho_text_converted
from scinoephile.multilang.dictionaries import LookupDirection

__all__ = [
    "DictionaryQueryLanguage",
    "detect_dictionary_query_language",
    "get_dictionary_lookup_direction",
]

RE_HANZI = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
PINYIN_TONE_MARKS = {
    "\u0300",  # grave
    "\u0301",  # acute
    "\u0302",  # circumflex
    "\u0304",  # macron
    "\u0308",  # diaeresis
    "\u030c",  # caron
}
YALE_TONE_MARKS = {
    "\u0300",  # grave
    "\u0301",  # acute
    "\u0304",  # macron
}


class DictionaryQueryLanguage(StrEnum):
    """Language classification for dictionary queries."""

    simplified = "simplified"
    """Simplified Chinese Hanzi."""

    traditional = "traditional"
    """Traditional Chinese Hanzi."""

    cmn_pinyin = "cmn_pinyin"
    """Mandarin Hanyu Pinyin with tone marks."""

    yue_yale = "yue_yale"
    """Cantonese Yale romanization with tone marks."""


def detect_dictionary_query_language(query: str) -> DictionaryQueryLanguage:
    """Detect the language category for a dictionary query.

    Arguments:
        query: dictionary query text
    Returns:
        detected query language
    Raises:
        ScinoephileError: If query language is mixed or ambiguous
    """
    query = query.strip()
    if not query:
        raise ScinoephileError("Dictionary query is empty.")

    has_hanzi = _contains_hanzi(query)
    has_latin = _contains_latin(query)
    has_digits = any(char.isdigit() for char in query)

    if has_hanzi:
        if has_latin or has_digits:
            raise ScinoephileError(
                "Dictionary queries must be exclusively Hanzi or romanization, "
                "not mixed."
            )
        return _detect_hanzi_variant(query)

    if not has_latin:
        raise ScinoephileError(
            "Dictionary queries must use Hanzi or accented romanization."
        )
    if has_digits:
        raise ScinoephileError(
            "Dictionary queries must use accented romanization (no digits)."
        )

    pinyin_match = _is_accented_pinyin_query(query)
    yale_match = _is_accented_yale_query(query)

    if pinyin_match and yale_match:
        raise ScinoephileError(
            "Dictionary query romanization is ambiguous between pinyin and Yale."
        )
    if pinyin_match:
        return DictionaryQueryLanguage.cmn_pinyin
    if yale_match:
        return DictionaryQueryLanguage.yue_yale

    raise ScinoephileError(
        "Dictionary queries must use accented Hanyu Pinyin or accented Yale."
    )


def get_dictionary_lookup_direction(
    language: DictionaryQueryLanguage,
) -> LookupDirection:
    """Get lookup direction for a detected query language.

    Arguments:
        language: detected query language
    Returns:
        lookup direction for dictionary search
    """
    if language in (
        DictionaryQueryLanguage.cmn_pinyin,
        DictionaryQueryLanguage.simplified,
        DictionaryQueryLanguage.traditional,
    ):
        return LookupDirection.CMN_TO_YUE
    return LookupDirection.YUE_TO_CMN


def _contains_hanzi(text: str) -> bool:
    """Check whether text contains Hanzi characters.

    Arguments:
        text: query text
    Returns:
        whether Hanzi characters are present
    """
    return RE_HANZI.search(text) is not None


def _contains_latin(text: str) -> bool:
    """Check whether text contains Latin letters.

    Arguments:
        text: query text
    Returns:
        whether Latin letters are present
    """
    return any(_is_latin_letter(char) for char in text)


def _is_latin_letter(char: str) -> bool:
    """Check whether a character is a Latin letter.

    Arguments:
        char: character to check
    Returns:
        whether character is a Latin letter
    """
    if not char.isalpha():
        return False
    return "LATIN" in unicodedata.name(char, "")


def _detect_hanzi_variant(query: str) -> DictionaryQueryLanguage:
    """Detect whether Hanzi query is simplified or traditional.

    Arguments:
        query: Hanzi query text
    Returns:
        simplified or traditional language label
    Raises:
        ScinoephileError: If the Hanzi variant is mixed or ambiguous
    """
    simplified = get_zho_text_converted(query, OpenCCConfig.t2s)
    traditional = get_zho_text_converted(query, OpenCCConfig.s2t)

    if query == simplified and query != traditional:
        return DictionaryQueryLanguage.simplified
    if query == traditional and query != simplified:
        return DictionaryQueryLanguage.traditional
    if query == simplified and query == traditional:
        raise ScinoephileError(
            "Dictionary query Hanzi is ambiguous between simplified and traditional."
        )
    raise ScinoephileError("Dictionary query Hanzi mixes simplified and traditional.")


def _is_accented_pinyin_query(query: str) -> bool:
    """Check whether query is accented Hanyu Pinyin.

    Arguments:
        query: romanized query text
    Returns:
        whether query appears to be accented pinyin
    """
    normalized = (
        unicodedata.normalize("NFC", query).replace("’", "'").replace("'", " ").strip()
    )
    if not normalized:
        return False
    tokens = normalized.split()
    if any(token.lower().endswith("h") for token in tokens):
        return False
    if not get_cmn_pinyin_query_strings(query):
        return False
    return _contains_diacritic(query, PINYIN_TONE_MARKS)


def _is_accented_yale_query(query: str) -> bool:
    """Check whether query is accented Yale romanization.

    Arguments:
        query: romanized query text
    Returns:
        whether query appears to be accented Yale
    """
    if not _contains_diacritic(query, YALE_TONE_MARKS):
        return False
    return bool(get_yue_jyutping_query_strings(query))


def _contains_diacritic(text: str, marks: set[str]) -> bool:
    """Check whether text contains any diacritic marks.

    Arguments:
        text: text to inspect
        marks: combining diacritic marks to detect
    Returns:
        whether any of the marks are present
    """
    normalized = unicodedata.normalize("NFD", text)
    return any(char in marks for char in normalized)
