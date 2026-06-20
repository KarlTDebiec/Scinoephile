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
        pytest.param(
            "acopopb_zho_hans_ocr_fuse",
            "acopopb_zho_hans_ocr_fuse_clean",
            id="acopopb-zho-hans-fuse",
        ),
        pytest.param(
            "acopopb_zho_hans_ocr_lens",
            "acopopb_zho_hans_ocr_lens_clean",
            id="acopopb-zho-hans-lens",
        ),
        pytest.param(
            "acopopb_zho_hans_ocr_paddle",
            "acopopb_zho_hans_ocr_paddle_clean",
            id="acopopb-zho-hans-paddle",
        ),
        pytest.param(
            "acopopb_zho_hant_ocr_fuse",
            "acopopb_zho_hant_ocr_fuse_clean",
            id="acopopb-zho-hant-fuse",
        ),
        pytest.param(
            "acopopb_zho_hant_ocr_lens",
            "acopopb_zho_hant_ocr_lens_clean",
            id="acopopb-zho-hant-lens",
        ),
        pytest.param(
            "acopopb_zho_hant_ocr_paddle",
            "acopopb_zho_hant_ocr_paddle_clean",
            id="acopopb-zho-hant-paddle",
        ),
        pytest.param(
            "acoptc_zho_hans_ocr_fuse",
            "acoptc_zho_hans_ocr_fuse_clean",
            id="acoptc-zho-hans-fuse",
        ),
        pytest.param(
            "acoptc_zho_hans_ocr_lens",
            "acoptc_zho_hans_ocr_lens_clean",
            id="acoptc-zho-hans-lens",
        ),
        pytest.param(
            "acoptc_zho_hans_ocr_paddle",
            "acoptc_zho_hans_ocr_paddle_clean",
            id="acoptc-zho-hans-paddle",
        ),
        pytest.param(
            "acoptc_zho_hant_ocr_fuse",
            "acoptc_zho_hant_ocr_fuse_clean",
            id="acoptc-zho-hant-fuse",
        ),
        pytest.param(
            "acoptc_zho_hant_ocr_lens",
            "acoptc_zho_hant_ocr_lens_clean",
            id="acoptc-zho-hant-lens",
        ),
        pytest.param(
            "acoptc_zho_hant_ocr_paddle",
            "acoptc_zho_hant_ocr_paddle_clean",
            id="acoptc-zho-hant-paddle",
        ),
        pytest.param(
            "kob_zho_hant_ocr_fuse",
            "kob_zho_hant_ocr_fuse_clean",
            id="kob-zho-hant-fuse",
        ),
        pytest.param(
            "kob_zho_hant_ocr_lens",
            "kob_zho_hant_ocr_lens_clean",
            id="kob-zho-hant-lens",
        ),
        pytest.param(
            "kob_zho_hant_ocr_paddle",
            "kob_zho_hant_ocr_paddle_clean",
            id="kob-zho-hant-paddle",
        ),
        pytest.param(
            "mlamd_zho_hans_fuse",
            "mlamd_zho_hans_fuse_clean",
            id="mlamd-zho-hans-fuse",
        ),
        pytest.param(
            "mlamd_zho_hans_ocr_lens",
            "mlamd_zho_hans_ocr_lens_clean",
            id="mlamd-zho-hans-lens",
        ),
        pytest.param(
            "mlamd_zho_hans_ocr_paddle",
            "mlamd_zho_hans_ocr_paddle_clean",
            id="mlamd-zho-hans-paddle",
        ),
        pytest.param(
            "mlamd_zho_hant_fuse",
            "mlamd_zho_hant_fuse_clean",
            id="mlamd-zho-hant-fuse",
        ),
        pytest.param(
            "mlamd_zho_hant_ocr_lens",
            "mlamd_zho_hant_ocr_lens_clean",
            id="mlamd-zho-hant-lens",
        ),
        pytest.param(
            "mlamd_zho_hant_ocr_paddle",
            "mlamd_zho_hant_ocr_paddle_clean",
            id="mlamd-zho-hant-paddle",
        ),
        pytest.param(
            "mnt_zho_hans_fuse",
            "mnt_zho_hans_fuse_clean",
            id="mnt-zho-hans-fuse",
        ),
        pytest.param(
            "mnt_zho_hans_ocr_lens",
            "mnt_zho_hans_ocr_lens_clean",
            id="mnt-zho-hans-lens",
        ),
        pytest.param(
            "mnt_zho_hans_ocr_paddle",
            "mnt_zho_hans_ocr_paddle_clean",
            id="mnt-zho-hans-paddle",
        ),
        pytest.param(
            "mnt_zho_hant_fuse",
            "mnt_zho_hant_fuse_clean",
            id="mnt-zho-hant-fuse",
        ),
        pytest.param(
            "mnt_zho_hant_ocr_lens",
            "mnt_zho_hant_ocr_lens_clean",
            id="mnt-zho-hant-lens",
        ),
        pytest.param(
            "mnt_zho_hant_ocr_paddle",
            "mnt_zho_hant_ocr_paddle_clean",
            id="mnt-zho-hant-paddle",
        ),
        pytest.param(
            "t_zho_hans_fuse",
            "t_zho_hans_fuse_clean",
            id="t-zho-hans-fuse",
        ),
        pytest.param(
            "t_zho_hans_ocr_lens",
            "t_zho_hans_ocr_lens_clean",
            id="t-zho-hans-lens",
        ),
        pytest.param(
            "t_zho_hans_ocr_paddle",
            "t_zho_hans_ocr_paddle_clean",
            id="t-zho-hans-paddle",
        ),
        pytest.param(
            "t_zho_hant_fuse",
            "t_zho_hant_fuse_clean",
            id="t-zho-hant-fuse",
        ),
        pytest.param(
            "t_zho_hant_ocr_lens",
            "t_zho_hant_ocr_lens_clean",
            id="t-zho-hant-lens",
        ),
        pytest.param(
            "t_zho_hant_ocr_paddle",
            "t_zho_hant_ocr_paddle_clean",
            id="t-zho-hant-paddle",
        ),
        pytest.param(
            "tmm_zho_hans_ocr_fuse",
            "tmm_zho_hans_ocr_fuse_clean",
            id="tmm-zho-hans-fuse",
        ),
        pytest.param(
            "tmm_zho_hans_ocr_lens",
            "tmm_zho_hans_ocr_lens_clean",
            id="tmm-zho-hans-lens",
        ),
        pytest.param(
            "tmm_zho_hans_ocr_paddle",
            "tmm_zho_hans_ocr_paddle_clean",
            id="tmm-zho-hans-paddle",
        ),
        pytest.param(
            "tmm_zho_hant_ocr_fuse",
            "tmm_zho_hant_ocr_fuse_clean",
            id="tmm-zho-hant-fuse",
        ),
        pytest.param(
            "tmm_zho_hant_ocr_lens",
            "tmm_zho_hant_ocr_lens_clean",
            id="tmm-zho-hant-lens",
        ),
        pytest.param(
            "tmm_zho_hant_ocr_paddle",
            "tmm_zho_hant_ocr_paddle_clean",
            id="tmm-zho-hant-paddle",
        ),
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
