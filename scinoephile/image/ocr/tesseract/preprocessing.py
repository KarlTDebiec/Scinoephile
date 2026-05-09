#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image preprocessing for Tesseract OCR."""

from __future__ import annotations

from PIL import Image

__all__ = ["preprocess_tesseract_ocr_image"]


def preprocess_tesseract_ocr_image(
    image: Image.Image, *, scale: int = 2
) -> Image.Image:
    """Preprocess an image before Tesseract recognition.

    Arguments:
        image: input subtitle image
        scale: integer resize multiplier
    Returns:
        RGB image with black text on an opaque white background
    Raises:
        ValueError: if scale is less than one
    """
    if scale < 1:
        raise ValueError("scale must be at least 1")

    rgba_image = image.convert("RGBA")
    one_color = Image.new("RGBA", rgba_image.size, (0, 0, 0, 0))
    alpha = rgba_image.getchannel("A")
    one_color.paste((0, 0, 0, 255), mask=alpha)

    white_background = Image.new("RGBA", rgba_image.size, (255, 255, 255, 255))
    white_background.alpha_composite(one_color)
    rgb_image = white_background.convert("RGB")
    if scale == 1:
        return rgb_image

    return rgb_image.resize(
        (rgb_image.width * scale, rgb_image.height * scale),
        Image.Resampling.NEAREST,
    )
