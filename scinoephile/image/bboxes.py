#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Bounding box utilities."""

from __future__ import annotations

import numpy as np
from PIL import Image

from .bbox import Bbox
from .colors import get_fill_and_outline_colors, get_grayscale_and_alpha, get_white_mask

__all__ = [
    "get_bboxes",
    "get_merged_bbox",
]

def get_bboxes(img: Image.Image) -> list[Bbox]:
    """Get raw bboxes from white interior pixels.

    Arguments:
        img: subtitle for which to get bboxes
    Returns:
        raw bboxes
    """
    grayscale, alpha = get_grayscale_and_alpha(img)
    fill_color, _outline = get_fill_and_outline_colors(grayscale, alpha)
    white_mask = get_white_mask(grayscale, alpha, fill_color)

    # Determine top and bottom of each line separated by whitespace
    lines = []
    line = None
    for i, white_pixels in enumerate(np.sum(white_mask, axis=1)):
        if white_pixels > 0:
            if line is None:
                line = [i, i]
            else:
                line[1] = i
        elif line is not None:
            lines.append(line)
            line = None
    if line is not None:
        lines.append(line)

    min_line_gap = 10
    if lines:
        merged_lines = [lines[0]]
        for y1, y2 in lines[1:]:
            last = merged_lines[-1]
            if y1 - last[1] < min_line_gap:
                last[1] = max(last[1], y2)
            else:
                merged_lines.append([y1, y2])
        lines = merged_lines

    # Determine left and right of each section per line to get final bbox
    bboxes: list[Bbox] = []
    for y1, y2 in lines:
        line_mask = white_mask[y1:y2]
        sections = []
        section = None
        for i, white_pixels in enumerate(np.sum(line_mask, axis=0)):
            if white_pixels > 0:
                if section is None:
                    section = [i, i]
                else:
                    section[1] = i
            elif section is not None:
                sections.append(section)
                section = None
        if section is not None:
            sections.append(section)

        for x1, x2 in sections:
            section_mask = line_mask[:, x1:x2]
            white_pixels = np.sum(section_mask, axis=1)
            if np.max(white_pixels) == 0:
                continue
            section_y1 = int(np.argmax(white_pixels > 0))
            section_y2 = int(len(white_pixels) - np.argmax(white_pixels[::-1] > 0) - 1)
            bboxes.append(
                Bbox(
                    x1=x1,
                    x2=x2,
                    y1=y1 + section_y1,
                    y2=y1 + section_y2,
                )
            )

    return bboxes


def get_merged_bbox(bboxes: list[Bbox]) -> Bbox:
    """Get merged bbox and dims tuple from bboxes.

    Arguments:
        bboxes: bboxes to merge
    Returns:
        merged bbox and dims tuple
    """
    return Bbox(
        x1=min(bbox.x1 for bbox in bboxes),
        x2=max(bbox.x2 for bbox in bboxes),
        y1=min(bbox.y1 for bbox in bboxes),
        y2=max(bbox.y2 for bbox in bboxes),
    )
