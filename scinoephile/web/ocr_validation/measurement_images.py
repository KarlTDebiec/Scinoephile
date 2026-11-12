#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PNG rendering for the OCR measurement displays."""

from __future__ import annotations

from base64 import b64encode
from collections.abc import Mapping
from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

__all__ = [
    "NumberLineBand",
    "NumberLineImage",
    "get_number_line_image",
    "get_png_data_url",
]

type NumberLineBand = tuple[str, str, int | None, int | None]
"""Band key, legend label, and inclusive lower and upper measurement bounds."""

_SCALE = 2
_AXIS_PADDING = 40
_TRACK_TOP = 42
_TRACK_BOTTOM = 57


@dataclass(frozen=True)
class NumberLineImage:
    """A number line rendered for both editor color schemes."""

    width: int
    """Display width in CSS pixels."""
    height: int
    """Display height in CSS pixels."""
    light_url: str
    """PNG data URL for the light theme."""
    dark_url: str
    """PNG data URL for the dark theme."""


def get_number_line_image(
    ticks: range,
    bands: tuple[NumberLineBand, ...],
    colors: Mapping[str, tuple[str, str]],
    *,
    width: int,
    reading: int | None = None,
) -> NumberLineImage:
    """Render a gap scale with ticks at the left edges of measurement intervals.

    Arguments:
        ticks: labeled boundaries including both ends of the scale
        bands: colored measurement intervals in drawing order
        colors: light and dark colors for each band key
        width: display width in CSS pixels
        reading: optional measured gap to label below the track
    Returns:
        number line PNGs for both color schemes
    """
    height = 33
    if reading is not None:
        height = 54
    image_size = (width * _SCALE, height * _SCALE)
    track_width = image_size[0] - 2 * _AXIS_PADDING
    first, last = ticks[0], ticks[-1]
    font = ImageFont.load_default(size=26)

    def position(value: int | float) -> int:
        """Map a measurement boundary to its column in the PNG.

        Arguments:
            value: measurement coordinate
        Returns:
            raster column
        """
        return _AXIS_PADDING + round((value - first) * track_width / (last - first))

    urls = []
    for theme, (ink, border) in enumerate(
        (("#323b45", "#a3aab3"), ("#e0e5ec", "#87919f"))
    ):
        image = Image.new("RGBA", image_size)
        draw = ImageDraw.Draw(image)
        left, right = position(first), position(last)
        draw.rectangle(
            (left - 1, _TRACK_TOP - 1, right, _TRACK_BOTTOM + 1), outline=border
        )
        for kind, _, lower, upper in bands:
            start, stop = first, last
            if lower is not None:
                start = max(first, lower)
            if upper is not None:
                stop = min(last, upper + 1)
            if start < stop:
                x1 = min(right - 1, position(start))
                x2 = max(x1, position(stop) - 1)
                draw.rectangle(
                    (x1, _TRACK_TOP, x2, _TRACK_BOTTOM), fill=colors[kind][theme]
                )
                if reading is not None and start > first:
                    draw.line((x1, _TRACK_TOP - 3, x1, _TRACK_BOTTOM + 3), fill=ink)
        for tick in ticks:
            x = position(tick)
            draw.text((x, 4), f"{tick}", font=font, fill=ink, anchor="mt")
            draw.line((x, 34, x, _TRACK_TOP - 1), fill=ink, width=2)
        if reading is not None:
            x = position(reading + 0.5)
            draw.polygon(((x, 63), (x - 9, 75), (x + 9, 75)), fill=ink)
            draw.text((x, 80), f"{reading} px", font=font, fill=ink, anchor="mt")
        urls.append(get_png_data_url(image))
    return NumberLineImage(width, height, urls[0], urls[1])


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
