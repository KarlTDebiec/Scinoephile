#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.english.get_english_proofread."""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.english.proofreading import get_english_proofread


def _test_get_english_proofed(series: Series, expected: Series):
    """Test get_english_proofed.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_english_proofread(series)

    assert len(series) == len(output)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies:\n" + "\n".join(errors))


def test_get_english_proofed_kob(kob_eng_fuse: Series, kob_eng_fuse_proofread: Series):
    """Test get_english_proofed with KOB English subtitles.

    Arguments:
        kob_eng_fuse: KOB English series fixture
        kob_eng_fuse_proofread: Expected proofed KOB English series fixture
    """
    _test_get_english_proofed(kob_eng_fuse, kob_eng_fuse_proofread)


def test_get_english_proofed_mlamd(
    mlamd_eng_fuse: Series, mlamd_eng_fuse_proofread: Series
):
    """Test get_english_proofed with MLAMD English subtitles.

    Arguments:
        mlamd_eng_fuse: MLAMD English series fixture
        mlamd_eng_fuse_proofread: Expected proofed MLAMD English series fixture
    """
    _test_get_english_proofed(mlamd_eng_fuse, mlamd_eng_fuse_proofread)


def test_get_english_proofed_mnt(mnt_eng_fuse: Series, mnt_eng_fuse_proofread: Series):
    """Test get_english_proofed with MNT English subtitles.

    Arguments:
        mnt_eng_fuse: MNT English series fixture
        mnt_eng_fuse_proofread: Expected proofed MNT English series fixture
    """
    _test_get_english_proofed(mnt_eng_fuse, mnt_eng_fuse_proofread)


def test_get_english_proofed_t(t_eng_fuse: Series, t_eng_fuse_proofread: Series):
    """Test get_english_proofed with T English subtitles.

    Arguments:
        t_eng_fuse: T English series fixture
        t_eng_fuse_proofread: Expected proofed T English series fixture
    """
    _test_get_english_proofed(t_eng_fuse, t_eng_fuse_proofread)
