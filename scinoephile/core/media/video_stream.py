#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Video stream metadata."""

from __future__ import annotations

from dataclasses import dataclass

from .stream import Stream

__all__ = ["VideoStream"]


@dataclass
class VideoStream(Stream):
    """Video stream metadata."""

    width: int | None = None
    """Video width in pixels, when available."""
    height: int | None = None
    """Video height in pixels, when available."""

    @property
    def details(self) -> list[str]:
        """Stream details."""
        details = super().details
        if self.width is not None and self.height is not None:
            details.append(f"{self.width}x{self.height}")
        return details
