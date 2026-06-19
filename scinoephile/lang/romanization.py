#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared helpers for romanized text formatting."""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable

from scinoephile.core.text import FULL_PUNC_CHARS, FULL_TO_HALF_PUNC, HALF_PUNC_CHARS

__all__ = [
    "is_romanized_punctuation",
    "join_romanized_tokens",
    "normalize_romanized_punctuation",
]

_ROMANIZED_CLOSING_PUNCTUATION = set(")]}>.,!?;:%”’\"'」』》〉】＞…")
_ROMANIZED_OPENING_PUNCTUATION = set("([{<“‘\"'「『《〈【＜")
_ROMANIZED_PUNCTUATION = {
    **FULL_TO_HALF_PUNC,
    "＜": "＜",
    "＞": "＞",
    "、": ",",
    "。": ".",
    "⋯": "…",
}


def is_romanized_punctuation(text: str) -> bool:
    """Check whether text is punctuation retained during romanization.

    Arguments:
        text: text to check
    Returns:
        whether every character is romanization punctuation
    """
    return bool(text) and all(_is_romanized_punctuation_char(char) for char in text)


def join_romanized_tokens(tokens: Iterable[str]) -> str:
    """Join romanized text and punctuation tokens with readable spacing.

    Arguments:
        tokens: romanized text and punctuation tokens
    Returns:
        formatted romanized text
    """
    output = ""
    for token in tokens:
        if not token:
            continue
        if not output:
            output = token
        elif _requires_space(output, token):
            output = f"{output} {token}"
        else:
            output = f"{output}{token}"
    return output


def normalize_romanized_punctuation(text: str) -> str:
    """Normalize punctuation for romanized text.

    Arguments:
        text: punctuation text to normalize
    Returns:
        punctuation suitable for romanized text
    """
    return "".join(_ROMANIZED_PUNCTUATION.get(char, char) for char in text)


def _is_romanized_punctuation_char(char: str) -> bool:
    """Check whether a character is punctuation retained during romanization.

    Arguments:
        char: character to check
    Returns:
        whether the character is romanization punctuation
    """
    return (
        char in HALF_PUNC_CHARS
        or char in FULL_PUNC_CHARS
        or unicodedata.category(char).startswith("P")
    )


def _requires_space(output: str, token: str) -> bool:
    """Check whether a token requires a preceding space.

    Arguments:
        output: romanized output accumulated so far
        token: token to append
    Returns:
        whether token should be separated from output by a space
    """
    previous_char = output[-1]
    current_char = token[0]
    if _is_romanized_punctuation_char(previous_char) and _is_romanized_punctuation_char(
        current_char
    ):
        return False
    if previous_char in _ROMANIZED_OPENING_PUNCTUATION:
        return False
    return current_char not in _ROMANIZED_CLOSING_PUNCTUATION
