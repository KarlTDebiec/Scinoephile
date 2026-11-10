#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow helpers for validating OCR against image subtitles."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import Protocol

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.image.ocr.validation import ValidationManager
from scinoephile.image.subtitles import ImageSeries

__all__ = ["OcrValidationEditor", "validate_ocr"]

logger = getLogger(__name__)


class OcrValidationEditor(Protocol):
    """Open a client editor that writes validated subtitles before returning."""

    def __call__(
        self,
        source_dir_path: Path,
        outfile_path: Path,
        *,
        validation_data_dir_path: Path | str | None,
        dev: bool,
    ) -> None:
        """Validate OCR interactively and write the output subtitles.

        Arguments:
            source_dir_path: directory containing OCR image subtitles
            outfile_path: validated subtitle output path
            validation_data_dir_path: local OCR validation data directory
            dev: whether to write validation data updates to repo data
        """
        ...


def validate_ocr(
    source: Path | ImageSeries,
    outfile_path: Path,
    *,
    validation_data_dir_path: Path | str | None = None,
    validation_editor: OcrValidationEditor | None = None,
    dev: bool = False,
    overwrite: bool = False,
) -> Series:
    """Validate OCR text from image subtitles.

    Arguments:
        source: image subtitle input path or image series
        outfile_path: validated subtitle output path
        validation_data_dir_path: local OCR validation data directory
        validation_editor: optional client editor for interactive validation
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
        if validation_editor is not None:
            if not isinstance(source, Path) or not source.is_dir():
                raise ScinoephileError(
                    f"{source} must be a directory when interactive validation "
                    "is enabled"
                )
            validation_editor(
                source,
                outfile_path,
                validation_data_dir_path=validation_data_dir_path,
                dev=dev,
            )
            return Series.load(outfile_path)

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
