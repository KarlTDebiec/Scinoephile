#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Tesseract OCR image preprocessing."""

from __future__ import annotations

from PIL import Image

from scinoephile.image.ocr.tesseract.preprocessing import (
    preprocess_tesseract_ocr_image,
)


def test_preprocess_tesseract_ocr_image_makes_opaque_white_background():
    """Test Tesseract preprocessing composites transparency onto white."""
    image = Image.new("RGBA", (4, 3), (0, 0, 0, 0))
    image.putpixel((1, 1), (220, 220, 220, 255))

    preprocessed = preprocess_tesseract_ocr_image(image)

    assert preprocessed.mode == "RGB"
    assert preprocessed.size == (8, 6)
    assert preprocessed.getpixel((0, 0)) == (255, 255, 255)
    assert preprocessed.getpixel((2, 2)) == (0, 0, 0)


def test_preprocess_tesseract_ocr_image_discards_dark_outline():
    """Test Tesseract preprocessing keeps bright fill and discards dark outline."""
    image = Image.new("RGBA", (3, 1), (0, 0, 0, 0))
    image.putpixel((0, 0), (15, 15, 15, 255))
    image.putpixel((1, 0), (20, 30, 40, 255))
    image.putpixel((2, 0), (220, 220, 220, 255))

    preprocessed = preprocess_tesseract_ocr_image(image, scale=1)

    assert preprocessed.getpixel((0, 0)) == (255, 255, 255)
    assert preprocessed.getpixel((1, 0)) == (255, 255, 255)
    assert preprocessed.getpixel((2, 0)) == (0, 0, 0)


def test_preprocess_tesseract_ocr_image_supports_scale_one():
    """Test Tesseract preprocessing can preserve source dimensions."""
    image = Image.new("RGBA", (4, 3), (255, 255, 255, 0))

    preprocessed = preprocess_tesseract_ocr_image(image, scale=1)

    assert preprocessed.size == (4, 3)
