#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.pairs."""

from __future__ import annotations

from scinoephile.core import Series
from scinoephile.core.pairs import get_pair_blocks_by_pause
from ..data.kob import kob_eng, kob_yue_hans
from ..data.mnt import mnt_zho_hant, mnt_eng
from ..data.pdp import pdp_eng, pdp_yue_hant
from ..data.t import t_zho_hans, t_eng


def _test_get_pair_blocks_by_pause(
    series_hanzi: Series, series_english: Series, expected: int
):
    pair_blocks = get_pair_blocks_by_pause(series_hanzi, series_english)
    assert len(pair_blocks) == expected


# get_pair_blocks_by_pause
def test_get_pair_blocks_by_pause_kob(kob_yue_hans: Series, kob_eng: Series):
    _test_get_pair_blocks_by_pause(kob_yue_hans, kob_eng, 193)


def test_get_pair_blocks_by_pause_mnt(mnt_zho_hant: Series, mnt_eng: Series):
    _test_get_pair_blocks_by_pause(mnt_zho_hant, mnt_eng, 176)


def test_get_pair_blocks_by_pause_pdp(pdp_yue_hant: Series, pdp_eng: Series):
    _test_get_pair_blocks_by_pause(pdp_yue_hant, pdp_eng, 203)


def test_get_pair_blocks_by_pause_t(t_zho_hans: Series, t_eng: Series):
    _test_get_pair_blocks_by_pause(t_zho_hans, t_eng, 194)
