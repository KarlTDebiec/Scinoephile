#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.eng.get_eng_proofread."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.lang.eng import get_eng_proofread


def _test_get_eng_proofread(series: Series, expected: Series):
    """Test get_eng_proofread.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_eng_proofread(series)

    assert len(series) == len(output)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies:\n" + "\n".join(errors))


def test_get_eng_proofread_kob(
    kob_eng_fuse_clean_validate: Series,
    kob_eng_fuse_clean_validate_proofread: Series,
):
    """Test get_eng_proofread with KOB English subtitles.

    Arguments:
        kob_eng_fuse_clean_validate: KOB English series fixture
        kob_eng_fuse_clean_validate_proofread: Expected proofread KOB English series
          fixture
    """
    _test_get_eng_proofread(
        kob_eng_fuse_clean_validate,
        kob_eng_fuse_clean_validate_proofread,
    )


def test_get_eng_proofread_mlamd(
    mlamd_eng_fuse_clean_validate: Series,
    mlamd_eng_fuse_clean_validate_proofread: Series,
):
    """Test get_eng_proofread with MLAMD English subtitles.

    Arguments:
        mlamd_eng_fuse_clean_validate: MLAMD English series fixture
        mlamd_eng_fuse_clean_validate_proofread: Expected proofread MLAMD English series
          fixture
    """
    _test_get_eng_proofread(
        mlamd_eng_fuse_clean_validate, mlamd_eng_fuse_clean_validate_proofread
    )


def test_get_eng_proofread_mnt(
    mnt_eng_fuse: Series,
    mnt_eng_fuse_proofread: Series,
):
    """Test get_eng_proofread with MNT English subtitles.

    Arguments:
        mnt_eng_fuse: MNT English series fixture
        mnt_eng_fuse_proofread: Expected proofread MNT English series
          fixture
    """
    _test_get_eng_proofread(
        mnt_eng_fuse,
        mnt_eng_fuse_proofread,
    )


def test_get_eng_proofread_t(
    t_eng_fuse: Series,
    t_eng_fuse_proofread: Series,
):
    """Test get_eng_proofread with T English subtitles.

    Arguments:
        t_eng_fuse: T English series fixture
        t_eng_fuse_proofread: Expected proofread T English series fixture
    """
    _test_get_eng_proofread(
        t_eng_fuse,
        t_eng_fuse_proofread,
    )
