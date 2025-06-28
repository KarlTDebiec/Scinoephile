#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Block of subtitles within an AudioSeries."""

from __future__ import annotations

from typing import Any

from pydub import AudioSegment

from scinoephile.core.block import Block


class AudioBlock(Block):
    """Block of subtitles within an AudioSeries."""

    def __init__(
        self,
        buffered_start: int,
        buffered_end: int,
        audio: AudioSegment,
        **kwargs: Any,
    ) -> None:
        """Initialize.

        Arguments:
            buffered_start: Start index of buffered audio
            buffered_end: End index of buffered audio
            audio: Audio of block
            **kwargs: Additional keyword arguments passed to Block constructor
        """
        super().__init__(**kwargs)
        self.buffered_start = buffered_start
        self.buffered_end = buffered_end
        self.audio = audio

    def __repr__(self) -> str:
        """Get string representation."""
        return (
            f"{self.__class__.__name__}("
            f"start_idx={self.start_idx}, "
            f"end_idx={self.end_idx}, "
            f"start={self.start}, "
            f"end={self.end}, "
            f"buffered_start={self.buffered_start}, "
            f"buffered_end={self.buffered_end})"
        )
