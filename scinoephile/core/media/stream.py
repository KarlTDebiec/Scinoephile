#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Media stream metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = ["Stream"]


@dataclass(frozen=True)
class Stream:
    """Media stream metadata."""

    index: int
    """Absolute ffmpeg stream index."""
    codec_type: str = "unknown"
    """Stream codec type."""
    codec_name: str = "unknown"
    """ffmpeg codec name."""
    language: str | None = None
    """ISO 639 language code from stream tags, when available."""
    title: str | None = None
    """Stream title from metadata, when available."""

    def __post_init__(self):
        """Normalize stream metadata."""
        if self.language is not None:
            object.__setattr__(self, "language", self.language.lower())

    @property
    def displayed_language(self) -> str:
        """Language tag to display for this stream."""
        return self.language or "und"

    @property
    def probe_description(self) -> str:
        """Ffprobe-style stream description."""
        description = (
            f"Stream {self.stream_id}: {self.codec_type.title()}: {self.codec_name}"
        )
        details = self.probe_details
        if details:
            description = f"{description} ({', '.join(details)})"
        return description

    def get_probe_description(
        self,
        *,
        infile_path: Path | None = None,
        details: bool = False,
    ) -> str:
        """Get an optionally enriched ffprobe-style stream description.

        Arguments:
            infile_path: media input file, when enrichment needs file access
            details: whether to include expensive additional details
        Returns:
            ffprobe-style stream description
        """
        return self.probe_description

    @property
    def probe_details(self) -> list[str]:
        """Ffprobe-style stream details."""
        details = []
        if self.title is not None:
            details.append(f"title={self.title}")
        return details

    @property
    def stream_id(self) -> str:
        """Ffprobe-style stream identifier."""
        if self.language is None:
            return f"#0:{self.index}"
        return f"#0:{self.index}({self.displayed_language})"

    @classmethod
    def from_ffprobe_stream(cls, stream: dict[str, Any]) -> Stream | None:
        """Parse a probed ffmpeg stream into typed stream metadata.

        Arguments:
            stream: ffprobe stream object
        Returns:
            stream metadata
        """
        codec_type = stream.get("codec_type")
        if not isinstance(codec_type, str) or not codec_type:
            codec_type = "unknown"
        if codec_type == "audio":
            from .audio_stream import AudioStream  # noqa: PLC0415

            return AudioStream.from_ffprobe_stream(stream)
        if codec_type == "subtitle":
            from .subtitle_stream import SubtitleStream  # noqa: PLC0415

            subtitle_stream = SubtitleStream.from_ffprobe_stream(stream)
            if subtitle_stream is not None:
                return subtitle_stream
        if codec_type == "video":
            from .video_stream import VideoStream  # noqa: PLC0415

            return VideoStream.from_ffprobe_stream(stream)
        return cls(
            index=int(stream.get("index", 0)),
            codec_type=codec_type,
            codec_name=cls._get_codec_name(stream, codec_type),
            language=cls._get_language(stream),
            title=cls._get_title(stream),
        )

    @staticmethod
    def _get_codec_name(stream: dict[str, Any], fallback: str = "unknown") -> str:
        """Return codec name from an ffprobe stream.

        Arguments:
            stream: ffprobe stream object
            fallback: fallback codec name
        Returns:
            codec name
        """
        codec_name = stream.get("codec_name")
        if not isinstance(codec_name, str) or not codec_name:
            codec_name = fallback
        return codec_name

    @staticmethod
    def _get_language(stream: dict[str, Any]) -> str | None:
        """Return language tag from an ffprobe stream.

        Arguments:
            stream: ffprobe stream object
        Returns:
            language tag, if present
        """
        tags = stream.get("tags")
        if not isinstance(tags, dict):
            return None
        language = tags.get("language")
        if not isinstance(language, str):
            return None
        return language

    @staticmethod
    def _get_title(stream: dict[str, Any]) -> str | None:
        """Return title from an ffprobe stream.

        Arguments:
            stream: ffprobe stream object
        Returns:
            title, if present
        """
        tags = stream.get("tags")
        if not isinstance(tags, dict):
            return None
        title = tags.get("title")
        if not isinstance(title, str):
            return None
        return title
