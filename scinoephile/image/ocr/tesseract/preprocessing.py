#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image preprocessing for Tesseract OCR."""

from __future__ import annotations

from PIL import Image, ImageChops

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
    luminance = rgba_image.convert("L")
    alpha = rgba_image.getchannel("A")
    luminance_mask = luminance.point(lambda value: 255 if value >= 96 else 0)
    alpha_mask = alpha.point(lambda value: 255 if value >= 10 else 0)
    fill_mask = ImageChops.multiply(luminance_mask, alpha_mask)

    rgb_image = Image.new("RGB", rgba_image.size, (255, 255, 255))
    rgb_image.paste((0, 0, 0), mask=fill_mask)
    if scale == 1:
        return rgb_image

    return rgb_image.resize(
        (rgb_image.width * scale, rgb_image.height * scale),
        Image.Resampling.NEAREST,
    )
