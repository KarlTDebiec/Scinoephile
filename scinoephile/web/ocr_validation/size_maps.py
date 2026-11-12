#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Raster maps of recorded and automatically accepted OCR box sizes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from PIL import Image, ImageDraw

from scinoephile.image.ocr.validation.char_dims import CHAR_DIM_TOLERANCE

from .measurement_images import (
    NumberLineBand,
    NumberLineImage,
    get_number_line_image,
    get_png_data_url,
)

__all__ = ["CharacterGapScale", "CharacterSizeMap", "get_character_size_maps"]

_STORED = "#0080ff"
_STORED_LABEL = "Previously approved"
_AUTO_APPROVED = "#00ff00"
_NEEDS_REVIEW = "#000000"
_PROPOSED = "#ff0000"
_MAP_TARGET_SIZE = 80
_MAP_PADDING = 2


@dataclass(frozen=True)
class CharacterGapScale:
    """Number line for a measured gap within a character."""

    value: int
    """Measured gap in pixels."""
    image: NumberLineImage
    """Rendered scale with the stored, accepted, and measured gaps."""


@dataclass(frozen=True)
class CharacterSizeMap:
    """Map and proposed measurements for one box in a character."""

    legend: ClassVar[tuple[tuple[str, str, str], ...]] = (
        ("stored", _STORED_LABEL, _STORED),
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
    """Plot the full tolerance around stored box sizes and gaps, and mark the proposal.

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
        image, min_width, min_height = _draw_size_map((width, height), known_sizes)
        gap_before = None
        if index:
            gap_index = index - 1
            gap_before = _get_gap_scale(
                dims[gap_index], {known[gap_index] for known in known_dims}
            )
        maps.append(
            CharacterSizeMap(
                width=width,
                height=height,
                gap_before=gap_before,
                min_width=min_width,
                min_height=min_height,
                image_size=image.width,
                display_size=image.width * max(1, _MAP_TARGET_SIZE // image.width),
                image_url=get_png_data_url(image),
            )
        )
    return tuple(maps)


def _draw_size_map(
    proposed: tuple[int, int], known_sizes: set[tuple[int, int]]
) -> tuple[Image.Image, int, int]:
    """Draw a square around the stored, accepted, and proposed dimensions.

    Arguments:
        proposed: measured width and height
        known_sizes: recorded sizes for this box position
    Returns:
        rendered size map and the width and height at its top-left pixel
    """
    tolerance = CHAR_DIM_TOLERANCE
    sizes = known_sizes | {proposed}
    for w, h in known_sizes:
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
    for w, h in known_sizes:
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


def _get_gap_scale(gap: int, stored: set[int]) -> CharacterGapScale:
    """Plot the proposed gap and the tolerance around every stored gap.

    Arguments:
        gap: proposed gap in pixels
        stored: recorded gaps at this position for the same box count
    Returns:
        gap scale with stored values and the intervals they auto-approve
    """
    tolerance = CHAR_DIM_TOLERANCE
    lower = min(0, gap, min(stored, default=tolerance) - tolerance)
    upper = max(10, gap + 1, max(stored, default=0) + tolerance + 1)
    step = ((upper - lower + 19) // 20) * 5
    ticks = range(lower // step * step, ((upper + step - 1) // step + 1) * step, step)
    bands: list[NumberLineBand] = [("needs-review", "Needs review", None, None)]
    bands.extend(
        ("auto-approved", "Auto-approved", value - tolerance, value + tolerance)
        for value in sorted(stored)
    )
    bands.extend(("stored", _STORED_LABEL, value, value) for value in sorted(stored))
    bands.append(("proposed", "Proposed", gap, gap))
    colors = {kind: (color, color) for kind, _, color in CharacterSizeMap.legend}
    image = get_number_line_image(ticks, tuple(bands), colors, width=160)
    return CharacterGapScale(gap, image)
