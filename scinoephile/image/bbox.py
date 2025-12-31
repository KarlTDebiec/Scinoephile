#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Bounding box utilities."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "Bbox",
    "get_merged_bbox",
]


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


def get_merged_bbox(bboxes: list[Bbox]) -> Bbox:
    """Get merged bbox and dims tuple from bboxes.

    Arguments:
        bboxes: bboxes to merge
    Returns:
        merged bbox and dims tuple
    """
    return Bbox(
        x1=min(bbox.x1 for bbox in bboxes),
        x2=max(bbox.x2 for bbox in bboxes),
        y1=min(bbox.y1 for bbox in bboxes),
        y2=max(bbox.y2 for bbox in bboxes),
    )
