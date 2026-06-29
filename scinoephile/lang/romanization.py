#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared helpers for romanized text formatting."""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable
from typing import Literal

from scinoephile.core.text import FULL_PUNC_CHARS, FULL_TO_HALF_PUNC, HALF_PUNC_CHARS

__all__ = [
    "RomanizedTokenKind",
    "is_romanized_punctuation",
    "join_romanized_tokens",
    "normalize_romanized_punctuation",
]

type RomanizedTokenKind = Literal["punctuation", "raw", "romanized"]
"""Kind of token being joined into romanized text."""

_ROMANIZED_CLOSING_PUNCTUATION = set(")]}>.,!?;:%”’」』》〉】＞…")
_ROMANIZED_OPENING_PUNCTUATION = set("([{<“‘「『《〈【＜")
_ROMANIZED_PUNCTUATION = {
    **FULL_TO_HALF_PUNC,
    "＜": "＜",
    "＞": "＞",
    "、": ",",
    "。": ".",
    "⋯": "…",
}
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
    open_symmetric_quotes: set[str] | None = None,
    token_kinds: Iterable[RomanizedTokenKind] | None = None,
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
    unfiltered_tokens = list(tokens)
    if open_symmetric_quotes is None:
        open_symmetric_quotes = set()
    if token_kinds is None:
        tokens = [token for token in unfiltered_tokens if token]
        token_kind_list = None
    else:
        token_kind_list = []
        tokens = []
        for token, token_kind in zip(unfiltered_tokens, token_kinds, strict=True):
            if token:
                tokens.append(token)
                token_kind_list.append(token_kind)
    quote_roles = _get_symmetric_quote_roles(
        tokens, open_symmetric_quotes, token_kind_list
    )
    output = ""
    previous_quote_role: Literal["closing", "infix", "opening"] | None = None
    for token, quote_role in zip(tokens, quote_roles, strict=True):
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
    return "".join(_ROMANIZED_PUNCTUATION.get(char, char) for char in text)


def _get_symmetric_quote_roles(
    tokens: list[str],
    open_quotes: set[str],
    token_kinds: list[RomanizedTokenKind] | None,
) -> list[Literal["closing", "infix", "opening"] | None]:
    """Get spacing roles for straight quote tokens.

    Arguments:
        tokens: romanized text and punctuation tokens
        open_quotes: straight quotes open before these tokens
        token_kinds: source kinds for the tokens, when available
    Returns:
        spacing roles for straight quote tokens
    """
    roles: list[Literal["closing", "infix", "opening"] | None] = []
    for index, token in enumerate(tokens):
        if token not in _ROMANIZED_SYMMETRIC_QUOTES:
            roles.append(None)
            continue

        if index:
            previous_token = tokens[index - 1]
        else:
            previous_token = ""
        if index + 1 < len(tokens):
            next_token = tokens[index + 1]
        else:
            next_token = ""
        if token in open_quotes:
            roles.append("closing")
            open_quotes.remove(token)
        elif token == "'" and _is_infix_quote_context(
            index, previous_token, next_token, token_kinds
        ):
            roles.append("infix")
        elif _is_romanized_text_token(previous_token) and not next_token:
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
    previous_token: str,
    next_token: str,
    token_kinds: list[RomanizedTokenKind] | None,
) -> bool:
    """Check whether a single quote joins raw text tokens.

    Arguments:
        index: token index of the quote
        previous_token: preceding token
        next_token: following token
        token_kinds: source kinds for the tokens, when available
    Returns:
        whether the quote should be treated as infix punctuation
    """
    if token_kinds is not None:
        return (
            index > 0
            and index + 1 < len(token_kinds)
            and token_kinds[index - 1] == "raw"
            and token_kinds[index + 1] == "raw"
        )
    return _is_romanized_text_token(previous_token) and _is_romanized_text_token(
        next_token
    )


def _is_romanized_text_token(token: str) -> bool:
    """Check whether a token is romanized text.

    Arguments:
        token: token to check
    Returns:
        whether token is romanized text
    """
    return bool(token) and not is_romanized_punctuation(token)


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
