#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PNG rendering for the OCR measurement displays."""

from __future__ import annotations

from base64 import b64encode
from collections.abc import Mapping
from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageDraw

__all__ = [
    "NumberLineBand",
    "NumberLineImage",
    "get_number_line_image",
    "get_png_data_url",
]

type NumberLineBand = tuple[str, str, int | None, int | None]
"""Band key, legend label, and inclusive lower and upper measurement bounds."""


@dataclass(frozen=True)
class NumberLineImage:
    """A one-row PNG strip for each editor color scheme."""

    ticks: range
    """Labeled column boundaries, including the right edge of the strip."""
    light_url: str
    """PNG data URL for the light theme."""
    dark_url: str
    """PNG data URL for the dark theme."""

    @property
    def width(self) -> int:
        """Native PNG width, with one column per gap value."""
        return self.ticks[-1] - self.ticks[0]


def get_number_line_image(
    ticks: range,
    bands: tuple[NumberLineBand, ...],
    colors: Mapping[str, tuple[str, str]],
) -> NumberLineImage:
    """Encode each integer gap value as one pixel in a PNG strip.

    Arguments:
        ticks: labeled boundaries from the first gap through the exclusive end
        bands: colored measurement intervals in drawing order
        colors: light and dark colors for each band key
    Returns:
        one-row PNGs for both color schemes
    """
    first, last = ticks[0], ticks[-1]
    urls = []
    for theme in range(2):
        image = Image.new("RGB", (last - first, 1))
        draw = ImageDraw.Draw(image)
        for kind, _, lower, upper in bands:
            start, stop = first, last
            if lower is not None:
                start = max(first, lower)
            if upper is not None:
                stop = min(last, upper + 1)
            if start < stop:
                draw.line(
                    (start - first, 0, stop - first - 1, 0), fill=colors[kind][theme]
                )
        urls.append(get_png_data_url(image))
    return NumberLineImage(ticks, urls[0], urls[1])


def get_png_data_url(image: Image.Image) -> str:
    """Encode a rendered measurement image for embedding in the editor.

    Arguments:
        image: rendered plot
    Returns:
        PNG data URL
    """
    with BytesIO() as output:
        image.save(output, format="PNG")
        return f"data:image/png;base64,{b64encode(output.getvalue()).decode('ascii')}"
