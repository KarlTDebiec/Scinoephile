#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Video stream metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .stream import Stream

__all__ = ["VideoStream"]


@dataclass(frozen=True)
class VideoStream(Stream):
    """Video stream metadata."""

    width: int | None = None
    """Video width in pixels, when available."""
    height: int | None = None
    """Video height in pixels, when available."""

    @property
    def probe_details(self) -> list[str]:
        """Ffprobe-style stream details."""
        details = []
        if self.width is not None and self.height is not None:
            details.append(f"{self.width}x{self.height}")
        details.extend(super().probe_details)
        return details

    @classmethod
    def from_ffprobe_stream(cls, stream: dict[str, Any]) -> VideoStream:
        """Parse a probed ffmpeg stream into video stream metadata.

        Arguments:
            stream: ffprobe stream object
        Returns:
            video stream metadata
        """
        width = stream.get("width")
        if not isinstance(width, int):
            width = None
        height = stream.get("height")
        if not isinstance(height, int):
            height = None
        return cls(
            index=int(stream.get("index", 0)),
            codec_type="video",
            codec_name=cls._get_codec_name(stream, "video"),
            language=cls._get_language(stream),
            title=cls._get_title(stream),
            width=width,
            height=height,
        )
