#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for bilingual subtitle processing."""
from __future__ import annotations

from scinoephile.core import SubtitleSeries
from scinoephile.core.bilingual import get_bilingual_subtitles
from ..data import mnt_input_english, mnt_input_hanzi


def test_get_bilingual_subtitles(
    mnt_input_hanzi: SubtitleSeries,
    mnt_input_english: SubtitleSeries,
):
    bilingual = get_bilingual_subtitles(mnt_input_hanzi, mnt_input_english)