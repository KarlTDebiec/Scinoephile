#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English OCR validation."""

from __future__ import annotations

from scinoephile.image.ocr.validation import ValidationManager
from scinoephile.image.subtitles import ImageSeries

__all__ = ["validate_eng_ocr"]


def validate_eng_ocr(
    series: ImageSeries,
    dev: bool = False,
) -> ImageSeries:
    """Validate OCR text against image series images.

    Arguments:
        series: ImageSeries to validate
        dev: whether to write validation data updates to the repo
    Returns:
        validated image subtitle series
    """
    validation_mgr = ValidationManager(dev=dev)
    return validation_mgr.validate(series)
