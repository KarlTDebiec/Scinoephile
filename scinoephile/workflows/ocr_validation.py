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
    infile_path: Path,
    outfile_path: Path,
    *,
    cache_dir_path: Path | str | None = None,
    dev: bool = False,
    overwrite: bool = False,
) -> Series:
    """Validate OCR text from an image subtitle input path.

    Arguments:
        infile_path: image subtitle input path
        outfile_path: validated subtitle output path
        cache_dir_path: cache directory for local OCR validation data
        dev: whether validation should write data updates to repo data
        overwrite: whether to overwrite existing validation output
    Returns:
        validated subtitle series
    """
    if outfile_path.exists() and not overwrite:
        logger.info(f"Validated OCR output exists: {outfile_path}")
        return Series.load(outfile_path)

    try:
        image_series = ImageSeries.load(infile_path)
        validation_manager = ValidationManager(cache_dir_path=cache_dir_path, dev=dev)
        validated = validation_manager.validate(image_series)
        validated.save(outfile_path, format_="srt", exist_ok=True)
        return Series.load(outfile_path)
    except ScinoephileError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise ScinoephileError(f"Unable to validate OCR: {exc}") from exc
