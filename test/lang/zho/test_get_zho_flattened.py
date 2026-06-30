#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_flattened."""

from __future__ import annotations

from pytest import FixtureRequest, fail, param

from scinoephile.lang.zho.flattening import get_zho_flattened
from test.helpers import assert_series_equal, parametrize


@parametrize(
    ("series_fixture", "expected_fixture"),
    [
        param(
            "acopopb_zho_hans_ocr_fuse_clean_validate_review",
            "acopopb_zho_hans_ocr_fuse_clean_validate_review_flatten",
            id="acopopb-zho-hans",
        ),
        param(
            "acopopb_zho_hant_ocr_fuse_clean_validate_review",
            "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten",
            id="acopopb-zho-hant",
        ),
        param(
            "acoptc_zho_hans_ocr_fuse_clean_validate_review",
            "acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten",
            id="acoptc-zho-hans",
        ),
        param(
            "acoptc_zho_hant_ocr_fuse_clean_validate_review",
            "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten",
            id="acoptc-zho-hant",
        ),
        param(
            "kob_zho_hant_ocr_fuse_clean_validate_review",
            "kob_zho_hant_ocr_fuse_clean_validate_review_flatten",
            id="kob-zho-hant",
        ),
        param(
            "kob_yue_hans_clean_review",
            "kob_yue_hans_clean_review_flatten",
            id="kob-yue-hans-srt",
        ),
        param(
            "kob_yue_hant_clean_review",
            "kob_yue_hant_clean_review_flatten",
            id="kob-yue-hant-srt",
        ),
        param(
            "mlamd_zho_hans_fuse_clean_validate_review",
            "mlamd_zho_hans_fuse_clean_validate_review_flatten",
            id="mlamd-zho-hans",
        ),
        param(
            "mlamd_zho_hant_fuse_clean_validate_review",
            "mlamd_zho_hant_fuse_clean_validate_review_flatten",
            id="mlamd-zho-hant",
        ),
        param(
            "mnt_zho_hans_fuse_clean_validate_review",
            "mnt_zho_hans_fuse_clean_validate_review_flatten",
            id="mnt-zho-hans",
        ),
        param(
            "mnt_zho_hant_fuse_clean_validate_review",
            "mnt_zho_hant_fuse_clean_validate_review_flatten",
            id="mnt-zho-hant",
        ),
        param(
            "t_zho_hans_fuse_clean_validate_review",
            "t_zho_hans_fuse_clean_validate_review_flatten",
            id="t-zho-hans",
        ),
        param(
            "t_zho_hant_fuse_clean_validate_review",
            "t_zho_hant_fuse_clean_validate_review_flatten",
            id="t-zho-hant",
        ),
        param(
            "tmm_zho_hans_ocr_fuse_clean_validate_review",
            "tmm_zho_hans_ocr_fuse_clean_validate_review_flatten",
            id="tmm-zho-hans",
        ),
        param(
            "tmm_zho_hant_ocr_fuse_clean_validate_review",
            "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten",
            id="tmm-zho-hant",
        ),
    ],
)
def test_get_zho_flattened(
    request: FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
):
    """Test get_zho_flattened against expected flattened outputs.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: fixture name for input series
        expected_fixture: fixture name for expected output series
    """
    series = request.getfixturevalue(series_fixture)
    output = get_zho_flattened(series)
    assert len(series) == len(output)

    errors = []
    for i, event in enumerate(output, 1):
        if event.text.count("\n") != 0:
            errors.append(f"Subtitle {i} contains newline")

    if errors:
        for error in errors:
            print(error)
        fail(f"Found {len(errors)} discrepancies")
    assert_series_equal(output, request.getfixturevalue(expected_fixture))
