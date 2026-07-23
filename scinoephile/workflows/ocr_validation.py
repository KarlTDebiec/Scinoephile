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
    source: Path | ImageSeries,
    outfile_path: Path,
    *,
    cache_dir_path: Path | str | None = None,
    interactive: bool = False,
    dev: bool = False,
    overwrite: bool = False,
    host: str = "127.0.0.1",
    port: int = 5000,
) -> Series:
    """Validate OCR text from image subtitles.

    Arguments:
        source: image subtitle input path or image series
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

    try:
        if interactive:
            if not isinstance(source, Path) or not source.is_dir():
                raise ScinoephileError(
                    f"{source} must be a directory when interactive validation "
                    "is enabled"
                )
            session = OcrValidationSession.from_dir_path(
                source,
                outfile_path=outfile_path,
                cache_dir_path=cache_dir_path,
                dev=dev,
            )
            run_app(session, host, port)
            return Series.load(outfile_path)

        if isinstance(source, ImageSeries):
            image_series = source
        else:
            image_series = ImageSeries.load(source)
        validation_manager = ValidationManager(cache_dir_path=cache_dir_path, dev=dev)
        validated = validation_manager.validate(image_series)
        validated.save(outfile_path, format_="srt", exist_ok=True)
        return Series.load(outfile_path)
    except ScinoephileError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise ScinoephileError(f"Unable to validate OCR: {exc}") from exc
