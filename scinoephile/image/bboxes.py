#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Bounding box utilities."""

from __future__ import annotations

import numpy as np
from PIL import Image

from .bbox import Bbox
from .colors import (
    get_fill_and_outline_colors,
    get_fill_color_mask_arr,
    get_grayscale_and_alpha_arrs,
)

__all__ = [
    "get_bboxes",
    "get_merged_bbox",
]


def get_bboxes(img: Image.Image) -> list[Bbox]:  # noqa: PLR0912, PLR0915
    """Get bboxes surrounding the fill color interiors of characters in an image.

    First attempts to split the image into multiple lines of text, if applicable.
    Then splits each line into bboxes horizontally, and fits the top and bottom.
    Note that characters with vertical gaps such as ":" have one bbox.

    Arguments:
        img: subtitle image to analyze
    Returns:
        bboxes
    """
    grayscale, alpha = get_grayscale_and_alpha_arrs(img)
    fill_color, _outline = get_fill_and_outline_colors(grayscale, alpha)
    white_mask = get_fill_color_mask_arr(grayscale, alpha, fill_color)

    # Determine top and bottom of each line separated by whitespace
    lines = []
    line = None
    for i, white_pixels in enumerate(np.sum(white_mask, axis=1)):
        if white_pixels > 0:
            if line is None:
                line = [i, i + 1]
            else:
                line[1] = i + 1
        elif line is not None:
            lines.append(line)
            line = None
    if line is not None:
        lines.append(line)

    min_line_gap = 5
    min_line_height = 30
    final_lines = lines
    if lines:
        merge_dirs: list[str | None] = [None] * len(lines)
        for idx, (y1, y2) in enumerate(lines):
            if (y2 - y1) >= min_line_height:
                continue
            prev_gap = y1 - lines[idx - 1][1] if idx > 0 else None
            next_gap = lines[idx + 1][0] - y2 if idx + 1 < len(lines) else None
            if prev_gap is None and next_gap is None:
                continue
            if prev_gap is None:
                merge_dirs[idx] = "down"
            elif next_gap is None:
                merge_dirs[idx] = "up"
            elif next_gap <= prev_gap:
                merge_dirs[idx] = "down"
            else:
                merge_dirs[idx] = "up"

        for idx, direction in enumerate(merge_dirs):
            if direction == "up" and idx > 0:
                lines[idx - 1][1] = max(lines[idx - 1][1], lines[idx][1])
                lines[idx] = None
            elif direction == "down" and idx + 1 < len(lines):
                lines[idx + 1][0] = min(lines[idx + 1][0], lines[idx][0])
                lines[idx + 1][1] = max(lines[idx + 1][1], lines[idx][1])
                lines[idx] = None

        merged_lines: list[list[int]] = []
        for line in lines:
            if line is None:
                continue
            if merged_lines and line[0] - merged_lines[-1][1] < min_line_gap:
                merged_lines[-1][1] = max(merged_lines[-1][1], line[1])
            else:
                merged_lines.append(line)
        final_lines = merged_lines

    # Determine left and right of each section per line to get final bbox
    bboxes: list[Bbox] = []
    for y1, y2 in final_lines:
        line_mask = white_mask[y1:y2]
        sections = []
        section = None
        for i, white_pixels in enumerate(np.sum(line_mask, axis=0)):
            if white_pixels > 0:
                if section is None:
                    section = [i, i + 1]
                else:
                    section[1] = i + 1
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
            section_y2 = (
                int(len(white_pixels) - np.argmax(white_pixels[::-1] > 0) - 1) + 1
            )
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
    """Get merged bbox from a list of bboxes.

    Arguments:
        bboxes: bboxes to merge
    Returns:
        merged bbox
    """
    return Bbox(
        x1=min(bbox.x1 for bbox in bboxes),
        x2=max(bbox.x2 for bbox in bboxes),
        y1=min(bbox.y1 for bbox in bboxes),
        y2=max(bbox.y2 for bbox in bboxes),
    )
