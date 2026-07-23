#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for core text helpers."""

from __future__ import annotations

from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.core.text import (
    RE_LATIN_WORD,
    get_char_type,
    join_text_lines,
    normalize_text,
    replace_control_characters,
)
from test.helpers import parametrize


def test_get_char_type_handles_unnamed_control_char() -> None:
    """Unnamed control characters raise a ScinoephileError."""
    with raises(ScinoephileError, match="<unnamed>"):
        get_char_type("\x00")


def test_get_char_type_rejects_combining_character() -> None:
    """Combining characters cannot be represented by the two-width model."""
    with raises(ScinoephileError, match="COMBINING ACUTE ACCENT"):
        get_char_type("\u0301")


@parametrize("char", ["Ｋ", "Ａ", "１", "ｋ"])
def test_get_char_type_handles_fullwidth_latin_forms(char: str) -> None:
    """Fullwidth Latin forms are classified as full-width characters."""
    assert get_char_type(char) == "full"


@parametrize("char", ["で", "ア"])
def test_get_char_type_handles_japanese_wide_characters(char: str) -> None:
    """Japanese wide characters are classified as full-width characters."""
    assert get_char_type(char) == "full"


@parametrize("char", ["A", "é", "Ω", "Ж", "ع", "ｱ"])
def test_get_char_type_handles_half_width_characters(char: str) -> None:
    """Printable non-wide characters are classified as half-width characters."""
    assert get_char_type(char) == "half"


@parametrize(
    ("texts", "expected"),
    [
        ((), ""),
        (("one", "two"), "one two"),
        (("甲", "乙"), "甲　乙"),
        (("one", "乙"), "one　乙"),
        (("甲", "two"), "甲　two"),
    ],
)
def test_join_text_lines(texts: tuple[str, ...], expected: str) -> None:
    """Text lines are joined according to adjacent characters' display width."""
    assert join_text_lines(texts) == expected


@parametrize(
    ("text", "expected"),
    [
        ("ＫＡＴＥ ｋａｔｅ １２３", "KATE kate 123"),
        ("ΟΚ, οκ.", "OK, ok."),
        (" \xa0ＫＡＴＥ\x00ΟΚ ", "KATE OK"),
        ("好呀！\x00\x00你", "好呀！  你"),
    ],
)
def test_normalize_text(text: str, expected: str) -> None:
    """Text normalization applies shared mechanical cleanup."""
    assert normalize_text(text) == expected


@parametrize(
    ("text", "expected"),
    [
        ("Don't stop 佢", ["Don't", "stop"]),
    ],
)
def test_re_latin_word(text: str, expected: list[str]) -> None:
    """Latin word regex matches word-like tokens."""
    assert RE_LATIN_WORD.findall(text) == expected


@parametrize(
    ("text", "expected"),
    [
        ("one\ntwo\tthree\r", "one\ntwo\tthree\r"),
    ],
)
def test_replace_control_characters_preserves_text_whitespace(
    text: str, expected: str
) -> None:
    """Line and tab whitespace are preserved."""
    assert replace_control_characters(text) == expected
