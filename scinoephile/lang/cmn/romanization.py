#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to cmn text romanization."""

from __future__ import annotations

import re
import unicodedata
from functools import cache
from warnings import catch_warnings, simplefilter

with catch_warnings():
    simplefilter("ignore", SyntaxWarning)
    import jieba
from pypinyin import Style, lazy_pinyin, pinyin
from pypinyin.contrib.tone_convert import tone_to_tone3

from scinoephile.core.romanization import (
    RomanizedTokenKind,
    is_romanized_punctuation,
    join_romanized_tokens,
    normalize_romanized_punctuation,
)
from scinoephile.core.text import RE_HANZI

__all__ = [
    "get_cmn_char_romanized",
    "get_cmn_pinyin_query_strings",
    "get_cmn_text_romanized",
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
RE_CMN_WHITESPACE = re.compile(r"(\s+)")


@cache
def get_cmn_char_romanized(text: str) -> str:
    """Get Mandarin pinyin romanization of a Hanzi character or short text.

    Arguments:
        text: Hanzi character or short text
    Returns:
        Mandarin pinyin romanization, or empty string for non-Hanzi text
    """
    return " ".join(lazy_pinyin(text, style=Style.TONE, errors="ignore", strict=False))


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


def get_cmn_text_romanized(text: str) -> str:
    """Get the Mandarin pinyin romanization of Hanzi text.

    Arguments:
        text: Hanzi text
    Returns:
        Mandarin pinyin romanization
    """
    lines: list[str] = []
    for line in text.split("\n"):
        line_output = ""
        open_symmetric_quotes: set[str] = set()
        pending_separator = ""
        for section in RE_CMN_WHITESPACE.split(line.strip()):
            if not section:
                continue
            if section.isspace():
                if line_output:
                    if "\u3000" in section:
                        pending_separator = "  "
                    else:
                        pending_separator = " "
                continue

            romanized_section = _get_cmn_section_romanized(
                section, open_symmetric_quotes
            )
            if romanized_section:
                if line_output and pending_separator:
                    line_output = f"{line_output}{pending_separator}"
                line_output = f"{line_output}{romanized_section}"
                pending_separator = ""
        lines.append(line_output)
    return "\n".join(lines).strip()


def _get_cmn_section_romanized(
    section: str,
    open_symmetric_quotes: set[str],
) -> str:
    """Get Mandarin pinyin romanization for a whitespace-delimited section.

    Arguments:
        section: text section to romanize
        open_symmetric_quotes: straight quotes open before this section
    Returns:
        pinyin romanization for this section
    """
    tokens: list[str] = []
    token_kinds: list[RomanizedTokenKind] = []
    for word in jieba.cut(section):
        for token, token_kind in _get_cmn_word_romanization_tokens(word):
            tokens.append(token)
            token_kinds.append(token_kind)
    return join_romanized_tokens(tokens, open_symmetric_quotes, token_kinds)


def _get_cmn_word_romanization_tokens(
    word: str,
) -> list[tuple[str, RomanizedTokenKind]]:
    """Get romanization tokens for a Jieba word.

    Arguments:
        word: word segmented by Jieba
    Returns:
        romanized text and punctuation tokens
    """
    tokens: list[tuple[str, RomanizedTokenKind]] = []
    current_chars: list[str] = []
    current_kind: str | None = None
    for char in word:
        if is_romanized_punctuation(char):
            char_kind = "punctuation"
        elif RE_HANZI.fullmatch(char) is not None:
            char_kind = "hanzi"
        else:
            char_kind = "raw"

        if char_kind == "punctuation":
            if current_chars and current_kind is not None:
                tokens.append(
                    (
                        _romanize_cmn_token(current_chars, current_kind),
                        "romanized" if current_kind == "hanzi" else "raw",
                    )
                )
            current_chars = []
            current_kind = None
            tokens.append((normalize_romanized_punctuation(char), "punctuation"))
            continue

        if char_kind != current_kind:
            if current_chars and current_kind is not None:
                tokens.append(
                    (
                        _romanize_cmn_token(current_chars, current_kind),
                        "romanized" if current_kind == "hanzi" else "raw",
                    )
                )
            current_chars = []
            current_kind = char_kind
        current_chars.append(char)

    if current_chars and current_kind is not None:
        tokens.append(
            (
                _romanize_cmn_token(current_chars, current_kind),
                "romanized" if current_kind == "hanzi" else "raw",
            )
        )
    return tokens


def _romanize_cmn_token(
    chars: list[str],
    token_kind: str,
) -> str:
    """Romanize a Mandarin token.

    Arguments:
        chars: token characters
        token_kind: kind of token to romanize
    Returns:
        romanized or raw token text
    """
    text = "".join(chars)
    if token_kind == "raw":
        return text
    return "".join(item[0] for item in pinyin(text, style=Style.TONE, strict=False))
