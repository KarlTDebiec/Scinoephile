#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for subtitle processing."""
from __future__ import annotations

from scinoephile.core import (
    SubtitleSeries,
    get_subtitle_blocks_for_synchronization,
    get_subtitles_block_by_time,
)
from ..data import mnt_input_english, mnt_input_hanzi


def test_get_subtitles_block_by_time(
    mnt_input_hanzi: SubtitleSeries,
):
    block = get_subtitles_block_by_time(
        mnt_input_hanzi,
        0,
        5 * 60 * 1000,
    )
    assert len(block) == 23


def test_get_subtitle_blocks_for_synchronization(
    mnt_input_hanzi: SubtitleSeries,
    mnt_input_english: SubtitleSeries,
):
    blocks = get_subtitle_blocks_for_synchronization(
        mnt_input_hanzi,
        mnt_input_english,
        16,
        12,
    )