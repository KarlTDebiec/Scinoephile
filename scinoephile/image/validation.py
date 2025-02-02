#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to OCR validation."""
from __future__ import annotations

from logging import info
from pathlib import Path

from PIL import Image

from scinoephile.common.validation import validate_output_directory
from scinoephile.image.image_series import ImageSeries


def validate_ocr(series: ImageSeries, output_path: Path) -> None:
    """Validates the OCR of an image series.

    Arguments:
        series: Series to validate
        output_path: Directory in which to save validation results
    """
    output_path = validate_output_directory(output_path)

    for i, event in enumerate(series.events, 1):
        img = event.image_stack
        resized = img.resize((img.width * 4, img.height * 4), Image.NEAREST)  # noqa
        resized.save(output_path / f"{i:04d}.png")
        info(f"Saved {output_path / f'{i:04d}.png'}")
