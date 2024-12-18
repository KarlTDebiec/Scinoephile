#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.pairs."""
from __future__ import annotations

from scinoephile.core import Series
from scinoephile.core.pairs import get_pair_blocks_by_pause
from ..data.kob import kob_en_hk, kob_yue_hans_hk
from ..data.mnt import mnt_cmn_hant_hk, mnt_en_us
from ..data.pdp import pdp_en_hk, pdp_yue_hant_hk
from ..data.t import t_cmn_hans_hk, t_en_hk


def _test_get_pair_blocks_by_pause(
    series_hanzi: Series, series_english: Series, expected: int
):
    pair_blocks = get_pair_blocks_by_pause(series_hanzi, series_english)
    assert len(pair_blocks) == expected


# get_pair_blocks_by_pause
def test_get_pair_blocks_by_pause_kob(kob_yue_hans_hk: Series, kob_en_hk: Series):
    _test_get_pair_blocks_by_pause(kob_yue_hans_hk, kob_en_hk, 193)


def test_get_pair_blocks_by_pause_mnt(mnt_cmn_hant_hk: Series, mnt_en_us: Series):
    _test_get_pair_blocks_by_pause(mnt_cmn_hant_hk, mnt_en_us, 176)


def test_get_pair_blocks_by_pause_pdp(pdp_yue_hant_hk: Series, pdp_en_hk: Series):
    _test_get_pair_blocks_by_pause(pdp_yue_hant_hk, pdp_en_hk, 203)


def test_get_pair_blocks_by_pause_t(t_cmn_hans_hk: Series, t_en_hk: Series):
    _test_get_pair_blocks_by_pause(t_cmn_hans_hk, t_en_hk, 194)
