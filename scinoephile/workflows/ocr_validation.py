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
from scinoephile.web.ocr_validation import OcrValidationSession
from scinoephile.web.ocr_validation.app import run_app

__all__ = ["validate_ocr"]

logger = getLogger(__name__)


def validate_ocr(
    infile_path: Path,
    outfile_path: Path,
    *,
    cache_dir_path: Path | str | None = None,
    interactive: bool = False,
    dev: bool = False,
    overwrite: bool = False,
    host: str = "127.0.0.1",
    port: int = 5000,
) -> Series:
    """Validate OCR text from an image subtitle input path.

    Arguments:
        infile_path: image subtitle input path
        outfile_path: validated subtitle output path
        cache_dir_path: cache directory for local OCR validation data
        interactive: whether to launch the OCR validation web UI
        dev: whether validation should write data updates to repo data
        overwrite: whether to overwrite existing validation output
        host: OCR validation web UI host
        port: OCR validation web UI port
    Returns:
        validated subtitle series
    """
    if outfile_path.exists() and not overwrite:
        logger.info(f"Validated OCR output exists: {outfile_path}")
        return Series.load(outfile_path)

    # Interactive validation
    if interactive:
        if not infile_path.is_dir():
            raise ScinoephileError(
                f"{infile_path} must be a directory when interactive validation "
                "is enabled"
            )
        session = OcrValidationSession.from_dir_path(
            infile_path,
            outfile_path=outfile_path,
            cache_dir_path=cache_dir_path,
            dev=dev,
        )
        run_app(session, host, port)
        return Series.load(outfile_path)

    # Non-interactive validation
    image_series = ImageSeries.load(infile_path)
    try:
        validation_manager = ValidationManager(cache_dir_path=cache_dir_path, dev=dev)
        validated = validation_manager.validate(image_series)
    except (OSError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to run noninteractive OCR validation: {exc}"
        ) from exc
    validated.save(outfile_path, format_="srt", exist_ok=True)
    return Series.load(outfile_path)
