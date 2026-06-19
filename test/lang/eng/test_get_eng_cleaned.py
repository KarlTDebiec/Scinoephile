#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.eng.get_eng_cleaned."""

from __future__ import annotations

import pytest

from scinoephile.lang.eng.cleaning import get_eng_cleaned, get_eng_text_cleaned
from test.helpers import assert_series_equal


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("hello\\N-\\Nworld", "hello\\Nworld"),
        (
            '<font face="Monospace">{\\an7}WOODY:\xa0Look out!</font>',
            "WOODY: Look out!",
        ),
        (
            "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ "
            "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ "
            "０１２３４５６７８９",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789",
        ),
        ("ΟΚ, οκ.", "OK, ok."),
    ],
)
def test_get_eng_text_cleaned(
    text: str,
    expected: str,
):
    """Test get_eng_text_cleaned.

    Arguments:
        text: text to clean
        expected: expected cleaned text
    """
    assert get_eng_text_cleaned(text) == expected


@pytest.mark.parametrize(
    ("series_fixture", "expected_fixture"),
    [
        pytest.param(
            "kob_eng_ocr_fuse",
            "kob_eng_ocr_fuse_clean",
            id="kob-eng-fuse",
        ),
        pytest.param(
            "mlamd_eng_fuse",
            "mlamd_eng_fuse_clean",
            id="mlamd-eng-fuse",
        ),
        pytest.param(
            "mnt_eng_fuse",
            "mnt_eng_fuse_clean",
            id="mnt-eng-fuse",
        ),
        pytest.param(
            "t_eng_fuse",
            "t_eng_fuse_clean",
            id="t-eng-fuse",
        ),
        pytest.param(
            "t_eng_ocr_lens",
            "t_eng_ocr_lens_clean",
            id="t-eng-lens",
        ),
        pytest.param(
            "t_eng_ocr_tesseract",
            "t_eng_ocr_tesseract_clean",
            id="t-eng-tesseract",
        ),
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
