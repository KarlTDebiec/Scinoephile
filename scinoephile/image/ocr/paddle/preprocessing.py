#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image preprocessing for PaddleOCR."""

from __future__ import annotations

from PIL import Image

__all__ = ["preprocess_paddle_ocr_image"]


def preprocess_paddle_ocr_image(image: Image.Image, border: int = 10) -> Image.Image:
    """Preprocess an image before PaddleOCR recognition.

    Arguments:
        image: input subtitle image
        border: transparent border width to add
    Returns:
        preprocessed image
    """
    rgba_image = image.convert("RGBA")
    if border <= 0:
        return rgba_image

    # Border preprocessing is adapted from SubtitleEdit's PaddleOCR workflow.
    total_border = border * 2
    preprocessed = Image.new(
        "RGBA",
        (
            rgba_image.width + 2 * total_border,
            rgba_image.height + 2 * total_border,
        ),
        (0, 0, 0, 0),
    )
    inner_border = Image.new(
        "RGBA",
        (preprocessed.width - 2 * border, preprocessed.height - 2 * border),
        (0, 0, 0, 255),
    )
    preprocessed.paste(inner_border, (border, border))
    preprocessed.paste(rgba_image, (total_border, total_border), rgba_image)
    return preprocessed
