#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.eng.get_eng_cleaned."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.lang.eng import get_eng_cleaned

# noinspection PyProtectedMember


def _test_get_eng_cleaned(series: Series, expected: Series):
    """Test get_eng_cleaned.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_eng_cleaned(series, remove_empty=False)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


def test_get_eng_cleaned_kob(
    kob_eng_fuse: Series,
    kob_eng_fuse_clean: Series,
):
    """Test get_eng_cleaned with KOB English subtitles.

    Arguments:
        kob_eng_fuse: KOB English series fixture
        kob_eng_fuse_clean: Expected cleaned KOB English series fixture
    """
    _test_get_eng_cleaned(kob_eng_fuse, kob_eng_fuse_clean)


def test_get_eng_cleaned_mlamd(
    mlamd_eng_fuse: Series,
    mlamd_eng_fuse_clean: Series,
):
    """Test get_eng_cleaned with MLAMD English subtitles.

    Arguments:
        mlamd_eng_fuse: MLAMD English series fixture
        mlamd_eng_fuse_clean: Expected cleaned MLAMD English series fixture
    """
    _test_get_eng_cleaned(mlamd_eng_fuse, mlamd_eng_fuse_clean)


def test_get_eng_cleaned_mnt(
    mnt_eng_fuse: Series,
    mnt_eng_fuse_clean: Series,
):
    """Test get_eng_cleaned with MNT English subtitles.

    Arguments:
        mnt_eng_fuse: MNT English series fixture
        mnt_eng_fuse_clean: Expected cleaned MNT English series fixture
    """
    _test_get_eng_cleaned(mnt_eng_fuse, mnt_eng_fuse_clean)


def test_get_eng_cleaned_t(
    t_eng_fuse: Series,
    t_eng_fuse_clean: Series,
):
    """Test get_eng_cleaned with T English subtitles.

    Arguments:
        t_eng_fuse: T English series fixture
        t_eng_fuse_clean: Expected cleaned T English series fixture
    """
    _test_get_eng_cleaned(t_eng_fuse, t_eng_fuse_clean)
