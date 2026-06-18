#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_cleaned."""

from __future__ import annotations

import pytest

from scinoephile.lang.zho.cleaning import _get_zho_text_cleaned, get_zho_cleaned
from test.helpers import assert_series_equal


def test_get_zho_text_cleaned_removes_subtitle_markup():
    """Test subtitle extraction markup is removed from standard Chinese text."""
    text = '<font face="Monospace">{\\an7}中文\xa0測試</font>'

    assert _get_zho_text_cleaned(text) == "中文 測試"


def test_get_zho_text_cleaned_normalizes_fullwidth_alphanumerics():
    """Test fullwidth letters and digits are normalized in Chinese text."""
    fullwidth_text = "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
    fullwidth_text = f"{fullwidth_text} ａｂｃｄｅｆｇｈｉｊｋｌｍ"
    fullwidth_text = f"{fullwidth_text}ｎｏｐｑｒｓｔｕｖｗｘｙｚ ０１２３４５６７８９"

    assert _get_zho_text_cleaned(fullwidth_text) == (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789"
    )


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
