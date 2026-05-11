#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream metadata."""

from __future__ import annotations

from dataclasses import dataclass, replace

from scinoephile.core.exceptions import ScinoephileError

from .constants import SUBTITLE_CODEC_OUTPUTS
from .stream import Stream

__all__ = ["SubtitleStream"]


@dataclass(frozen=True)
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
    script: str | None = None
    """Detected Chinese script tag, when known."""

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
    def displayed_language(self) -> str:
        """Language tag to display for this subtitle stream."""
        if self.is_chinese and self.script is not None:
            return self.script
        return self.language or "und"

    @property
    def extension(self) -> str:
        """File extension to use for extracted subtitles."""
        if self.codec_name not in SUBTITLE_CODEC_OUTPUTS:
            raise ScinoephileError(f"Unsupported subtitle codec {self.codec_name}")
        return SUBTITLE_CODEC_OUTPUTS[self.codec_name][0]

    @property
    def is_chinese(self) -> bool:
        """Whether this stream has a Chinese language code."""
        return self.language in {"chi", "zho", "yue"}

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
        return f"{self.displayed_language}-{self.index}.{self.extension}"

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
            f"{self._format_span_time(self.first_start_ms)}-"
            f"{self._format_span_time(self.last_end_ms)}"
        )

    @property
    def stream_id(self) -> str:
        """Ffprobe-style stream identifier."""
        if self.language is None:
            return f"#0:{self.index}"
        return f"#0:{self.index}({self.displayed_language})"

    def with_script(self, script: str | None) -> SubtitleStream:
        """Return this stream with detected script metadata.

        Arguments:
            script: detected Chinese script, if any
        Returns:
            stream with script metadata
        """
        if script is None and self.is_chinese:
            script = f"{self.language}-Unknown"
        return replace(self, script=script)

    def with_stats(
        self,
        *,
        subtitle_count: int,
        first_start_ms: int | None,
        last_end_ms: int | None,
    ) -> SubtitleStream:
        """Return this stream with derived subtitle statistics.

        Arguments:
            subtitle_count: number of subtitle events
            first_start_ms: first subtitle start time in milliseconds
            last_end_ms: last subtitle end time in milliseconds
        Returns:
            stream with subtitle statistics
        """
        return replace(
            self,
            subtitle_count=subtitle_count,
            first_start_ms=first_start_ms,
            last_end_ms=last_end_ms,
        )

    def without_stats(self) -> SubtitleStream:
        """Return this stream without subtitle statistics.

        Returns:
            stream without subtitle statistics
        """
        return replace(
            self,
            subtitle_count=None,
            first_start_ms=None,
            last_end_ms=None,
        )

    @staticmethod
    def _format_span_time(time_ms: int) -> str:
        """Format a stream span timestamp.

        Arguments:
            time_ms: time in milliseconds
        Returns:
            timestamp formatted as HH:MM:SS
        """
        total_seconds = time_ms // 1000
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
