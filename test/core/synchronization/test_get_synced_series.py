#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.synchronization.get_synced_series."""

from __future__ import annotations

from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import get_synced_series
from test.helpers import assert_series_equal


def _test_get_synced_series(one: Series, two: Series, expected: Series):
    """Test get_synced_series.

    Arguments:
        one: subtitles series one
        two: subtitles series two
        expected: expected output series
    """
    output = get_synced_series(one, two)
    assert_series_equal(output, expected)


def test_get_synced_series_kob(
    kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review: Series,
    kob_eng_ocr_fuse_clean_validate_review_flatten: Series,
    kob_zho_hans_eng: Series,
):
    """Test get_synced_series with KOB subtitles.

    Arguments:
        kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review:
          simplified standard Chinese subtitle fixture
        kob_eng_ocr_fuse_clean_validate_review_flatten: English subtitle fixture
        kob_zho_hans_eng: expected synced subtitles fixture
    """
    _test_get_synced_series(
        kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review,
        kob_eng_ocr_fuse_clean_validate_review_flatten,
        kob_zho_hans_eng,
    )


def test_get_synced_series_mlamd(
    mlamd_zho_hans_fuse_clean_validate_review_flatten: Series,
    mlamd_eng_fuse_clean_validate_review_flatten: Series,
    mlamd_zho_hans_eng: Series,
):
    """Test get_synced_series with MLAMD subtitles.

    Arguments:
        mlamd_zho_hans_fuse_clean_validate_review_flatten: simplified standard
          Chinese subtitle fixture
        mlamd_eng_fuse_clean_validate_review_flatten: English subtitle fixture
        mlamd_zho_hans_eng: expected synced subtitle fixture
    """
    _test_get_synced_series(
        mlamd_zho_hans_fuse_clean_validate_review_flatten,
        mlamd_eng_fuse_clean_validate_review_flatten,
        mlamd_zho_hans_eng,
    )


def test_get_synced_series_t(
    t_zho_hans_fuse_clean_validate_review_flatten: Series,
    t_eng_fuse_clean_validate_review_flatten: Series,
    t_zho_hans_eng: Series,
):
    """Test get_synced_series with T subtitles.

    Arguments:
        t_zho_hans_fuse_clean_validate_review_flatten: simplified standard Chinese
          subtitle fixture
        t_eng_fuse_clean_validate_review_flatten: English subtitle fixture
        t_zho_hans_eng: expected synced subtitle fixture
    """
    _test_get_synced_series(
        t_zho_hans_fuse_clean_validate_review_flatten,
        t_eng_fuse_clean_validate_review_flatten,
        t_zho_hans_eng,
    )
