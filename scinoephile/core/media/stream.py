#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Media stream metadata."""

from __future__ import annotations

from dataclasses import dataclass

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
    def description(self) -> str:
        """Stream description."""
        description = (
            f"Stream {self.stream_id}: {self.codec_type.title()}: {self.codec_name}"
        )
        details = self.details
        if details:
            description = f"{description} ({', '.join(details)})"
        return description

    @property
    def details(self) -> list[str]:
        """Stream details."""
        details = []
        if self.title is not None:
            details.append(f"title={self.title}")
        return details

    @property
    def stream_id(self) -> str:
        """Ffprobe-style stream identifier."""
        if self.language is None:
            return f"#0:{self.index}"
        return f"#0:{self.index}({self.language})"
