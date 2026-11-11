#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Raster maps of recorded and automatically accepted OCR box sizes."""

from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass
from io import BytesIO
from typing import ClassVar

from PIL import Image, ImageDraw

from scinoephile.image.ocr.validation.char_dims import (
    CHAR_DIM_TOLERANCE,
    char_dims_within_tolerance,
)

__all__ = ["CharacterSizeMap", "get_character_size_maps"]

_STORED = "#2154c6"
_AUTO_APPROVED = "#47a873"
_NEEDS_REVIEW = "#b97075"
_PROPOSED = "#000000"


@dataclass(frozen=True)
class CharacterSizeMap:
    """Map and proposed measurements for one box in a character."""

    legend: ClassVar[tuple[tuple[str, str], ...]] = (
        ("Stored size", _STORED),
        ("Auto-approved", _AUTO_APPROVED),
        ("Needs review", _NEEDS_REVIEW),
        ("Proposed", _PROPOSED),
    )
    """Labels and colors shared by the raster and its legend."""

    width: int
    """Proposed box width in pixels."""
    height: int
    """Proposed box height in pixels."""
    gap_before: int | None
    """Measured gap before this box, if it has a preceding box."""
    image_width: int
    """Map width in pixels."""
    image_height: int
    """Map height in pixels."""
    image_url: str
    """Inline PNG of the size map."""


def get_character_size_maps(
    dims: tuple[int, ...], known_dims: tuple[tuple[int, ...], ...]
) -> tuple[CharacterSizeMap, ...]:
    """Plot each box with the other boxes and gaps held at their measured values.

    Arguments:
        dims: proposed widths, heights, and gaps in box order
        known_dims: stored configurations with the same number of boxes
    Returns:
        ordered size maps for the proposed boxes
    """
    maps = []
    for index in range(0, len(dims), 3):
        width, height = dims[index : index + 2]
        known_sizes = {(known[index], known[index + 1]) for known in known_dims}
        fixed_dims = dims[:index] + dims[index + 2 :]
        compatible_sizes = {
            (known[index], known[index + 1])
            for known in known_dims
            if char_dims_within_tolerance(
                fixed_dims, known[:index] + known[index + 2 :]
            )
        }
        image = _draw_size_map((width, height), known_sizes, compatible_sizes)
        with BytesIO() as output:
            image.save(output, format="PNG")
            image_url = (
                f"data:image/png;base64,{b64encode(output.getvalue()).decode('ascii')}"
            )

        gap_before = None
        if index:
            gap_before = dims[index - 1]
        maps.append(
            CharacterSizeMap(
                width, height, gap_before, image.width, image.height, image_url
            )
        )
    return tuple(maps)


def _draw_size_map(
    proposed: tuple[int, int],
    known_sizes: set[tuple[int, int]],
    compatible_sizes: set[tuple[int, int]],
) -> Image.Image:
    """Draw the pixel grid, widening either axis to fit larger measurements.

    Arguments:
        proposed: measured width and height
        known_sizes: recorded sizes for this box position
        compatible_sizes: recorded sizes whose other measurements match
    Returns:
        rendered size map
    """
    tolerance = CHAR_DIM_TOLERANCE
    padding = max(tolerance, 2) + 1
    sizes = known_sizes | {proposed}
    width = max(100, max(w for w, _ in sizes) + padding)
    height = max(100, max(h for _, h in sizes) + padding)
    image = Image.new("RGB", (width, height), _NEEDS_REVIEW)
    draw = ImageDraw.Draw(image)
    for w, h in compatible_sizes:
        draw.rectangle(
            (w - tolerance, h - tolerance, w + tolerance, h + tolerance),
            fill=_AUTO_APPROVED,
        )
    w, h = proposed
    draw.rectangle((w - 2, h - 2, w + 2, h + 2), outline="white")
    for point in known_sizes:
        draw.point(point, fill=_STORED)
    draw.point(proposed, fill=_PROPOSED)
    return image
