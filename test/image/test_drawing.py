#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of image drawing utilities."""

from __future__ import annotations

from PIL import Image

from scinoephile.image.bbox import Bbox
from scinoephile.image.drawing import convert_rgba_img_to_la, get_img_with_bboxes


def test_convert_rgba_img_to_la_converts_grayscale_rgba_image():
    """Test grayscale RGBA images are returned in LA mode."""
    img = Image.new("RGBA", (2, 2), (64, 64, 64, 128))

    result = convert_rgba_img_to_la(img)

    assert result.mode == "LA"
    assert result.getpixel((0, 0)) == (64, 128)


def test_convert_rgba_img_to_la_preserves_color_rgba_image():
    """Test color RGBA images are returned unchanged."""
    img = Image.new("RGBA", (2, 2), (64, 32, 16, 128))

    result = convert_rgba_img_to_la(img)

    assert result is img


def test_get_img_with_bboxes_draws_second_outline_pixel_outside():
    """Test bbox outlines are thickened outside the original bbox."""
    img = Image.new("LA", (5, 5), (50, 255))
    result = get_img_with_bboxes(img, [Bbox(x1=1, x2=4, y1=1, y2=4)])
    background = (50, 50, 50, 255)

    assert result.getpixel((1, 1)) != background
    assert result.getpixel((2, 2)) != background
    assert result.getpixel((3, 3)) == background
