#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese OCR validation helpers."""

from __future__ import annotations

from pathlib import Path

from scinoephile.image.ocr import ValidationManager
from scinoephile.image.subtitles import ImageSeries

__all__ = ["validate_zho_ocr"]


def validate_zho_ocr(
    series: ImageSeries,
    stop_at_idx: int | None = None,
    interactive: bool = False,
    output_dir_path: Path | str | None = None,
) -> ImageSeries:
    """Validate OCR text against image series images.

    Arguments:
        series: ImageSeries to validate
        stop_at_idx: stop processing at this index
        interactive: whether to prompt user for confirmations
        output_dir_path: directory in which to save validation images
    """
    validation_mgr = ValidationManager(tab="　　")
    output_series = validation_mgr.validate(series, stop_at_idx, interactive)

    if output_dir_path is not None:
        output_series.save(output_dir_path)
    return output_series
