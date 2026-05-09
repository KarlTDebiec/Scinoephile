#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audio stream metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .stream import Stream

__all__ = ["AudioStream"]


@dataclass(frozen=True)
class AudioStream(Stream):
    """Audio stream metadata."""

    channels: int | None = None
    """Number of audio channels, when available."""

    @property
    def probe_details(self) -> list[str]:
        """Ffprobe-style stream details."""
        details = super().probe_details
        if self.channels is not None:
            details.append(f"channels={self.channels}")
        return details

    @classmethod
    def from_ffprobe_stream(cls, stream: dict[str, Any]) -> AudioStream:
        """Parse a probed ffmpeg stream into audio stream metadata.

        Arguments:
            stream: ffprobe stream object
        Returns:
            audio stream metadata
        """
        channels = stream.get("channels")
        if not isinstance(channels, int):
            channels = None
        return cls(
            index=int(stream.get("index", 0)),
            codec_type="audio",
            codec_name=cls._get_codec_name(stream, "audio"),
            language=cls._get_language(stream),
            title=cls._get_title(stream),
            channels=channels,
        )
