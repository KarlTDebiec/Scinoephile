#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Detect dictionary query language for 中文/粤文 lookups."""

from __future__ import annotations

import re
import unicodedata
from enum import StrEnum

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.lang.cmn.romanization import is_accented_pinyin
from scinoephile.lang.yue.romanization import is_accented_yale
from scinoephile.lang.zho.conversion import (
    OpenCCConfig,
    get_zho_text_converted,
    is_simplified,
    is_traditional,
)
from scinoephile.multilang.dictionaries import LookupDirection

__all__ = [
    "DictionaryQueryLanguage",
    "detect_dictionary_query_language",
    "get_dictionary_lookup_direction",
]

RE_HANZI = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")


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

    has_hanzi = RE_HANZI.search(query) is not None
    has_latin = any(
        char.isalpha() and "LATIN" in unicodedata.name(char, "") for char in query
    )
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

    pinyin_match = is_accented_pinyin(query)
    yale_match = is_accented_yale(query)

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
    simplified_match = is_simplified(query)
    traditional_match = is_traditional(query)
    if simplified_match and traditional_match:
        raise ScinoephileError(
            "Dictionary query Hanzi is ambiguous between simplified and traditional."
        )
    if simplified_match:
        return DictionaryQueryLanguage.simplified
    if traditional_match:
        return DictionaryQueryLanguage.traditional
    if query == simplified and query == traditional:
        raise ScinoephileError(
            "Dictionary query Hanzi is ambiguous between simplified and traditional."
        )
    raise ScinoephileError("Dictionary query Hanzi mixes simplified and traditional.")
