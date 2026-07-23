#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream metadata."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.timing import format_time_ms

from .constants import SUBTITLE_CODEC_OUTPUTS
from .stream import Stream

__all__ = ["SubtitleStream"]


@dataclass
class SubtitleStream(Stream):
    """Subtitle stream metadata needed for extraction."""

    codec_type: str = "subtitle"
    """Stream codec type."""
    codec_name: str = "subtitle"
    """ffmpeg codec name."""
    forced: bool = False
    """Whether stream is marked as forced."""
    sdh: bool = False
    """Whether stream is marked as hearing impaired."""
    subtitle_count: int | None = None
    """Number of subtitle packets in stream, when available."""
    first_start_ms: int | None = None
    """First subtitle start time in milliseconds, when known."""
    last_end_ms: int | None = None
    """Last subtitle end time in milliseconds, when known."""

    @property
    def details(self) -> list[str]:
        """Stream details."""
        details = super().details
        if self.subtitle_count is not None:
            details.append(f"subtitles={self.subtitle_count}")
        span = self.span
        if span is not None:
            details.append(f"span={span}")
        return details

    @property
    def extension(self) -> str:
        """File extension to use for extracted subtitles."""
        if self.codec_name not in SUBTITLE_CODEC_OUTPUTS:
            raise ScinoephileError(f"Unsupported subtitle codec {self.codec_name}")
        return SUBTITLE_CODEC_OUTPUTS[self.codec_name][0]

    @property
    def outfile_filename(self) -> str:
        """Filename to use when extracting this subtitle stream.

        Raises:
            ValueError: if the stream has no language tag
        """
        if self.language is None:
            raise ValueError(
                "Subtitle stream must have a language to build output path"
            )
        return f"{self.language}-{self.index}.{self.extension}"

    @property
    def output_codec(self) -> str:
        """Ffmpeg subtitle codec to use for extracted subtitles."""
        if self.codec_name not in SUBTITLE_CODEC_OUTPUTS:
            raise ScinoephileError(f"Unsupported subtitle codec {self.codec_name}")
        return SUBTITLE_CODEC_OUTPUTS[self.codec_name][1]

    @property
    def span(self) -> str | None:
        """Subtitle stream active span formatted as HH:MM:SS-HH:MM:SS."""
        if self.first_start_ms is None or self.last_end_ms is None:
            return None
        return (
            f"{format_time_ms(self.first_start_ms)}-{format_time_ms(self.last_end_ms)}"
        )
