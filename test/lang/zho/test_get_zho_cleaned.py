#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_cleaned."""

from __future__ import annotations

import pytest

from scinoephile.lang.zho.cleaning import get_zho_cleaned, get_zho_text_cleaned
from test.helpers import assert_series_equal


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ('<font face="Monospace">{\\an7}中文\xa0測試</font>', "中文 測試"),
        (
            "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ "
            "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ "
            "０１２３４５６７８９",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789",
        ),
    ],
)
def test_get_zho_text_cleaned(text: str, expected: str):
    """Test get_zho_text_cleaned.

    Arguments:
        text: text to clean
        expected: expected cleaned text
    """
    assert get_zho_text_cleaned(text) == expected


@pytest.mark.parametrize(
    ("series_fixture", "expected_fixture"),
    [
        ("kob_zho_hant_ocr_fuse", "kob_zho_hant_ocr_fuse_clean"),
        ("mlamd_zho_hans_fuse", "mlamd_zho_hans_fuse_clean"),
        ("mnt_zho_hans_fuse", "mnt_zho_hans_fuse_clean"),
        ("t_zho_hans_fuse", "t_zho_hans_fuse_clean"),
        ("t_zho_hans_ocr_paddle", "t_zho_hans_ocr_paddle_clean"),
        ("t_zho_hant_fuse", "t_zho_hant_fuse_clean"),
        ("t_zho_hant_ocr_paddle", "t_zho_hant_ocr_paddle_clean"),
    ],
)
def test_get_zho_cleaned(
    request: pytest.FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
):
    """Test get_zho_cleaned against expected cleaned outputs.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: fixture name for input series
        expected_fixture: fixture name for expected output series
    """
    output = get_zho_cleaned(
        request.getfixturevalue(series_fixture),
        remove_empty=False,
    )
    assert_series_equal(output, request.getfixturevalue(expected_fixture))
