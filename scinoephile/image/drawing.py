#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to drawing."""

from __future__ import annotations

import colorsys

import numpy as np
from PIL import Image, ImageDraw

from .bbox import Bbox
from .colors import (
    get_fill_and_outline_colors,
    get_fill_color_mask_arr,
    get_grayscale_and_alpha_arrs,
)

__all__ = [
    "convert_rgba_img_to_la",
    "get_img_with_bboxes",
]


def convert_rgba_img_to_la(img: Image.Image) -> tuple[Image.Image, bool]:
    """Convert RGBA images with grayscale color channels to LA.

    Arguments:
        img: Image to convert
    Returns:
        Image and whether it was converted
    """
    if img.mode != "RGBA":
        return img, False
    arr = np.array(img)
    if np.all(arr[:, :, 0] == arr[:, :, 1]) and np.all(arr[:, :, 1] == arr[:, :, 2]):
        return img.convert("LA"), True
    return img, False


def get_img_with_bboxes(
    img: Image.Image, bboxes: list[Bbox], use_fill_mask: bool = True
) -> Image.Image:
    """Draw bounding boxes on a 2x image with rainbow colors for debugging.

    Arguments:
        img: reference image
        bboxes: bounding boxes to draw
        use_fill_mask: whether to draw on an inverted fill-color mask
    Returns:
        2x image with bounding boxes drawn
    """
    resample = getattr(Image, "Resampling", Image).NEAREST
    if use_fill_mask:
        grayscale, alpha = get_grayscale_and_alpha_arrs(img)
        fill_color, _outline = get_fill_and_outline_colors(grayscale, alpha)
        fill_mask = get_fill_color_mask_arr(grayscale, alpha, fill_color)
        inverted_mask = np.logical_not(fill_mask).astype(np.uint8) * 255
        mask_img = Image.fromarray(inverted_mask, mode="L")
        base_img = mask_img.convert("RGBA")
    else:
        base_img = img.convert("RGBA")

    img_with_bboxes = base_img.resize(
        (img.width * 2, img.height * 2),
        resample=resample,
    )
    draw = ImageDraw.Draw(img_with_bboxes)

    # Generate palette
    palette = [
        tuple(
            int(c * 255)
            for c in np.array(colorsys.hsv_to_rgb(i / len(bboxes), 1.0, 1.0))
        )
        for i in range(len(bboxes))
    ]

    # Draw boxes
    for i, bbox in enumerate(bboxes):
        x1 = bbox.x1 * 2
        y1 = bbox.y1 * 2
        x2 = bbox.x2 * 2 - 1
        y2 = bbox.y2 * 2 - 1
        draw.rectangle(
            [x1, y1, x2, y2],
            outline=palette[i],
            width=1,
        )

    return img_with_bboxes
