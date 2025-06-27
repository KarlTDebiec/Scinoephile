#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Block of subtitles within an AudioSeries."""

from __future__ import annotations

from pydub import AudioSegment

from scinoephile.audio import AudioSeries
from scinoephile.core.block import Block


class AudioBlock(Block):
    """Block of subtitles within an AudioSeries."""

    def __init__(
        self,
        series: AudioSeries,
        start_idx: int,
        end_idx: int,
        buffered_start: int,
        buffered_end: int,
        audio: AudioSegment,
    ) -> None:
        """Initialize.

        Arguments:
            series: AudioSeries containing block
            start_idx: Start index of block
            end_idx: End index of block
            audio: Audio of block
        """
        super().__init__(series, start_idx, end_idx)
        self.buffered_start = buffered_start
        self.buffered_end = buffered_end
        self.audio = audio
