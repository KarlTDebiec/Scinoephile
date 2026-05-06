#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of PaddleOCR image preprocessing."""

from __future__ import annotations

from PIL import Image

from scinoephile.image.ocr.paddle.preprocessing import preprocess_paddle_ocr_image


def test_preprocess_paddle_ocr_image_adds_subtitleedit_double_border():
    """Test PaddleOCR preprocessing adds SubtitleEdit-style double border."""
    image = Image.new("RGBA", (12, 8), (255, 255, 255, 0))

    preprocessed = preprocess_paddle_ocr_image(image, border=10)

    assert preprocessed.mode == "RGBA"
    assert preprocessed.size == (52, 48)
    assert preprocessed.getpixel((5, 5)) == (0, 0, 0, 0)
    assert preprocessed.getpixel((15, 15)) == (0, 0, 0, 255)
