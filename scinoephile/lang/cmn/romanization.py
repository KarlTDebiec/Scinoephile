#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 普通话 text romanization."""

from __future__ import annotations

import re
import unicodedata
from copy import deepcopy

from pypinyin.contrib.tone_convert import tone_to_tone3

from scinoephile.core.subtitles import Series

__all__ = [
    "get_cmn_pinyin_query_strings",
    "get_cmn_romanized",
    "is_accented_pinyin",
    "is_numbered_pinyin",
]

RE_CMN_PINYIN_BASE = (
    r"[A-Za-züÜvV:āáǎàēéěèīíǐìōóǒòūúǔù"
    r"ĀÁǍÀĒÉĚÈĪÍǏÌŌÓǑÒŪÚǓÙêÊḿḾńŃňŇǹǸ]+"
)
# Combining tone marks used for accented pinyin.
# Note: U+0308 COMBINING DIAERESIS is excluded so numbered inputs like "lüe4"
# (NFD: "lu" + U+0308) are not treated as accented pinyin.
RE_CMN_PINYIN_TONE_MARKS = re.compile(r"[\u0300\u0301\u0302\u0304\u030C]")
RE_CMN_PINYIN = re.compile(rf"^{RE_CMN_PINYIN_BASE}[1-5]?$")
RE_CMN_PINYIN_ACCENTED = re.compile(rf"^{RE_CMN_PINYIN_BASE}$")
RE_CMN_PINYIN_NUMBERED = re.compile(rf"^{RE_CMN_PINYIN_BASE}[1-5]$")
RE_CMN_PROHIBITED_TOKEN = re.compile(r"^(gw|kw|ng)|h$", re.IGNORECASE)


def get_cmn_pinyin_query_strings(text: str) -> list[str]:
    """Get normalized pinyin query strings for text.

    Arguments:
        text: Hanyu Pinyin query text with tone marks or tone numbers and optional
          apostrophes
    Returns:
        normalized pinyin query strings using tone numbers
    """
    nfc_text = unicodedata.normalize("NFC", text).replace("’", "'").replace("'", " ")
    nfc_text = nfc_text.strip()
    if not nfc_text:
        return []

    tokens = nfc_text.split()
    if not all(RE_CMN_PINYIN.fullmatch(token) for token in tokens):
        return []

    tokens = [tone_to_tone3(token.lower()).lower() for token in tokens]
    query_strings = {" ".join(tokens)}

    for query_string in tuple(query_strings):
        if "ü" in query_string:
            query_strings.add(query_string.replace("ü", "u:"))
            query_strings.add(query_string.replace("ü", "v"))
        if "u:" in query_string:
            query_strings.add(query_string.replace("u:", "ü"))
            query_strings.add(query_string.replace("u:", "v"))
        if "v" in query_string:
            query_strings.add(query_string.replace("v", "ü"))
            query_strings.add(query_string.replace("v", "u:"))

    return sorted(query_strings)


def get_cmn_romanized(series: Series, append: bool = True) -> Series:
    """Get the Mandarin pinyin romanization of Hanzi series.

    Arguments:
        series: Series for which to get Mandarin pinyin romanization
        append: Whether to append romanization to original text
    Returns:
        Mandarin pinyin romanization of series
    """
    series = deepcopy(series)
    for event in series:
        romanized = _get_cmn_text_romanized(event.text)
        if append:
            if romanized:
                event.text = f"{event.text}\\N{romanized}"
        else:
            event.text = romanized
    return series


def is_accented_pinyin(text: str) -> bool:
    """Check whether text is accented Hanyu Pinyin.

    Arguments:
        text: query text
    Returns:
        whether text appears to be accented pinyin
    """
    # NFC (Normalization Form C) composes characters so tone vowels like ǎ are
    # represented as a single code point instead of a base letter + combining mark.
    nfc_text = unicodedata.normalize("NFC", text)
    # Apostrophes are treated as syllable separators in pinyin, so normalize them
    # to spaces for tokenization.
    nfc_text = nfc_text.replace("’", "'").replace("'", " ").strip()
    if not nfc_text:
        return False
    tokens = nfc_text.split()
    if any(any(char.isdigit() for char in token) for token in tokens):
        return False
    if any(RE_CMN_PROHIBITED_TOKEN.search(token) for token in tokens):
        return False
    if not all(RE_CMN_PINYIN_ACCENTED.fullmatch(token) for token in tokens):
        return False
    # Use NFD so precomposed characters (e.g., ǎ) expose combining tone marks.
    # NFD (Normalization Form D) decomposes precomposed tone vowels into base
    # letter + combining tone mark so we can detect tone marks reliably.
    nfd_text = unicodedata.normalize("NFD", nfc_text)
    return bool(RE_CMN_PINYIN_TONE_MARKS.search(nfd_text))


def is_numbered_pinyin(text: str) -> bool:
    """Check whether text is numbered Hanyu Pinyin.

    Arguments:
        text: query text
    Returns:
        whether text appears to be numbered pinyin
    """
    # NFC (Normalization Form C) composes characters so tone vowels like ǎ are
    # represented as a single code point instead of a base letter + combining mark.
    nfc_text = unicodedata.normalize("NFC", text)
    # Apostrophes are treated as syllable separators in pinyin, so normalize them
    # to spaces for tokenization.
    nfc_text = nfc_text.replace("’", "'").replace("'", " ").strip()
    if not nfc_text:
        return False
    tokens = nfc_text.split()
    # NFD (Normalization Form D) decomposes precomposed tone vowels into base
    # letter + combining tone mark so we can detect tone marks reliably.
    nfd_text = unicodedata.normalize("NFD", nfc_text)
    if RE_CMN_PINYIN_TONE_MARKS.search(nfd_text):
        return False
    if any(token.endswith("5") for token in tokens) and any(
        token[-1] in {"1", "2", "3", "4"} for token in tokens if token[-1].isdigit()
    ):
        return False
    if any(RE_CMN_PROHIBITED_TOKEN.search(token) for token in tokens):
        return False
    return all(RE_CMN_PINYIN_NUMBERED.fullmatch(token) for token in tokens)


def _get_cmn_text_romanized(text: str) -> str:
    """Get the Mandarin pinyin romanization of Hanzi text.

    Arguments:
        text: query text
    Returns:
        whether text appears to be accented pinyin
    """
    # NFC (Normalization Form C) composes characters so tone vowels like ǎ are
    # represented as a single code point instead of a base letter + combining mark.
    nfc_text = unicodedata.normalize("NFC", text)
    # Apostrophes are treated as syllable separators in pinyin, so normalize them
    # to spaces for tokenization.
    nfc_text = nfc_text.replace("’", "'").replace("'", " ").strip()
    if not nfc_text:
        return False
    tokens = nfc_text.split()
    if any(any(char.isdigit() for char in token) for token in tokens):
        return False
    if any(RE_CMN_PROHIBITED_TOKEN.search(token) for token in tokens):
        return False
    if not all(RE_CMN_PINYIN_ACCENTED.fullmatch(token) for token in tokens):
        return False
    # Use NFD so precomposed characters (e.g., ǎ) expose combining tone marks.
    # NFD (Normalization Form D) decomposes precomposed tone vowels into base
    # letter + combining tone mark so we can detect tone marks reliably.
    nfd_text = unicodedata.normalize("NFD", nfc_text)
    return bool(RE_CMN_PINYIN_TONE_MARKS.search(nfd_text))


def is_numbered_pinyin(text: str) -> bool:
    """Check whether text is numbered Hanyu Pinyin.

    Arguments:
        text: query text
    Returns:
        whether text appears to be numbered pinyin
    """
    # NFC (Normalization Form C) composes characters so tone vowels like ǎ are
    # represented as a single code point instead of a base letter + combining mark.
    nfc_text = unicodedata.normalize("NFC", text)
    # Apostrophes are treated as syllable separators in pinyin, so normalize them
    # to spaces for tokenization.
    nfc_text = nfc_text.replace("’", "'").replace("'", " ").strip()
    if not nfc_text:
        return False
    tokens = nfc_text.split()
    # NFD (Normalization Form D) decomposes precomposed tone vowels into base
    # letter + combining tone mark so we can detect tone marks reliably.
    nfd_text = unicodedata.normalize("NFD", nfc_text)
    if RE_CMN_PINYIN_TONE_MARKS.search(nfd_text):
        return False
    if any(token.endswith("5") for token in tokens) and any(
        token[-1] in {"1", "2", "3", "4"} for token in tokens if token[-1].isdigit()
    ):
        return False
    if any(RE_CMN_PROHIBITED_TOKEN.search(token) for token in tokens):
        return False
    return all(RE_CMN_PINYIN_NUMBERED.fullmatch(token) for token in tokens)
