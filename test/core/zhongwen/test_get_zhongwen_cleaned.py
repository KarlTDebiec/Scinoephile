#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.zhongwen.get_zhongwen_cleaned."""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.zhongwen import get_zhongwen_cleaned


def _test_get_zhongwen_cleaned(series: Series, expected: Series):
    """Test get_zhongwen_cleaned.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_zhongwen_cleaned(series)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


def test_get_zhongwen_cleaned_kob(kob_yue_hans: Series, kob_yue_hans_clean: Series):
    """Test get_zhongwen_cleaned with KOB 简体粤文 subtitles.

    Arguments:
        kob_yue_hans: KOB 简体粤文 series fixture
        kob_yue_hans_clean: Expected cleaned KOB 简体粤文 series fixture
    """
    _test_get_zhongwen_cleaned(kob_yue_hans, kob_yue_hans_clean)


def test_get_zhongwen_cleaned_mlamd(
    mlamd_zho_hans_fuse_proofread: Series, mlamd_zho_hans_fuse_proofread_clean: Series
):
    """Test get_zhongwen_cleaned with MLAMD 繁体中文 subtitles.

    Arguments:
        mlamd_zho_hans_fuse_proofread: MLAMD 繁体中文 series fixture
        mlamd_zho_hans_fuse_proofread_clean: Expected cleaned MLAMD 繁体中文 series
          fixture
    """
    _test_get_zhongwen_cleaned(
        mlamd_zho_hans_fuse_proofread, mlamd_zho_hans_fuse_proofread_clean
    )


def test_get_zhongwen_cleaned_mnt(
    mnt_zho_hans_fuse_proofread: Series, mnt_zho_hans_fuse_proofread_clean: Series
):
    """Test get_zhongwen_cleaned with MNT 繁体中文 subtitles.

    Arguments:
        mnt_zho_hans_fuse_proofread: MNT 繁体中文 series fixture
        mnt_zho_hans_fuse_proofread_clean: Expected cleaned MNT 繁体中文 series fixture
    """
    _test_get_zhongwen_cleaned(
        mnt_zho_hans_fuse_proofread, mnt_zho_hans_fuse_proofread_clean
    )


def test_get_zhongwen_cleaned_t(t_zho_hans: Series, t_zho_hans_clean: Series):
    """Test get_zhongwen_cleaned with T 簡體中文 subtitles.

    Arguments:
        t_zho_hans: T 簡體中文 series fixture
        t_zho_hans_clean: Expected cleaned T 簡體中文 series fixture
    """
    _test_get_zhongwen_cleaned(t_zho_hans, t_zho_hans_clean)
