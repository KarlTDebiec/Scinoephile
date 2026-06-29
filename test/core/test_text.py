#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for core text helpers."""

from __future__ import annotations

from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.core.text import (
    FULL_TO_HALF_PUNC,
    HALF_TO_FULL_PUNC,
    get_char_type,
    normalize_fullwidth_alphanumerics,
    normalize_ocr_confusables_to_ascii,
    sanitize_text,
)
from test.helpers import parametrize


def test_get_char_type_handles_unnamed_control_char() -> None:
    """Unnamed control characters raise a ScinoephileError."""
    with raises(ScinoephileError, match="<unnamed>"):
        get_char_type("\x00")


@parametrize("char", ["Ｋ", "Ａ", "１", "ｋ"])
def test_get_char_type_handles_fullwidth_latin_forms(char: str) -> None:
    """Fullwidth Latin forms are classified as full-width characters."""
    assert get_char_type(char) == "full"


@parametrize(
    ("half_punc", "full_punc"),
    [
        ("､", "、"),
        ("｡", "。"),
        ("･", "・"),
        ("｢", "「"),
        ("｣", "」"),
        ("·", "・"),
    ],
)
def test_half_to_full_punc_includes_cjk_aliases(
    half_punc: str,
    full_punc: str,
) -> None:
    """CJK punctuation aliases are mapped to full-width forms."""
    assert HALF_TO_FULL_PUNC[half_punc] == full_punc


@parametrize(
    ("full_punc", "half_punc"),
    [
        ("＜", "<"),
        ("＞", ">"),
        ("、", "､"),
        ("。", "｡"),
        ("・", "･"),
        ("「", "｢"),
        ("」", "｣"),
        ("⋯", "…"),
    ],
)
def test_full_to_half_punc_includes_cjk_aliases(
    full_punc: str,
    half_punc: str,
) -> None:
    """CJK punctuation aliases are mapped to half-width forms."""
    assert FULL_TO_HALF_PUNC[full_punc] == half_punc


@parametrize(
    ("text", "expected"),
    [
        ("ＫＡＴＥ ｋａｔｅ １２３", "KATE kate 123"),
    ],
)
def test_normalize_fullwidth_alphanumerics(text: str, expected: str) -> None:
    """Fullwidth letters and digits are converted to regular ASCII."""
    assert normalize_fullwidth_alphanumerics(text) == expected


@parametrize(
    ("text", "expected"),
    [
        ("ΟΚ, οκ.", "OK, ok."),
    ],
)
def test_normalize_ocr_confusables_to_ascii(text: str, expected: str) -> None:
    """OCR-confusable characters are converted to regular ASCII."""
    assert normalize_ocr_confusables_to_ascii(text) == expected


@parametrize(
    ("text", "expected"),
    [
        ("好呀！\x00\x00你", "好呀！  你"),
    ],
)
def test_sanitize_text_replaces_control_chars(text: str, expected: str) -> None:
    """Control characters that are not text whitespace are replaced."""
    assert sanitize_text(text) == expected


@parametrize(
    ("text", "expected"),
    [
        ("one\ntwo\tthree\r", "one\ntwo\tthree\r"),
    ],
)
def test_sanitize_text_preserves_text_whitespace(text: str, expected: str) -> None:
    """Line and tab whitespace are preserved."""
    assert sanitize_text(text) == expected
