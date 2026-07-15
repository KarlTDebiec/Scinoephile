#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle series romanization."""

from __future__ import annotations

from pytest import FixtureRequest, param, raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.workflows.romanize import romanize
from test.helpers import assert_series_equal, parametrize
from test.helpers.series_files import get_text_series


@parametrize(
    ("series_fixture", "expected_fixture", "language"),
    [
        param(
            "acopopb_zho_hans_ocr_fuse_clean_validate_review_flatten",
            "acopopb_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize",
            Language.zho_hans,
            id="acopopb-zho-hans",
        ),
        param(
            "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
            Language.zho_hant,
            id="acopopb-zho-hant-simplify-review",
        ),
        param(
            "acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten",
            "acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize",
            Language.zho_hans,
            id="acoptc-zho-hans",
        ),
        param(
            "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
            Language.zho_hant,
            id="acoptc-zho-hant-simplify-review",
        ),
        param(
            "kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
            Language.zho_hant,
            id="kob-zho-hant-simplify-review",
        ),
        param(
            "mlamd_zho_hans_fuse_clean_validate_review_flatten",
            "mlamd_zho_hans_fuse_clean_validate_review_flatten_romanize",
            Language.zho_hans,
            id="mlamd-zho-hans",
        ),
        param(
            "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review_romanize",
            Language.zho_hant,
            id="mlamd-zho-hant-simplify-review",
        ),
        param(
            "mnt_zho_hans_fuse_clean_validate_review_flatten",
            "mnt_zho_hans_fuse_clean_validate_review_flatten_romanize",
            Language.zho_hans,
            id="mnt-zho-hans",
        ),
        param(
            "mnt_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "mnt_zho_hant_fuse_clean_validate_review_flatten_simplify_review_romanize",
            Language.zho_hant,
            id="mnt-zho-hant-simplify-review",
        ),
        param(
            "t_zho_hans_fuse_clean_validate_review_flatten",
            "t_zho_hans_fuse_clean_validate_review_flatten_romanize",
            Language.zho_hans,
            id="t-zho-hans",
        ),
        param(
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify_review_romanize",
            Language.zho_hant,
            id="t-zho-hant-simplify-review",
        ),
        param(
            "tmm_zho_hans_ocr_fuse_clean_validate_review_flatten",
            "tmm_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize",
            Language.zho_hans,
            id="tmm-zho-hans",
        ),
        param(
            "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
            Language.zho_hant,
            id="tmm-zho-hant-simplify-review",
        ),
        param(
            "acopopb_yue_hans_ocr_fuse_clean_validate_review_flatten",
            "acopopb_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize",
            Language.yue_hans,
            id="acopopb-yue-hans",
        ),
        param(
            "acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
            Language.yue_hant,
            id="acopopb-yue-hant",
        ),
        param(
            "acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten",
            "acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize",
            Language.yue_hans,
            id="acoptc-yue-hans",
        ),
        param(
            "acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
            Language.yue_hant,
            id="acoptc-yue-hant",
        ),
        param(
            "kob_yue_hans_clean_review_flatten_timewarp",
            "kob_yue_hans_clean_review_flatten_timewarp_romanize",
            Language.yue_hans,
            id="kob-yue-hans-srt",
        ),
        param(
            "kob_yue_hant_clean_review_flatten_timewarp_simplify_review",
            "kob_yue_hant_clean_review_flatten_timewarp_simplify_review_romanize",
            Language.yue_hant,
            id="kob-yue-hant-srt",
        ),
        param(
            "tmm_yue_hans_ocr_fuse_clean_validate_review_flatten",
            "tmm_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize",
            Language.yue_hans,
            id="tmm-yue-hans",
        ),
        param(
            "tmm_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "tmm_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
            Language.yue_hant,
            id="tmm-yue-hant",
        ),
    ],
)
def test_romanize_series(
    request: FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
    language: Language,
):
    """Test romanize against expected romanized outputs.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: fixture name for input series
        expected_fixture: fixture name for expected output series
        language: language whose romanization system to use
    """
    output = romanize(
        request.getfixturevalue(series_fixture),
        language=language,
        append=True,
    )
    assert_series_equal(output, request.getfixturevalue(expected_fixture))


def test_romanize_series_replaces_text():
    """Test romanize replaces source text when append is false."""
    source = get_text_series("你好")

    output = romanize(
        source,
        language=Language.zho_hans,
        append=False,
    )

    assert output.events[0].text == "nǐhǎo"
    assert source.events[0].text == "你好"


def test_romanize_series_rejects_unsupported_language():
    """Test romanize rejects unsupported languages."""
    with raises(
        ScinoephileError,
        match="Romanization does not support language eng",
    ):
        romanize(get_text_series("Hello"), language=Language.eng)
