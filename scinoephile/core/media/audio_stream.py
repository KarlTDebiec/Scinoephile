#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audio stream metadata."""

from __future__ import annotations

from dataclasses import dataclass

from .stream import Stream

__all__ = ["AudioStream"]


@dataclass
class AudioStream(Stream):
    """Audio stream metadata."""

    channels: int | None = None
    """Number of audio channels, when available."""

    @property
    def details(self) -> list[str]:
        """Stream details."""
        details = super().details
        if self.channels is not None:
            details.append(f"channels={self.channels}")
        return details
