#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to drawing."""

from __future__ import annotations

import colorsys

import numpy as np
from PIL import Image, ImageDraw

from scinoephile.image.bbox import Bbox

__all__ = [
    "get_img_with_bboxes",
    "get_white_mask",
]


def get_img_with_bboxes(img: Image.Image, bboxes: list[Bbox]) -> Image.Image:
    """Draw bounding boxes on an image with rainbow colors for debugging.

    Arguments:
        img: reference image
        bboxes: bounding boxes to draw
    Returns:
        image with bounding boxes drawn.
    """
    img_with_bboxes = img.convert("RGBA")
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
        draw.rectangle(
            [bbox.x1, bbox.y1, bbox.x2, bbox.y2],
            outline=palette[i],
            width=1,
        )

    return img_with_bboxes


def get_white_mask(
    grayscale: np.ndarray,
    alpha: np.ndarray,
    fill_color: int,
) -> np.ndarray:
    """Get a white interior mask from grayscale/alpha arrays.

    Arguments:
        grayscale: grayscale values
        alpha: alpha values
        fill_color: fill color used in rendering
    Returns:
        boolean mask of white interior pixels
    """
    tolerance = 10
    lower = max(0, fill_color - tolerance)
    upper = min(255, fill_color + tolerance)
    return (alpha > 0) & (grayscale >= lower) & (grayscale <= upper)
