#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.eng.get_eng_cleaned."""

from __future__ import annotations

import pytest

from scinoephile.lang.eng.cleaning import _get_english_text_cleaned, get_eng_cleaned
from test.helpers import assert_series_equal

# noinspection PyProtectedMember


def test_get_english_text_cleaned_removes_ass_dash_only_line():
    """Test ASS multiline dash-only line removal."""
    assert _get_english_text_cleaned("hello\\N-\\Nworld") == "hello\\Nworld"


def test_get_english_text_cleaned_removes_eia_608_markup():
    """Test EIA-608 extraction markup is removed from English text."""
    text = '<font face="Monospace">{\\an7}WOODY:\xa0Look out!</font>'

    assert _get_english_text_cleaned(text) == "WOODY: Look out!"


def test_get_english_text_cleaned_normalizes_fullwidth_alphanumerics():
    """Test fullwidth letters and digits are normalized in English text."""
    fullwidth_text = "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
    fullwidth_text = f"{fullwidth_text} ａｂｃｄｅｆｇｈｉｊｋｌｍ"
    fullwidth_text = f"{fullwidth_text}ｎｏｐｑｒｓｔｕｖｗｘｙｚ ０１２３４５６７８９"

    assert _get_english_text_cleaned(fullwidth_text) == (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789"
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ΟΚ, οκ.", "OK, ok."),
    ],
)
def test_get_english_text_cleaned_normalizes_greek_ocr_confusables(
    text: str,
    expected: str,
):
    """Test Greek OCR confusables are normalized in English text.

    Arguments:
        text: text to clean
        expected: expected cleaned text
    """
    assert _get_english_text_cleaned(text) == expected


@pytest.mark.parametrize(
    ("series_fixture", "expected_fixture"),
    [
        ("kob_eng_ocr_fuse", "kob_eng_ocr_fuse_clean"),
        ("mlamd_eng_fuse", "mlamd_eng_fuse_clean"),
        ("mnt_eng_fuse", "mnt_eng_fuse_clean"),
        ("t_eng_fuse", "t_eng_fuse_clean"),
        ("t_eng_ocr_lens", "t_eng_ocr_lens_clean"),
        ("t_eng_ocr_tesseract", "t_eng_ocr_tesseract_clean"),
    ],
)
def test_get_eng_cleaned(
    request: pytest.FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
):
    """Test get_eng_cleaned against expected cleaned outputs.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: fixture name for input series
        expected_fixture: fixture name for expected output series
    """
    output = get_eng_cleaned(
        request.getfixturevalue(series_fixture),
        remove_empty=False,
    )
    assert_series_equal(output, request.getfixturevalue(expected_fixture))
