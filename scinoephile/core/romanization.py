#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared helpers for romanized text formatting."""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable
from typing import Literal

from .text import FULL_PUNC_CHARS, FULL_TO_HALF_PUNC, HALF_PUNC_CHARS

__all__ = [
    "RomanizedTokenKind",
    "is_romanized_punctuation",
    "join_romanized_tokens",
    "normalize_romanized_punctuation",
]

type RomanizedTokenKind = Literal["punctuation", "raw", "romanized"]
"""Kind of token being joined into romanized text."""

_ROMANIZED_CLOSING_PUNCTUATION = set(")]}>.,!?;:%”’」』》〉】＞…､｡｣･")
_ROMANIZED_OPENING_PUNCTUATION = set("([{<“‘「『《〈【＜｢･")
_ROMANIZED_RETAINED_FULLWIDTH_PUNCTUATION = {"＜", "＞"}
_ROMANIZED_SYMMETRIC_QUOTES = {'"', "'"}


def is_romanized_punctuation(text: str) -> bool:
    """Check whether text is punctuation retained during romanization.

    Arguments:
        text: text to check
    Returns:
        whether every character is romanization punctuation
    """
    return bool(text) and all(_is_romanized_punctuation_char(char) for char in text)


def join_romanized_tokens(
    tokens: Iterable[str],
    open_symmetric_quotes: set[str],
    token_kinds: Iterable[RomanizedTokenKind],
) -> str:
    """Join romanized text and punctuation tokens with readable spacing.

    Arguments:
        tokens: romanized text and punctuation tokens
        open_symmetric_quotes: straight quotes open before these tokens
        token_kinds: source kinds for the tokens, used to distinguish contractions
          from single-quoted romanized phrases
    Returns:
        formatted romanized text
    """
    token_list: list[str] = []
    token_kind_list: list[RomanizedTokenKind] = []
    for token, token_kind in zip(tokens, token_kinds, strict=True):
        if token:
            token_list.append(token)
            token_kind_list.append(token_kind)
    quote_roles = _get_symmetric_quote_roles(
        token_list, open_symmetric_quotes, token_kind_list
    )
    output = ""
    previous_quote_role: Literal["closing", "infix", "opening"] | None = None
    for token, quote_role in zip(token_list, quote_roles, strict=True):
        if not output:
            output = token
        elif _requires_space(output, token, previous_quote_role, quote_role):
            output = f"{output} {token}"
        else:
            output = f"{output}{token}"
        previous_quote_role = quote_role
    return output


def normalize_romanized_punctuation(text: str) -> str:
    """Normalize punctuation for romanized text.

    Arguments:
        text: punctuation text to normalize
    Returns:
        punctuation suitable for romanized text
    """
    return "".join(
        char
        if char in _ROMANIZED_RETAINED_FULLWIDTH_PUNCTUATION
        else FULL_TO_HALF_PUNC.get(char, char)
        for char in text
    )


def _get_symmetric_quote_roles(
    tokens: list[str],
    open_quotes: set[str],
    token_kinds: list[RomanizedTokenKind],
) -> list[Literal["closing", "infix", "opening"] | None]:
    """Get spacing roles for straight quote tokens.

    Arguments:
        tokens: romanized text and punctuation tokens
        open_quotes: straight quotes open before these tokens
        token_kinds: source kinds for the tokens
    Returns:
        spacing roles for straight quote tokens
    """
    roles: list[Literal["closing", "infix", "opening"] | None] = []
    for index, token in enumerate(tokens):
        if token not in _ROMANIZED_SYMMETRIC_QUOTES:
            roles.append(None)
            continue

        if token in open_quotes:
            roles.append("closing")
            open_quotes.remove(token)
        elif token == "'" and _is_infix_quote_context(index, token_kinds):
            roles.append("infix")
        elif (
            index > 0
            and index == len(tokens) - 1
            and token_kinds[index - 1] in {"raw", "romanized"}
        ):
            roles.append("closing")
        else:
            roles.append("opening")
            open_quotes.add(token)
    return roles


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


def _is_infix_quote_context(
    index: int,
    token_kinds: list[RomanizedTokenKind],
) -> bool:
    """Check whether a single quote joins raw text tokens.

    Arguments:
        index: token index of the quote
        token_kinds: source kinds for the tokens
    Returns:
        whether the quote should be treated as infix punctuation
    """
    return (
        index > 0
        and index + 1 < len(token_kinds)
        and token_kinds[index - 1] == "raw"
        and token_kinds[index + 1] == "raw"
    )


def _requires_space(
    output: str,
    token: str,
    previous_quote_role: Literal["closing", "infix", "opening"] | None,
    quote_role: Literal["closing", "infix", "opening"] | None,
) -> bool:
    """Check whether a token requires a preceding space.

    Arguments:
        output: romanized output accumulated so far
        token: token to append
        previous_quote_role: role of the preceding token if it was a straight quote
        quote_role: role of the token if it is a straight quote
    Returns:
        whether token should be separated from output by a space
    """
    previous_char = output[-1]
    current_char = token[0]
    if previous_quote_role in {"infix", "opening"}:
        return False
    if quote_role in {"closing", "infix"}:
        return False
    if _is_romanized_punctuation_char(previous_char) and _is_romanized_punctuation_char(
        current_char
    ):
        return False
    if previous_char in _ROMANIZED_OPENING_PUNCTUATION:
        return False
    return current_char not in _ROMANIZED_CLOSING_PUNCTUATION
