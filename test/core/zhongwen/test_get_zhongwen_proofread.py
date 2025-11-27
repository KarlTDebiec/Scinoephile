#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.zhongwen.get_zhongwen_proofread."""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.zhongwen.proofreading import get_zhongwen_proofread


def _test_get_zhongwen_proofread(series: Series, expected: Series):
    """Test get_zhongwen_proofread.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_zhongwen_proofread(series)

    assert len(series) == len(output)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies:\n" + "\n".join(errors))


def test_get_zhongwen_proofread_kob(
    kob_zho_hant_fuse: Series, kob_zho_hant_fuse_proofread: Series
):
    """Test get_zhongwen_proofread with KOB English subtitles.

    Arguments:
        kob_zho_hans_fuse: KOB English series fixture
        kob_zho_hant_fuse: Expected proofread KOB English series fixture
    """
    _test_get_zhongwen_proofread(kob_zho_hant_fuse, kob_zho_hant_fuse_proofread)


def test_get_zhongwen_proofread_mlamd(
    mlamd_zho_hans_fuse: Series, mlamd_zho_hans_fuse_proofread: Series
):
    """Test get_zhongwen_proofread with MLAMD English subtitles.

    Arguments:
        mlamd_zho_hans_fuse: MLAMD English series fixture
        mlamd_zho_hans_fuse_proofread: Expected proofread MLAMD English series fixture
    """
    _test_get_zhongwen_proofread(mlamd_zho_hans_fuse, mlamd_zho_hans_fuse_proofread)


def test_get_zhongwen_proofread_mnt(
    mnt_zho_hans_fuse: Series, mnt_zho_hans_fuse_proofread: Series
):
    """Test get_zhongwen_proofread with MNT English subtitles.

    Arguments:
        mnt_zho_hans_fuse: MNT English series fixture
        mnt_zho_hans_fuse_proofread: Expected proofread MNT English series fixture
    """
    _test_get_zhongwen_proofread(mnt_zho_hans_fuse, mnt_zho_hans_fuse_proofread)


def test_get_zhongwen_proofread_t(
    t_zho_hans_fuse: Series, t_zho_hans_fuse_proofread: Series
):
    """Test get_zhongwen_proofread with T English subtitles.

    Arguments:
        t_zho_hans_fuse: T English series fixture
        t_zho_hans_fuse_proofread: Expected proofread T English series fixture
    """
    _test_get_zhongwen_proofread(t_zho_hans_fuse, t_zho_hans_fuse_proofread)
