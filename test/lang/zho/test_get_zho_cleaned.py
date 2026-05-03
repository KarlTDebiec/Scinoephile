#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_cleaned."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.cleaning import get_zho_cleaned


def _test_get_zho_cleaned(series: Series, expected: Series):
    """Test get_zho_cleaned.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_zho_cleaned(series, remove_empty=False)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


def test_get_zho_cleaned_kob(
    kob_zho_hant_ocr_fuse: Series,
    kob_zho_hant_ocr_fuse_clean: Series,
):
    """Test get_zho_cleaned with KOB traditional standard Chinese subtitles.

    Arguments:
        kob_zho_hant_ocr_fuse: KOB traditional standard Chinese series fixture
        kob_zho_hant_ocr_fuse_clean: Expected cleaned KOB traditional standard
          Chinese series fixture
    """
    _test_get_zho_cleaned(kob_zho_hant_ocr_fuse, kob_zho_hant_ocr_fuse_clean)


def test_get_zho_cleaned_mlamd(
    mlamd_zho_hans_fuse: Series,
    mlamd_zho_hans_fuse_clean: Series,
):
    """Test get_zho_cleaned with MLAMD simplified standard Chinese subtitles.

    Arguments:
        mlamd_zho_hans_fuse: MLAMD simplified standard Chinese series fixture
        mlamd_zho_hans_fuse_clean: Expected cleaned MLAMD simplified standard
          Chinese series fixture
    """
    _test_get_zho_cleaned(mlamd_zho_hans_fuse, mlamd_zho_hans_fuse_clean)


def test_get_zho_cleaned_mnt(
    mnt_zho_hans_fuse: Series,
    mnt_zho_hans_fuse_clean: Series,
):
    """Test get_zho_cleaned with MNT simplified standard Chinese subtitles.

    Arguments:
        mnt_zho_hans_fuse: MNT simplified standard Chinese series fixture
        mnt_zho_hans_fuse_clean: Expected cleaned MNT simplified standard Chinese
          series fixture
    """
    _test_get_zho_cleaned(mnt_zho_hans_fuse, mnt_zho_hans_fuse_clean)


def test_get_zho_cleaned_t(
    t_zho_hans_fuse: Series,
    t_zho_hans_fuse_clean: Series,
):
    """Test get_zho_cleaned with T simplified standard Chinese subtitles.

    Arguments:
        t_zho_hans_fuse: T simplified standard Chinese series fixture
        t_zho_hans_fuse_clean: Expected cleaned T simplified standard Chinese
          series fixture
    """
    _test_get_zho_cleaned(t_zho_hans_fuse, t_zho_hans_fuse_clean)
