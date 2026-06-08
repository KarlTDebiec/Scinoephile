#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow helpers for OCR validation."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core import ScinoephileError
from scinoephile.image.ocr.validation import ValidationManager
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.ocr_validation import validate_eng_ocr
from scinoephile.lang.zho.ocr_validation import validate_zho_ocr
from scinoephile.web.ocr_validation import OcrValidationSession, create_app

__all__ = [
    "run_ocr_validation_web",
    "validate_ocr",
]


def run_ocr_validation_web(
    infile_path: Path,
    outfile_path: Path,
    cache_dir_path: Path,
    *,
    host: str,
    port: int,
    dev: bool,
):
    """Run interactive OCR validation through the local web UI.

    Arguments:
        infile_path: OCR image subtitle directory path
        outfile_path: validated subtitle output path
        cache_dir_path: OCR validation cache directory path
        host: OCR validation web UI host
        port: OCR validation web UI port
        dev: whether validation should write data updates to repo data
    """
    session = OcrValidationSession.from_dir_path(
        infile_path,
        outfile_path=outfile_path,
        cache_dir_path=cache_dir_path,
        dev=dev,
    )
    try:
        create_app(session).run(host, port)
    except ScinoephileError:
        raise
    except (OSError, ValueError) as exc:
        raise ScinoephileError(str(exc)) from exc


def validate_ocr(
    infile_path: Path,
    language: str,
    *,
    cache_dir_path: Path,
    dev: bool = False,
) -> ImageSeries:
    """Validate OCR text in image subtitles.

    Arguments:
        infile_path: OCR image subtitle input path
        language: OCR validation language
        cache_dir_path: OCR validation cache directory path
        dev: whether validation should write data updates to repo data
    Returns:
        validated image subtitle series
    """
    series = _load_image_series(infile_path)
    validation_manager = _get_validation_manager(cache_dir_path, dev)
    if language == "eng":
        return validate_eng_ocr(series, validation_manager)
    if language == "zho":
        return validate_zho_ocr(series, validation_manager)
    raise ScinoephileError(f"Unsupported OCR validation language: {language}")


def _get_validation_manager(cache_dir_path: Path, dev: bool) -> ValidationManager:
    """Get an OCR validation manager.

    Arguments:
        cache_dir_path: OCR validation cache directory path
        dev: whether validation should write data updates to repo data
    Returns:
        OCR validation manager
    """
    try:
        return ValidationManager(cache_dir_path=cache_dir_path, dev=dev)
    except ScinoephileError:
        raise
    except (OSError, ValueError) as exc:
        raise ScinoephileError(str(exc)) from exc


def _load_image_series(infile_path: Path) -> ImageSeries:
    """Load image subtitles for OCR validation.

    Arguments:
        infile_path: OCR image subtitle input path
    Returns:
        image subtitle series
    """
    try:
        return ImageSeries.load(infile_path)
    except ScinoephileError:
        raise
    except (OSError, ValueError) as exc:
        raise ScinoephileError(str(exc)) from exc
