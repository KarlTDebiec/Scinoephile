#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to character bounding boxes."""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageChops


def get_bbox(img: Image.Image) -> tuple[int, int, int, int]:
    """Get bbox of non-white/transparent pixels in an image.

    Arguments:
        img: Image
    Returns:
        bbox of non-white/transparent pixels
    """
    img_l = img if img.mode == "L" else img.convert("L")
    mask = ImageChops.invert(img_l).point(lambda p: p > 0 and 255)
    bbox = mask.getbbox()
    return bbox


def get_char_bboxes(img: Image.Image) -> list[tuple[int, int, int, int]]:
    """Get character bboxes within an image.

    Arguments:
        img: Image
    Returns:
        Character bounding boxes [(x1, y1, x2, y2), ...]
    """
    if img.mode != "L":
        raise ValueError("Image must be of mode 'L'")

    arr = np.array(img)

    # Split over x-axis into sections separated by white space
    sections = []
    section = None
    for i, nonwhite_pixels in enumerate(np.sum(arr < 255, axis=0)):
        if nonwhite_pixels > 0:
            if section is None:
                section = [i, i]
            else:
                section[1] = i
        elif section is not None:
            sections.append(section)
            section = None
    if section is not None:
        sections.append(section)

    # Determine top and bottom of each section to get final bbox
    bboxes = []
    for x1, x2 in sections:
        section = arr[:, x1:x2]
        nonwhite_pixels = np.sum(section < 255, axis=1)
        y1 = int(np.argmax(nonwhite_pixels > 0))
        y2 = int(len(nonwhite_pixels) - np.argmax(nonwhite_pixels[::-1] > 0) - 1)
        bboxes.append((x1, y1, x2, y2))

    # Clean up bboxes
    bboxes = _merge_split_hanzi_bboxes(bboxes)
    bboxes = _merge_ellipsis_bboxes(bboxes)

    return bboxes


def _merge_ellipsis_bboxes(
    bboxes: list[tuple[int, int, int, int]],
    max_size: int = 30,
    max_spacing: int = 11,
) -> list[tuple[int, int, int, int]]:
    """Identify ellipsis and merge their bounding boxes.

    Arguments:
        bboxes: Nascent list of bounding boxes [(x1, y1, x2, y2), ...]
        max_size: Max width and height for a box to be considered part of an ellipse
        max_spacing: Max allowed gap between dots in an ellipse
    Returns:
        bboxes with ellipsis merged
    """
    merged_bboxes = []
    i = 0
    while i < len(bboxes):
        # Check if ellipsis
        if i <= len(bboxes) - 3:
            b1x1, b1y1, b1x2, b1y2 = bboxes[i]
            b2x1, b2y1, b2x2, b2y2 = bboxes[i + 1]
            b3x1, b3y1, b3x2, b3y2 = bboxes[i + 2]

            # If ellipsis, merge
            if (
                max(b1x2 - b1x1, b1y2 - b1y1) <= max_size
                and max(b2x2 - b2x1, b2y2 - b2y1) <= max_size
                and max(b3x2 - b3x1, b3y2 - b3y1) <= max_size
                and abs(b2x1 - b1x2) <= max_spacing
                and abs(b3x1 - b2x2) <= max_spacing
            ):
                merged_bboxes.append(
                    (b1x1, min(b1y1, b2y1, b3y1), b3x2, max(b1y2, b2y2, b3y2))
                )
                i += 3
                continue

        # If not ellipsis, keep as is
        merged_bboxes.append(bboxes[i])
        i += 1

    return merged_bboxes


def _merge_split_hanzi_bboxes(
    bboxes: list[tuple[int, int, int, int]],
    min_aspect_ratio: float = 1.41,
    max_gap: int = 8,
) -> list[tuple[int, int, int, int]]:
    """Identify split hanzi and merge their bounding boxes.

    Arguments:
        bboxes: Nascent list of bboxes [(x1, y1, x2, y2), ...]
        min_aspect_ratio: Min aspect ratio to be considered part of split hanzi
        max_gap: Max gap between halves to be considered part of split hanzi
    Returns:
        bboxes with split hanzi merged
    """
    merged_bboxes = []
    i = 0
    while i < len(bboxes):
        # Check if split hanzi
        if i <= len(bboxes) - 2:
            b1x1, b1y1, b1x2, b1y2 = bboxes[i]
            b2x1, b2y1, b2x2, b2y2 = bboxes[i + 1]

            b1_aspect_ratio = (b1y2 - b1y1) / max(b1x2 - b1x1, 1)
            b2_aspect_ratio = (b2y2 - b2y1) / max(b2x2 - b2x1, 1)
            b1_b2_gap = abs(b2x1 - b1x2)

            # If split hanzi, merge
            if (
                b1_aspect_ratio >= min_aspect_ratio
                and b2_aspect_ratio >= min_aspect_ratio
                and b1_b2_gap <= max_gap
            ):
                merged_bboxes.append((b1x1, min(b1y1, b2y1), b2x2, max(b1y2, b2y2)))
                i += 2
                continue

        # If not split hanzi, keep as is
        merged_bboxes.append(bboxes[i])
        i += 1

    return merged_bboxes
