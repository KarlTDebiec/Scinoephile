#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for core text helpers."""

from __future__ import annotations

from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.core.text import (
    RE_LATIN_WORD,
    get_char_type,
    is_lexical_character,
    is_low_information_text,
    join_text_lines,
    normalize_nfkc,
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
    """Fullwidth Latin forms are classified as full-width characters.

    Arguments:
        char: char value
    """
    assert get_char_type(char) == "full"


@parametrize("char", ["で", "ア"])
def test_get_char_type_handles_japanese_wide_characters(char: str) -> None:
    """Japanese wide characters are classified as full-width characters.

    Arguments:
        char: char value
    """
    assert get_char_type(char) == "full"


@parametrize("char", ["A", "é", "Ω", "Ж", "ع", "ｱ"])
def test_get_char_type_handles_half_width_characters(char: str) -> None:
    """Printable non-wide characters are classified as half-width characters.

    Arguments:
        char: char value
    """
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
    """Text lines are joined according to adjacent characters' display width.

    Arguments:
        texts: texts
        expected: expected value
    """
    assert join_text_lines(texts) == expected


@parametrize(
    ("character", "expected"),
    [
        ("甲", True),
        ("Ａ", True),
        ("1", True),
        ("。", False),
        ("・", False),
        (" ", False),
    ],
)
def test_is_lexical_character(character: str, expected: bool) -> None:
    """Lexical characters exclude punctuation, symbols, and separators.

    Arguments:
        character: character value
        expected: expected value
    """
    assert is_lexical_character(character) is expected


@parametrize(
    ("text", "expected"),
    [
        ("哎　哎哎啊啊啊嗯", True),
        ("ＡＡＡＨ！", True),
        ("哈哈嗯", True),
        ("", False),
        ("・・　", False),
        ("哎呀次子", False),
        ("Hi", False),
    ],
)
def test_is_low_information_text(text: str, expected: bool) -> None:
    """Low-information text includes common Chinese and Latin vocalizations.

    Arguments:
        text: text to classify
        expected: expected classification
    """
    assert is_low_information_text(text) is expected


@parametrize(("text", "expected"), [("Ａ①", "A1"), ("㍿", "株式会社")])
def test_normalize_nfkc(text: str, expected: str) -> None:
    """NFKC normalization applies Unicode compatibility composition.

    Arguments:
        text: text
        expected: expected value
    """
    assert normalize_nfkc(text) == expected


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
    """Text normalization applies shared mechanical cleanup.

    Arguments:
        text: text
        expected: expected value
    """
    assert normalize_text(text) == expected


@parametrize(("text", "expected"), [("Don't stop 佢", ["Don't", "stop"])])
def test_re_latin_word(text: str, expected: list[str]) -> None:
    """Latin word regex matches word-like tokens.

    Arguments:
        text: text
        expected: expected value
    """
    assert RE_LATIN_WORD.findall(text) == expected


@parametrize(("text", "expected"), [("one\ntwo\tthree\r", "one\ntwo\tthree\r")])
def test_replace_control_characters_preserves_text_whitespace(
    text: str, expected: str
) -> None:
    """Line and tab whitespace are preserved.

    Arguments:
        text: text
        expected: expected value
    """
    assert replace_control_characters(text) == expected
