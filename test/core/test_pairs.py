#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for scinoephile.core.synchronization"""
from __future__ import annotations

from scinoephile.core import SubtitleSeries
from scinoephile.core.pairs import get_pair_blocks_by_pause
from ..data.mnt import mnt_input_english, mnt_input_hanzi


def test_get_pair_blocks_by_pause(
    mnt_input_hanzi: SubtitleSeries,
    mnt_input_english: SubtitleSeries,
) -> None:
    pair_blocks = get_pair_blocks_by_pause(mnt_input_hanzi, mnt_input_english)
    assert len(pair_blocks) == 176