#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow helpers for validating OCR against image subtitles."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.image.ocr.validation import ValidationManager
from scinoephile.image.subtitles import ImageSeries

__all__ = ["validate_ocr"]

logger = getLogger(__name__)


def validate_ocr(
    source: Path | ImageSeries,
    outfile_path: Path,
    *,
    cache_dir_path: Path | str | None = None,
    interactive: bool = False,
    dev: bool = False,
    overwrite: bool = False,
) -> Series:
    """Validate OCR text from image subtitles.

    Arguments:
        source: image subtitle input path or image series
        outfile_path: validated subtitle output path
        cache_dir_path: cache directory for local OCR validation data
        interactive: whether to request interactive validation
        dev: whether validation should write data updates to repo data
        overwrite: whether to overwrite existing validation output
    Returns:
        validated subtitle series
    """
    if outfile_path.exists() and not overwrite:
        logger.info(f"Validated OCR output exists: {outfile_path}")
        return Series.load(outfile_path)

    try:
        if interactive:
            raise ScinoephileError(
                "Interactive OCR validation is not available in this workflow"
            )

        if isinstance(source, ImageSeries):
            image_series = source
        else:
            image_series = ImageSeries.load(source)
        validation_manager = ValidationManager(cache_dir_path=cache_dir_path, dev=dev)
        validated = validation_manager.validate(image_series, interactive=False)
        validated.save(outfile_path, format_="srt", exist_ok=True)
        return Series.load(outfile_path)
    except ScinoephileError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise ScinoephileError(f"Unable to validate OCR: {exc}") from exc
