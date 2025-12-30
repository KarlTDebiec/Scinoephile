#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Bounding box utilities."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Bbox"]


@dataclass(frozen=True, slots=True)
class Bbox:
    """Bounding box coordinates."""

    left: int
    """Left x coordinate."""
    right: int
    """Right x coordinate."""
    top: int
    """Top y coordinate."""
    bottom: int
    """Bottom y coordinate."""

    @property
    def width(self) -> int:
        """Width of bbox."""
        return self.right - self.left

    @property
    def height(self) -> int:
        """Height of bbox."""
        return self.bottom - self.top
