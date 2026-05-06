#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR bounding box."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["PaddleOcrBoundingBox"]


@dataclass(frozen=True)
class PaddleOcrBoundingBox:
    """PaddleOCR text bounding box."""

    top_left: tuple[float, float]
    """Top-left point."""
    top_right: tuple[float, float]
    """Top-right point."""
    bottom_right: tuple[float, float]
    """Bottom-right point."""
    bottom_left: tuple[float, float]
    """Bottom-left point."""

    @property
    def center(self) -> tuple[float, float]:
        """Center point."""
        return (
            (
                self.top_left[0]
                + self.top_right[0]
                + self.bottom_right[0]
                + self.bottom_left[0]
            )
            / 4,
            (
                self.top_left[1]
                + self.top_right[1]
                + self.bottom_right[1]
                + self.bottom_left[1]
            )
            / 4,
        )

    @property
    def height(self) -> float:
        """Bounding box height."""
        return max(
            abs(self.bottom_left[1] - self.top_left[1]),
            abs(self.bottom_right[1] - self.top_right[1]),
        )
