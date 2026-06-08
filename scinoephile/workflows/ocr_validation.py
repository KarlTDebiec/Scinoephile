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
from scinoephile.lang.eng.ocr_validation import validate_eng_ocr
from scinoephile.lang.zho.ocr_validation import validate_zho_ocr
from scinoephile.web.ocr_validation import OcrValidationSession
from scinoephile.web.ocr_validation.app import run_app

__all__ = [
    "validate_ocr",
    "validate_ocr_from_path",
]

logger = getLogger(__name__)


def validate_ocr(
    image_series: ImageSeries,
    language: str,
    outfile_path: Path,
    *,
    image_dir_path: Path | None = None,
    cache_dir_path: Path | str | None = None,
    interactive: bool = False,
    dev: bool = False,
    overwrite: bool = False,
    host: str = "127.0.0.1",
    port: int = 5000,
) -> Series:
    """Validate OCR text against image subtitles.

    Arguments:
        image_series: image subtitle series to validate
        language: OCR validation language
        outfile_path: validated subtitle output path
        image_dir_path: image subtitle directory for interactive validation
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
        return _load_validated_series(outfile_path)

    if interactive:
        if image_dir_path is None:
            raise ScinoephileError(
                "image_dir_path is required for interactive OCR validation"
            )
        _run_interactive_validation(
            image_dir_path,
            outfile_path,
            cache_dir_path,
            dev,
            host,
            port,
        )
    else:
        validated = _run_noninteractive_validation(
            image_series,
            language,
            cache_dir_path,
            dev,
        )
        _save_validated_series(validated, outfile_path)
    return _load_validated_series(outfile_path)


def validate_ocr_from_path(
    infile_path: Path,
    language: str,
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
        language: OCR validation language
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
        return _load_validated_series(outfile_path)

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
        return _load_validated_series(outfile_path)

    try:
        image_series = ImageSeries.load(infile_path)
    except ScinoephileError:
        raise
    except (OSError, ValueError) as exc:
        raise ScinoephileError(str(exc)) from exc
    return validate_ocr(
        image_series,
        language,
        outfile_path,
        cache_dir_path=cache_dir_path,
        dev=dev,
        overwrite=overwrite,
    )


def _load_validated_series(outfile_path: Path) -> Series:
    """Load validated OCR subtitles.

    Arguments:
        outfile_path: validated subtitle output path
    Returns:
        validated subtitle series
    """
    try:
        return Series.load(outfile_path)
    except ScinoephileError:
        raise
    except (OSError, ValueError) as exc:
        raise ScinoephileError(str(exc)) from exc


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
        if isinstance(cache_dir_path, str):
            session_cache_dir_path = Path(cache_dir_path)
        else:
            session_cache_dir_path = cache_dir_path
        session = OcrValidationSession.from_dir_path(
            image_dir_path,
            outfile_path=outfile_path,
            cache_dir_path=session_cache_dir_path,
            dev=dev,
        )
        run_app(session, host, port)
    except ScinoephileError:
        raise
    except (ImportError, OSError, ValueError) as exc:
        raise ScinoephileError(str(exc)) from exc


def _run_noninteractive_validation(
    image_series: ImageSeries,
    language: str,
    cache_dir_path: Path | str | None,
    dev: bool,
) -> Series:
    """Run noninteractive OCR validation.

    Arguments:
        image_series: image subtitle series to validate
        language: OCR validation language
        cache_dir_path: cache directory for local OCR validation data
        dev: whether validation should write data updates to repo data
    Returns:
        validated subtitle series
    """
    try:
        if cache_dir_path is None:
            validation_manager = ValidationManager(dev=dev)
        else:
            validation_manager = ValidationManager(
                cache_dir_path=cache_dir_path,
                dev=dev,
            )
        if language == "eng":
            return validate_eng_ocr(image_series, validation_manager)
        return validate_zho_ocr(image_series, validation_manager)
    except ScinoephileError:
        raise
    except (OSError, ValueError) as exc:
        raise ScinoephileError(str(exc)) from exc


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
        raise ScinoephileError(str(exc)) from exc
