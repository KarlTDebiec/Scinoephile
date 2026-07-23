#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of image bbox extraction."""

from __future__ import annotations

from PIL import Image, ImageDraw

from scinoephile.image.bbox import Bbox
from scinoephile.image.bboxes import get_bboxes


def test_get_bboxes_merges_line_components_at_minimum_gap():
    """Test component lines separated by the minimum gap are grouped together."""
    img = _make_mask_img(
        size=(10, 70),
        rects=[
            (2, 0, 7, 4),
            (2, 10, 7, 64),
        ],
    )

    assert get_bboxes(img) == [Bbox(x1=2, x2=8, y1=0, y2=65)]


def test_get_bboxes_preserves_full_height_lines_at_minimum_gap():
    """Test full-height lines separated by the minimum gap remain separate."""
    img = _make_mask_img(
        size=(10, 70),
        rects=[
            (2, 0, 7, 29),
            (2, 35, 7, 64),
        ],
    )

    assert get_bboxes(img) == [
        Bbox(x1=2, x2=8, y1=0, y2=30),
        Bbox(x1=2, x2=8, y1=35, y2=65),
    ]


def test_get_bboxes_preserves_chained_small_line_merges():
    """Test chained line merges preserve all accumulated stroke bands."""
    img = _make_mask_img(
        size=(10, 60),
        rects=[
            (2, 0, 7, 4),
            (2, 9, 7, 13),
            (2, 18, 7, 54),
        ],
    )

    assert get_bboxes(img) == [Bbox(x1=2, x2=8, y1=0, y2=55)]


def _make_mask_img(
    size: tuple[int, int], rects: list[tuple[int, int, int, int]]
) -> Image.Image:
    """Build a transparent LA image with white inclusive rectangles.

    Arguments:
        size: image size
        rects: rectangle bounds to draw
    Returns:
        image with white mask rectangles
    """
    img = Image.new("LA", size, (0, 0))
    draw = ImageDraw.Draw(img)
    for rect in rects:
        draw.rectangle(rect, fill=(255, 255))
    return img
