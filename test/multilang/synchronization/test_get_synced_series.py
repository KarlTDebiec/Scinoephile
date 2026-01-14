#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.multilang.synchronization.get_synced_series."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.multilang.synchronization import get_synced_series


def _test_get_synced_series(one: Series, two: Series, expected: Series):
    """Test get_synced_series.

    Arguments:
        one: subtitles series one
        two: subtitles series two
        expected: expected output series
    """
    output = get_synced_series(one, two)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


def test_get_synced_series_kob(
    kob_zho_hant_fuse_clean_validate_proofread_flatten_simplify: Series,
    kob_eng_fuse_clean_validate_proofread_flatten: Series,
    kob_zho_hans_eng: Series,
):
    """Test get_synced_series with KOB subtitles.

    Arguments:
        kob_zho_hant_fuse_clean_validate_proofread_flatten_simplify: 简体中文
          subtitle fixture
        kob_eng_fuse_clean_validate_proofread_flatten: English subtitle fixture
        kob_zho_hans_eng: expected synced subtitles fixture
    """
    _test_get_synced_series(
        kob_zho_hant_fuse_clean_validate_proofread_flatten_simplify,
        kob_eng_fuse_clean_validate_proofread_flatten,
        kob_zho_hans_eng,
    )


def test_get_synced_series_mlamd(
    mlamd_zho_hans_fuse_clean_validate_proofread_flatten: Series,
    mlamd_eng_fuse_clean_validate_proofread_flatten: Series,
    mlamd_zho_hans_eng: Series,
):
    """Test get_synced_series with MLAMD subtitles.

    Arguments:
        mlamd_zho_hans_fuse_clean_validate_proofread_flatten: 简体中文 subtitle fixture
        mlamd_eng_fuse_clean_validate_proofread_flatten: English subtitle fixture
        mlamd_zho_hans_eng: expected synced subtitle fixture
    """
    _test_get_synced_series(
        mlamd_zho_hans_fuse_clean_validate_proofread_flatten,
        mlamd_eng_fuse_clean_validate_proofread_flatten,
        mlamd_zho_hans_eng,
    )


def test_get_synced_series_mnt(
    mnt_zho_hans_fuse_clean_validate_proofread_flatten: Series,
    mnt_eng_fuse_clean_validate_proofread_flatten: Series,
    mnt_zho_hans_eng: Series,
):
    """Test get_synced_series with MNT subtitles.

    Arguments:
        mnt_zho_hans_fuse_clean_validate_proofread_flatten: 简体中文 subtitle fixture
        mnt_eng_fuse_clean_validate_proofread_flatten: English subtitle fixture
        mnt_zho_hans_eng: expected synced subtitle fixture
    """
    del mnt_zho_hans_fuse_clean_validate_proofread_flatten.events[0]
    del mnt_zho_hans_fuse_clean_validate_proofread_flatten.events[-1]
    mnt_eng_fuse_clean_validate_proofread_flatten.shift(s=-4.5)
    _test_get_synced_series(
        mnt_zho_hans_fuse_clean_validate_proofread_flatten,
        mnt_eng_fuse_clean_validate_proofread_flatten,
        mnt_zho_hans_eng,
    )


def test_get_synced_series_t(
    t_zho_hans_fuse_clean_validate_proofread_flatten: Series,
    t_eng_fuse_clean_validate_proofread_flatten: Series,
    t_zho_hans_eng: Series,
):
    """Test get_synced_series with T subtitles.

    Arguments:
        t_zho_hans_fuse_clean_validate_proofread_flatten: 简体中文 subtitle fixture
        t_eng_fuse_clean_validate_proofread_flatten: English subtitle fixture
        t_zho_hans_eng: expected synced subtitle fixture
    """
    _test_get_synced_series(
        t_zho_hans_fuse_clean_validate_proofread_flatten,
        t_eng_fuse_clean_validate_proofread_flatten,
        t_zho_hans_eng,
    )
