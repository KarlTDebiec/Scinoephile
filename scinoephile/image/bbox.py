#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Bounding box coordinates."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Bbox"]


@dataclass
class Bbox:
    """Bounding box coordinates."""

    x1: int
    """Left x coordinate."""
    x2: int
    """Right x coordinate."""
    y1: int
    """Top y coordinate."""
    y2: int
    """Bottom y coordinate."""

    @property
    def width(self) -> int:
        """Width of bbox."""
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        """Height of bbox."""
        return self.y2 - self.y1
