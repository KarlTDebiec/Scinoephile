#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Color utilities for images."""

from __future__ import annotations

import numpy as np
from PIL import Image

from scinoephile.core import ScinoephileError

__all__ = [
    "get_fill_and_outline_colors",
    "get_fill_and_outline_colors_from_hist",
    "get_grayscale_and_alpha_arrs",
    "get_fill_color_mask_arr",
]


def get_grayscale_and_alpha_arrs(img: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    """Get arrays of grayscale and alpha channels of an Image in LA, L, or RGBA mode.

    Arguments:
        img: Image from which to extract grayscale and alpha
    Returns:
        grayscale values and alpha mask
    """
    arr = np.array(img)
    if img.mode == "LA":
        return arr[:, :, 0], arr[:, :, 1]
    if img.mode == "L":
        alpha = np.ones(arr.shape, dtype=np.uint8) * 255
        return arr, alpha
    if img.mode == "RGBA":
        rgb = arr[:, :, :3].astype(np.float32)
        grayscale = (
            0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
        ).astype(np.uint8)
        alpha = arr[:, :, 3]
        return grayscale, alpha
    raise ScinoephileError(
        f"Unsupported image mode '{img.mode}' for grayscale and alpha extraction."
    )


def get_fill_color_mask_arr(
    grayscale: np.ndarray,
    alpha: np.ndarray,
    fill_color: int,
) -> np.ndarray:
    """Get a boolean mask array that is true for pixels close to a provided fill color.

    Arguments:
        grayscale: grayscale values
        alpha: alpha values
        fill_color: fill color
    Returns:
        boolean mask array that is true for pixels close to the provided fill color
    """
    tolerance = 10
    lower = max(0, fill_color - tolerance)
    upper = min(255, fill_color + tolerance)
    return (alpha > 0) & (grayscale >= lower) & (grayscale <= upper)


def get_fill_and_outline_colors(
    grayscale: np.ndarray,
    alpha: np.ndarray,
) -> tuple[int, int]:
    """Get fill and outline grayscale values from grayscale/alpha arrays.

    Arguments:
        grayscale: grayscale values
        alpha: alpha values
    Returns:
        Fill and outline grayscale values
    """
    mask = alpha != 0
    values = grayscale[mask]
    if values.size == 0:
        return 255, 0
    hist = np.bincount(values, minlength=256)
    return get_fill_and_outline_colors_from_hist(hist)


def get_fill_and_outline_colors_from_hist(hist: np.ndarray) -> tuple[int, int]:
    """Get fill and outline grayscale values from a histogram.

    Arguments:
        hist: grayscale histogram
    Returns:
        Fill and outline grayscale values
    """
    if hist.size == 0 or np.sum(hist) == 0:
        return 255, 0
    fill, outline = map(int, np.argsort(hist)[-2:])
    if outline > fill:
        fill, outline = outline, fill
    return fill, outline
