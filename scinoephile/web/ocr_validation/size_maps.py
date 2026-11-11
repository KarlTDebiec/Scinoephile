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

__all__ = ["CharacterGapScale", "CharacterSizeMap", "get_character_size_maps"]

_STORED = "#2154c6"
_AUTO_APPROVED = "#47a873"
_NEEDS_REVIEW = "#b97075"
_PROPOSED = "#000000"
_MAP_TARGET_SIZE = 80
_MAP_PADDING = 2


@dataclass(frozen=True)
class CharacterGapScale:
    """Number line for a measured gap within a character."""

    value: int
    """Measured gap in pixels."""
    ticks: range
    """Labels spanning the stored, accepted, and measured gaps."""
    bands: tuple[tuple[str, str, int | None, int | None], ...]
    """Colored ranges from the background through the stored gaps."""


@dataclass(frozen=True)
class CharacterSizeMap:
    """Map and proposed measurements for one box in a character."""

    legend: ClassVar[tuple[tuple[str, str, str], ...]] = (
        ("stored", "Stored", _STORED),
        ("auto-approved", "Auto-approved", _AUTO_APPROVED),
        ("needs-review", "Needs review", _NEEDS_REVIEW),
        ("proposed", "Proposed", _PROPOSED),
    )
    """Labels and colors shared by the raster and its legend."""

    width: int
    """Proposed box width in pixels."""
    height: int
    """Proposed box height in pixels."""
    gap_before: CharacterGapScale | None
    """Number line for the gap before this box, when present."""
    min_width: int
    """Box width at the left edge of the map."""
    min_height: int
    """Box height at the top edge of the map."""
    image_size: int
    """Native pixel length of either side of the square map."""
    display_size: int
    """Displayed length in physical pixels, at an integer magnification."""
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
        image, min_width, min_height = _draw_size_map(
            (width, height), known_sizes, compatible_sizes
        )
        with BytesIO() as output:
            image.save(output, format="PNG")
            image_url = (
                f"data:image/png;base64,{b64encode(output.getvalue()).decode('ascii')}"
            )

        gap_before = None
        if index:
            gap_before = _get_gap_scale(dims, known_dims, index - 1)
        maps.append(
            CharacterSizeMap(
                width=width,
                height=height,
                gap_before=gap_before,
                min_width=min_width,
                min_height=min_height,
                image_size=image.width,
                display_size=image.width * max(1, _MAP_TARGET_SIZE // image.width),
                image_url=image_url,
            )
        )
    return tuple(maps)


def _draw_size_map(
    proposed: tuple[int, int],
    known_sizes: set[tuple[int, int]],
    compatible_sizes: set[tuple[int, int]],
) -> tuple[Image.Image, int, int]:
    """Draw a square around the stored, accepted, and proposed dimensions.

    Arguments:
        proposed: measured width and height
        known_sizes: recorded sizes for this box position
        compatible_sizes: recorded sizes whose other measurements match
    Returns:
        rendered size map and the width and height at its top-left pixel
    """
    tolerance = CHAR_DIM_TOLERANCE
    sizes = known_sizes | {proposed}
    for w, h in compatible_sizes:
        sizes.update(((w - tolerance, h - tolerance), (w + tolerance, h + tolerance)))
    min_width = max(0, min(w for w, _ in sizes) - _MAP_PADDING)
    min_height = max(0, min(h for _, h in sizes) - _MAP_PADDING)
    width = max(w for w, _ in sizes) + _MAP_PADDING - min_width + 1
    height = max(h for _, h in sizes) + _MAP_PADDING - min_height + 1
    side = max(width, height)
    min_width = max(0, min_width - (side - width) // 2)
    min_height = max(0, min_height - (side - height) // 2)
    image = Image.new("RGB", (side, side), _NEEDS_REVIEW)
    draw = ImageDraw.Draw(image)
    for w, h in compatible_sizes:
        x, y = w - min_width, h - min_height
        draw.rectangle(
            (x - tolerance, y - tolerance, x + tolerance, y + tolerance),
            fill=_AUTO_APPROVED,
        )
    w, h = proposed
    x, y = w - min_width, h - min_height
    if side > _MAP_TARGET_SIZE // 2:
        draw.rectangle((x - 2, y - 2, x + 2, y + 2), outline="white")
    for known_width, known_height in known_sizes:
        draw.point((known_width - min_width, known_height - min_height), fill=_STORED)
    draw.point((x, y), fill=_PROPOSED)
    return image, min_width, min_height


def _get_gap_scale(
    dims: tuple[int, ...], known_dims: tuple[tuple[int, ...], ...], index: int
) -> CharacterGapScale:
    """Plot one gap with the rest of the character's measurements fixed.

    Arguments:
        dims: proposed widths, heights, and gaps in box order
        known_dims: recorded configurations with the same box count
        index: index of the gap in the measurements
    Returns:
        gap scale with stored values and the intervals they auto-approve
    """
    gap = dims[index]
    stored = {known[index] for known in known_dims}
    fixed_dims = dims[:index] + dims[index + 1 :]
    compatible = {
        known[index]
        for known in known_dims
        if char_dims_within_tolerance(fixed_dims, known[:index] + known[index + 1 :])
    }
    tolerance = CHAR_DIM_TOLERANCE
    lower = min(
        0, gap, min(stored, default=0), min(compatible, default=tolerance) - tolerance
    )
    upper = max(10, gap, max(stored, default=0), max(compatible, default=0) + tolerance)
    step = ((upper - lower + 19) // 20) * 5
    ticks = range(lower // step * step, ((upper + step - 1) // step + 1) * step, step)
    bands: list[tuple[str, str, int | None, int | None]] = [
        ("needs-review", "Needs review", None, None)
    ]
    bands.extend(
        ("auto-approved", "Auto-approved", value - tolerance, value + tolerance)
        for value in sorted(compatible)
    )
    bands.extend(("stored", "Stored", value, value) for value in sorted(stored))
    return CharacterGapScale(gap, ticks, tuple(bands))
