#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.cmn.get_cmn_romanized."""

from __future__ import annotations

from pytest import FixtureRequest, mark, param

from scinoephile.lang.cmn.romanization import get_cmn_romanized, get_cmn_text_romanized
from test.helpers import assert_series_equal


@mark.parametrize(
    ("series_fixture", "expected_fixture"),
    [
        param(
            "acopopb_zho_hans_ocr_fuse_clean_validate_review_flatten",
            "acopopb_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize",
            id="acopopb-zho-hans",
        ),
        param(
            "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
            id="acopopb-zho-hant-simplify-review",
        ),
        param(
            "acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten",
            "acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize",
            id="acoptc-zho-hans",
        ),
        param(
            "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
            id="acoptc-zho-hant-simplify-review",
        ),
        param(
            "kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
            id="kob-zho-hant-simplify-review",
        ),
        param(
            "mlamd_zho_hans_fuse_clean_validate_review_flatten",
            "mlamd_zho_hans_fuse_clean_validate_review_flatten_romanize",
            id="mlamd-zho-hans",
        ),
        param(
            "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review_romanize",
            id="mlamd-zho-hant-simplify-review",
        ),
        param(
            "mnt_zho_hans_fuse_clean_validate_review_flatten",
            "mnt_zho_hans_fuse_clean_validate_review_flatten_romanize",
            id="mnt-zho-hans",
        ),
        param(
            "mnt_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "mnt_zho_hant_fuse_clean_validate_review_flatten_simplify_review_romanize",
            id="mnt-zho-hant-simplify-review",
        ),
        param(
            "t_zho_hans_fuse_clean_validate_review_flatten",
            "t_zho_hans_fuse_clean_validate_review_flatten_romanize",
            id="t-zho-hans",
        ),
        param(
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify_review_romanize",
            id="t-zho-hant-simplify-review",
        ),
        param(
            "tmm_zho_hans_ocr_fuse_clean_validate_review_flatten",
            "tmm_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize",
            id="tmm-zho-hans",
        ),
        param(
            "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
            id="tmm-zho-hant-simplify-review",
        ),
    ],
)
def test_get_cmn_romanized(
    request: FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
):
    """Test get_cmn_romanized against expected romanized outputs.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: Fixture name for input series
        expected_fixture: Fixture name for expected output series
    """
    output = get_cmn_romanized(
        request.getfixturevalue(series_fixture),
        append=True,
    )
    assert_series_equal(output, request.getfixturevalue(expected_fixture))


@mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "nǐhǎo shìjiè"),
        ("你好,世界!", "nǐhǎo, shìjiè!"),
        ("「你好」世界？", "「nǐhǎo」 shìjiè?"),
        ("＂你好＂世界", '"nǐhǎo" shìjiè'),
        ("＇你好＇世界", "'nǐhǎo' shìjiè"),
        ("你好：世界；再见。", "nǐhǎo: shìjiè; zàijiàn."),
        ("don't你好", "don't nǐhǎo"),
        ('"t i"你好', '"t  i" nǐhǎo'),
    ],
)
def test_get_mandarin_text_romanization(text: str, expected: str):
    """Test get_cmn_text_romanized.

    Arguments:
        text: Text to romanize
        expected: Expected romanization
    """
    assert get_cmn_text_romanized(text) == expected
