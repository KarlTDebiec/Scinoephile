#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Data class for a pair of characters."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.text import get_char_type, whitespace_chars
from scinoephile.image.bbox import Bbox

__all__ = ["CharPair", "get_char_pairs"]


@dataclass(slots=True)
class CharPair:
    """Data class for a pair of characters."""

    char_1: str
    """First character."""
    char_2: str
    """Second character."""
    width_1: int
    """Width of the first character."""
    width_2: int
    """Width of the second character."""
    gap: int
    """Gap between the two characters."""
    whitespace: str
    """Whitespace between the two characters."""

    @property
    def type_1(self) -> str:
        """Type of the first character."""
        return get_char_type(self.char_1)

    @property
    def type_2(self) -> str:
        """Type of the second character."""
        return get_char_type(self.char_2)


def get_char_pairs(
    text: str,
    bboxes: list[Bbox],
) -> list[CharPair]:
    """Build character pairs from text and bboxes.

    Arguments:
        text: subtitle text
        bboxes: bounding boxes for each non-whitespace character
    Returns:
        List of character pairs
    """
    bbox_widths = [bbox.width for bbox in bboxes]
    bbox_gaps = [bboxes[i + 1].x1 - bboxes[i].x2 for i in range(len(bboxes) - 1)]

    char_1_i = 0
    width_1_i = 0
    gap_i = 0
    char_pairs = []
    while True:
        if char_1_i > len(text) - 2:
            break

        char_1 = text[char_1_i]
        width_1 = bbox_widths[width_1_i]

        char_2_i = char_1_i + 1
        width_2_i = width_1_i + 1
        width_2 = bbox_widths[width_2_i]

        gap_whitespace = ""
        while char_2_i < len(text):
            char_2 = text[char_2_i]
            if char_2 in whitespace_chars:
                gap_whitespace += char_2
                char_2_i += 1
                continue
            break

        char_2 = text[char_2_i]
        gap = bbox_gaps[gap_i]
        pair = CharPair(char_1, char_2, width_1, width_2, gap, gap_whitespace)
        char_pairs.append(pair)

        char_1_i = char_2_i
        width_1_i = width_2_i
        gap_i += 1

    return char_pairs
