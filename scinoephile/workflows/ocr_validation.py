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
    text_series: Series | None = None,
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
        text_series: optional OCR text to apply to the image subtitle directory
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

    if text_series is not None:
        _apply_text_series(infile_path, text_series)

    if interactive:
        if not infile_path.is_dir():
            raise ScinoephileError(
                f"{infile_path} must be a directory when interactive validation "
                "is enabled"
            )
        _run_interactive_validation(
            infile_path,
            outfile_path,
            cache_dir_path,
            dev,
            host,
            port,
        )
        return Series.load(outfile_path)

    try:
        image_series = ImageSeries.load(infile_path)
        if text_series is not None:
            image_series.copy_text_from(text_series)
    except ScinoephileError:
        raise
    except (OSError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to load OCR image subtitles from {infile_path}: {exc}"
        ) from exc
    validated = _run_noninteractive_validation(
        image_series,
        cache_dir_path,
        dev,
    )
    _save_validated_series(validated, outfile_path)
    return Series.load(outfile_path)


def _apply_text_series(infile_path: Path, text_series: Series):
    """Apply text subtitles to an image subtitle directory index.

    Arguments:
        infile_path: image subtitle directory path
        text_series: text subtitle series to write into the image index
    """
    if not infile_path.is_dir():
        raise ScinoephileError(
            "text_series can only be applied to an image subtitle directory"
        )
    try:
        image_series = ImageSeries.load(infile_path)
        image_series.copy_text_from(text_series)
        image_series.save(infile_path)
    except ScinoephileError:
        raise
    except (OSError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to apply OCR text to image subtitle directory {infile_path}: {exc}"
        ) from exc


def _run_interactive_validation(
    image_dir_path: Path,
    outfile_path: Path,
    cache_dir_path: Path | str | None,
    dev: bool,
    host: str,
    port: int,
):
    """Run interactive OCR validation.

    Arguments:
        image_dir_path: OCR image subtitle directory
        outfile_path: validated subtitle output path
        cache_dir_path: cache directory for local OCR validation data
        dev: whether validation should write data updates to repo data
        host: OCR validation web UI host
        port: OCR validation web UI port
    """
    try:
        session = OcrValidationSession.from_dir_path(
            image_dir_path,
            outfile_path=outfile_path,
            cache_dir_path=cache_dir_path,
            dev=dev,
        )
        run_app(session, host, port)
    except ScinoephileError:
        raise
    except (ImportError, OSError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to run interactive OCR validation for {image_dir_path}: {exc}"
        ) from exc


def _run_noninteractive_validation(
    image_series: ImageSeries,
    cache_dir_path: Path | str | None,
    dev: bool,
) -> Series:
    """Run noninteractive OCR validation.

    Arguments:
        image_series: image subtitle series to validate
        cache_dir_path: cache directory for local OCR validation data
        dev: whether validation should write data updates to repo data
    Returns:
        validated subtitle series
    """
    try:
        validation_manager = ValidationManager(cache_dir_path=cache_dir_path, dev=dev)
        return validation_manager.validate(image_series)
    except ScinoephileError:
        raise
    except (OSError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to run noninteractive OCR validation: {exc}"
        ) from exc


def _save_validated_series(series: Series, outfile_path: Path):
    """Save validated OCR subtitles.

    Arguments:
        series: validated subtitle series
        outfile_path: validated subtitle output path
    """
    try:
        series.save(outfile_path, format_="srt", exist_ok=True)
    except ScinoephileError:
        raise
    except (OSError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to save validated OCR output to {outfile_path}: {exc}"
        ) from exc
