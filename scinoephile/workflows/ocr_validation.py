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

__all__ = ["serve_ocr_validation", "validate_ocr"]

logger = getLogger(__name__)


def serve_ocr_validation(
    dir_path: Path,
    outfile_path: Path,
    *,
    validation_data_dir_path: Path | str | None = None,
    dev: bool = False,
    host: str = "127.0.0.1",
    port: int = 5000,
    title: str | None = None,
):
    """Open the local OCR editor and keep its SRT output current.

    Arguments:
        dir_path: directory containing OCR text and subtitle images
        outfile_path: SRT regenerated from the image directory when the editor opens
        validation_data_dir_path: local OCR validation data directory
        dev: whether validation should write data updates to repo data
        host: OCR validation web UI host
        port: OCR validation web UI port
        title: display title for the OCR validation editor
    Raises:
        ScinoephileError: if the editor cannot open or serve the OCR directory
    """
    try:
        session = OcrValidationSession.from_dir_path(
            dir_path,
            outfile_path=outfile_path,
            validation_data_dir_path=validation_data_dir_path,
            dev=dev,
        )
        run_app(session, host, port, title=title)
    except ScinoephileError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise ScinoephileError(f"Unable to serve OCR validation: {exc}") from exc


def validate_ocr(
    source: Path | ImageSeries,
    outfile_path: Path,
    *,
    validation_data_dir_path: Path | str | None = None,
    dev: bool = False,
    overwrite: bool = False,
) -> Series:
    """Automatically validate OCR text from image subtitles and write the SRT.

    Arguments:
        source: image subtitle input path or image series
        outfile_path: validated subtitle output path
        validation_data_dir_path: local OCR validation data directory
        dev: whether validation should write data updates to repo data
        overwrite: whether to overwrite existing validation output
    Returns:
        validated subtitle series
    Raises:
        ScinoephileError: if the operation fails
    """
    if outfile_path.exists() and not overwrite:
        logger.info(f"Validated OCR output exists: {outfile_path}")
        return Series.load(outfile_path)

    try:
        if isinstance(source, ImageSeries):
            image_series = source
        else:
            image_series = ImageSeries.load(source)
        validation_manager = ValidationManager(
            validation_data_dir_path=validation_data_dir_path, dev=dev
        )
        validated = validation_manager.validate(image_series)
        validated.save(outfile_path, format_="srt", exist_ok=True)
        return Series.load(outfile_path)
    except ScinoephileError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise ScinoephileError(f"Unable to validate OCR: {exc}") from exc
