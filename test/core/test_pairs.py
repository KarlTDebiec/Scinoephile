#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.pairs."""

from __future__ import annotations

from scinoephile.core import Series
from scinoephile.core.pairs import get_pair_blocks_by_pause


def _test_get_pair_blocks_by_pause(
    series_one: Series, series_two: Series, expected: int
):
    """Test get_pair_blocks_by_pause.

    Arguments:
        series_one: series one with which to test
        series_two: series two with which to test
        expected: Expected number of pair blocks
    """
    pair_blocks = get_pair_blocks_by_pause(series_one, series_two)
    assert len(pair_blocks) == expected


# get_pair_blocks_by_pause
def test_get_pair_blocks_by_pause_kob(kob_yue_hans: Series, kob_eng: Series):
    """Test get_pair_blocks_by_pause with KOB 简体粤文 and English subtitles.

    Arguments:
        kob_yue_hans: KOB 简体粤文 series fixture
        kob_eng: KOB English series fixture
    """
    _test_get_pair_blocks_by_pause(kob_yue_hans, kob_eng, 193)


def test_get_pair_blocks_by_pause_mnt(mnt_zho_hant: Series, mnt_eng: Series):
    """Test get_pair_blocks_by_pause with MNT 繁体中文 and English subtitles.

    Arguments:
        mnt_zho_hant: MNT 繁体中文 series fixture
        mnt_eng: MNT English series fixture
    """
    _test_get_pair_blocks_by_pause(mnt_zho_hant, mnt_eng, 176)


def test_get_pair_blocks_by_pause_t(t_zho_hans: Series, t_eng: Series):
    """Test get_pair_blocks_by_pause with T 简体中文 and English subtitles.

    Arguments:
        t_zho_hans: T 简体中文 series fixture
        t_eng: T English series fixture
    """
    _test_get_pair_blocks_by_pause(t_zho_hans, t_eng, 192)
