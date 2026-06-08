#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English OCR validation."""

from __future__ import annotations

from scinoephile.core import ScinoephileError
from scinoephile.image.ocr.validation import ValidationManager
from scinoephile.image.subtitles import ImageSeries

__all__ = ["validate_eng_ocr"]


def validate_eng_ocr(
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
    try:
        if validation_manager is None:
            validation_manager = ValidationManager()
        return validation_manager.validate(series)
    except ScinoephileError:
        raise
    except (OSError, ValueError) as exc:
        raise ScinoephileError(str(exc)) from exc
