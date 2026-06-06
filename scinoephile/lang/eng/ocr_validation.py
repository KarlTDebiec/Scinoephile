#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English OCR validation."""

from __future__ import annotations

from pathlib import Path

from scinoephile.image.ocr.validation import ValidationManager
from scinoephile.image.subtitles import ImageSeries

__all__ = ["validate_eng_ocr"]


def validate_eng_ocr(
    series: ImageSeries,
    validation_manager: ValidationManager | None = None,
    *,
    cache_dir_path: Path | str | None = None,
    dev: bool = False,
) -> ImageSeries:
    """Validate OCR text against image series images.

    Arguments:
        series: ImageSeries to validate
        validation_manager: validation manager to use, if already configured
        cache_dir_path: cache directory for local OCR validation data
        dev: whether to write validation data updates to the repo
    Returns:
        validated image subtitle series
    """
    if validation_manager is None:
        validation_manager = ValidationManager(cache_dir_path=cache_dir_path, dev=dev)
    return validation_manager.validate(series)
