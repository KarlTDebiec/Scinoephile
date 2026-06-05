#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of image drawing utilities."""

from __future__ import annotations

from PIL import Image

from scinoephile.image.bbox import Bbox
from scinoephile.image.drawing import get_img_with_bboxes


def test_get_img_with_bboxes_draws_second_outline_pixel_outside():
    """Test bbox outlines are thickened outside the original bbox."""
    img = Image.new("LA", (5, 5), (50, 255))
    result = get_img_with_bboxes(img, [Bbox(x1=1, x2=4, y1=1, y2=4)])

    assert result.getpixel((1, 1)) == (255, 0, 0, 255)
    assert result.getpixel((2, 2)) == (255, 0, 0, 255)
    assert result.getpixel((3, 3)) == (50, 50, 50, 255)
