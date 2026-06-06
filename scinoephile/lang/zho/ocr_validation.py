#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to standard Chinese OCR validation."""

from __future__ import annotations

from scinoephile.image.ocr.validation import ValidationManager
from scinoephile.image.subtitles import ImageSeries

__all__ = ["validate_zho_ocr"]


def validate_zho_ocr(
    series: ImageSeries,
    validation_manager: ValidationManager | None = None,
) -> ImageSeries:
    """Validate OCR text against image series images.

    Arguments:
        series: ImageSeries to validate
        validation_manager: validation manager to use, if already configured
    Returns:
        validated image subtitle series
    """
    if validation_manager is None:
        validation_manager = ValidationManager()
    return validation_manager.validate(series)
