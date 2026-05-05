#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .constants import SUBTITLE_CODEC_OUTPUTS

__all__ = ["SubtitleStream"]


@dataclass(frozen=True)
class SubtitleStream:
    """Subtitle stream metadata needed for extraction."""

    index: int
    """Absolute ffmpeg stream index."""
    language: str | None
    """ISO 639 language code from stream tags, when available."""
    codec_name: str
    """ffmpeg codec name."""
    title: str | None = None
    """Stream title from metadata, when available."""
    forced: bool = False
    """Whether stream is marked as forced."""
    sdh: bool = False
    """Whether stream is marked as hearing impaired."""
    subtitle_count: int | None = None
    """Number of subtitle packets in stream, when available."""

    @property
    def extension(self) -> str:
        """File extension to use for extracted subtitles."""
        return SUBTITLE_CODEC_OUTPUTS.get(self.codec_name, ("srt", "copy"))[0]

    @property
    def output_codec(self) -> str:
        """Ffmpeg subtitle codec to use for extracted subtitles."""
        return SUBTITLE_CODEC_OUTPUTS.get(self.codec_name, ("srt", "copy"))[1]

    @classmethod
    def from_ffprobe_stream(cls, stream: dict[str, Any]) -> SubtitleStream | None:
        """Parse a probed ffmpeg stream into subtitle metadata when applicable.

        Arguments:
            stream: ffprobe stream object
        Returns:
            subtitle stream metadata, or None for non-subtitle streams
        """
        if stream.get("codec_type") != "subtitle":
            return None

        codec_name = stream.get("codec_name")
        if not isinstance(codec_name, str) or not codec_name:
            codec_name = "subtitle"

        tags = stream.get("tags")
        if not isinstance(tags, dict):
            tags = {}

        disposition = stream.get("disposition")
        if not isinstance(disposition, dict):
            disposition = {}

        language = tags.get("language")
        if not isinstance(language, str):
            language = None

        title = tags.get("title")
        if not isinstance(title, str):
            title = None

        return cls(
            index=int(stream["index"]),
            language=language,
            codec_name=codec_name,
            title=title,
            forced=bool(disposition.get("forced")),
            sdh=bool(disposition.get("hearing_impaired")),
            subtitle_count=cls._get_optional_int(stream.get("nb_read_packets")),
        )

    @staticmethod
    def _get_optional_int(value: object) -> int | None:
        """Get an integer value if one is present.

        Arguments:
            value: value to inspect
        Returns:
            integer or None
        """
        if isinstance(value, int | str):
            return int(value)
        return None
