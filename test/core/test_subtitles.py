#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for subtitle processing."""
from __future__ import annotations

from scinoephile.core import SubtitleSeries
from scinoephile.core.pairs import (
    get_merged_from_blocks,
    get_pair_blocks_by_pause,
)
from ..data.mnt import mnt_input_english, mnt_input_hanzi


def test_get_pair_blocks_by_pause_and_get_merged_from_blocks(
    mnt_input_hanzi: SubtitleSeries,
    mnt_input_english: SubtitleSeries,
):
    blocks = get_pair_blocks_by_pause(
        mnt_input_hanzi,
        mnt_input_english,
    )

    assert len(mnt_input_hanzi) == sum([len(b[0].events) for b in blocks])
    assert len(mnt_input_english) == sum([len(b[1].events) for b in blocks])

    merged_hanzi = get_merged_from_blocks([b[0] for b in blocks])
    merged_english = get_merged_from_blocks([b[1] for b in blocks])

    assert len(mnt_input_hanzi) == len(merged_hanzi)
    assert len(mnt_input_english) == len(merged_english)
