#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for scinoephile.core.pairs"""
from __future__ import annotations

from scinoephile.core import Series
from scinoephile.core.pairs import get_pair_blocks_by_pause
from ..data.mnt import mnt_cmn_hant_hk, mnt_en_us


def _test_get_pair_blocks_by_pause(
    series_hanzi: Series, series_english: Series, expected: int
):
    pair_blocks = get_pair_blocks_by_pause(series_hanzi, series_english)
    assert len(pair_blocks) == expected


def test_get_pair_blocks_by_pause_mnt(mnt_cmn_hant_hk: Series, mnt_en_us: Series):
    _test_get_pair_blocks_by_pause(mnt_cmn_hant_hk, mnt_en_us, 176)
