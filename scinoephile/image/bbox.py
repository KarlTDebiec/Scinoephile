#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to character bounding boxes."""

from __future__ import annotations

from PIL import Image, ImageChops

__all__ = ["get_bbox"]


def get_bbox(img: Image.Image) -> tuple[int, int, int, int] | None:
    """Get bbox of non-white/transparent pixels in an image.

    Arguments:
        img: Image
    Returns:
        bbox of non-white/transparent pixels, or None if no pixels found
    """
    img_l = img if img.mode == "L" else img.convert("L")
    mask = ImageChops.invert(img_l).point(lambda p: p > 0 and 255)
    bbox = mask.getbbox()
    return bbox
