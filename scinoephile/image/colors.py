#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Color utilities for images."""

from __future__ import annotations

import numpy as np

from scinoephile.core import ScinoephileError

__all__ = [
    "get_fill_and_outline_colors",
    "get_fill_and_outline_colors_from_hist",
    "get_grayscale_and_alpha",
]


def get_grayscale_and_alpha(img) -> tuple[np.ndarray, np.ndarray]:
    """Get grayscale and alpha arrays for an image.

    Arguments:
        img: Image from which to extract grayscale and alpha
    Returns:
        Grayscale values and alpha mask
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
