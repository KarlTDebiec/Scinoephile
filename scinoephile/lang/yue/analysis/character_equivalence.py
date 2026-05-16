#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Character equivalence helpers for written Cantonese analysis."""

from __future__ import annotations

from scinoephile.analysis.diff import SeriesDiff

__all__ = [
    "YUE_DIFF_CHAR_EQUIVALENCES",
    "YUE_DIFF_IGNORABLE_CHARS",
    "are_yue_diff_chars_equal",
    "are_yue_diff_display_chars_equal",
    "get_yue_diff_normalized",
    "is_yue_diff_display_ignorable_char",
    "is_yue_diff_ignorable_char",
]

YUE_DIFF_CHAR_EQUIVALENCES: frozenset[frozenset[str]] = frozenset(
    {
        frozenset(("啦", "喇")),
        frozenset(("哋", "地")),
        frozenset(("吓", "下")),
    }
)
"""Explicit Cantonese character equivalences used for flexible analysis."""

YUE_DIFF_IGNORABLE_CHARS: frozenset[str] = frozenset("　 \t，。！？、；：,.!?")
"""Common subtitle punctuation and spacing ignored by flexible analysis."""

_YUE_DIFF_CHAR_NORMALIZATION: dict[str, str] = {
    "喇": "啦",
    "地": "哋",
    "下": "吓",
}
_YUE_DIFF_SPACING_PARTICLES: frozenset[str] = frozenset(("阿", "呀"))


def are_yue_diff_chars_equal(one: str, two: str) -> bool:
    """Check whether two characters are equivalent for Cantonese analysis.

    Arguments:
        one: first character
        two: second character
    Returns:
        whether the two characters should compare as equal
    """
    if one == two:
        return True
    return frozenset((one, two)) in YUE_DIFF_CHAR_EQUIVALENCES


def are_yue_diff_display_chars_equal(
    one: str,
    two: str,
    *,
    one_text: str,
    two_text: str,
    one_pos: int,
    two_pos: int,
) -> bool:
    """Check whether a visible character difference is ignored in Yue analysis.

    Arguments:
        one: first character
        two: second character
        one_text: first text containing the character
        two_text: second text containing the character
        one_pos: position of the first character
        two_pos: position of the second character
    Returns:
        whether the visible difference is ignored
    """
    if are_yue_diff_chars_equal(one, two):
        return True
    if is_yue_diff_ignorable_char(one) and is_yue_diff_ignorable_char(two):
        return True
    if _are_yue_diff_spacing_particle_chars_equal(one, two):
        return True
    if frozenset((one, two)) == frozenset(("啦", "啰")):
        return _is_yue_diff_sentence_final_char(
            one_text,
            one_pos,
        ) and _is_yue_diff_sentence_final_char(
            two_text,
            two_pos,
        )
    return False


def get_yue_diff_normalized(text: str) -> str:
    """Normalize text for Cantonese-flexible analysis.

    Arguments:
        text: text to normalize
    Returns:
        normalized text for diffing or CER alignment
    """
    text = SeriesDiff._normalize_line(text)
    chars = []
    for idx, char in enumerate(text):
        if is_yue_diff_ignorable_char(char):
            continue
        if char in _YUE_DIFF_SPACING_PARTICLES:
            continue
        if char == "啰" and _is_yue_diff_sentence_final_char(text, idx):
            chars.append("啦")
        else:
            chars.append(_YUE_DIFF_CHAR_NORMALIZATION.get(char, char))
    return "".join(chars)


def is_yue_diff_display_ignorable_char(char: str) -> bool:
    """Check whether a one-sided visible character is ignored in Yue analysis.

    Arguments:
        char: character to check
    Returns:
        whether the character is ignored for display
    """
    if is_yue_diff_ignorable_char(char):
        return True
    return char in _YUE_DIFF_SPACING_PARTICLES


def is_yue_diff_ignorable_char(char: str) -> bool:
    """Check whether a character may be ignored by Cantonese analysis.

    Arguments:
        char: character to check
    Returns:
        whether the character is ignorable
    """
    if len(char) != 1:
        return False
    if char in YUE_DIFF_IGNORABLE_CHARS:
        return True
    return _is_yue_diff_non_newline_whitespace(char)


def _are_yue_diff_spacing_particle_chars_equal(one: str, two: str) -> bool:
    """Check whether a spacing particle is interchangeable with whitespace.

    Arguments:
        one: first character
        two: second character
    Returns:
        whether the characters are a spacing particle and whitespace
    """
    if one in _YUE_DIFF_SPACING_PARTICLES:
        return _is_yue_diff_non_newline_whitespace(two)
    if two in _YUE_DIFF_SPACING_PARTICLES:
        return _is_yue_diff_non_newline_whitespace(one)
    return False


def _is_yue_diff_non_newline_whitespace(char: str) -> bool:
    """Check whether a character is whitespace other than a newline.

    Arguments:
        char: character to check
    Returns:
        whether the character is non-newline whitespace
    """
    return len(char) == 1 and char.isspace() and char not in {"\n", "\r"}


def _is_yue_diff_sentence_final_char(text: str, char_pos: int) -> bool:
    """Check whether a character is final apart from ignorable suffixes.

    Arguments:
        text: text containing the character
        char_pos: character position to check
    Returns:
        whether the character is final in its subtitle line
    """
    for char in text[char_pos + 1 :]:
        if not is_yue_diff_ignorable_char(char):
            return False
    return True
