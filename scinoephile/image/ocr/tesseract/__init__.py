#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tesseract OCR support for image subtitles."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import cast

from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

from .tesseract_ocr_recognizer import TesseractOcrRecognizer

__all__ = [
    "TesseractOcrRecognizer",
    "get_tesseract_ocr_recognizer",
    "ocr_image_series_with_tesseract",
]

logger = getLogger(__name__)


def get_tesseract_ocr_recognizer(
    *,
    cache_dir_path: Path | None = None,
    executable_path: Path | str = "tesseract",
    detect_italics: bool = False,
    language: str = "eng",
    legacy_tessdata_dir_path: Path | None = None,
    oem: int | None = 3,
    psm: int = 6,
    scale: int = 2,
    skip_executable_validation: bool = False,
    tessdata_dir_path: Path | None = None,
) -> TesseractOcrRecognizer:
    """Get Tesseract recognizer with provided configuration.

    Arguments:
        cache_dir_path: directory in which to cache OCR results
        executable_path: Tesseract executable path or command name
        detect_italics: whether to run a legacy-engine pass for italics
        language: Tesseract language code
        legacy_tessdata_dir_path: optional tessdata directory for legacy OCR
        oem: Tesseract OCR engine mode, or None to omit --oem
        psm: Tesseract page segmentation mode
        scale: image preprocessing scale
        skip_executable_validation: whether to skip executable validation
        tessdata_dir_path: optional tessdata directory
    Returns:
        Tesseract recognizer
    """
    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("tesseract")
    return TesseractOcrRecognizer(
        cache_dir_path=cache_dir_path,
        executable_path=executable_path,
        detect_italics=detect_italics,
        language=language,
        legacy_tessdata_dir_path=legacy_tessdata_dir_path,
        oem=oem,
        psm=psm,
        scale=scale,
        skip_executable_validation=skip_executable_validation,
        tessdata_dir_path=tessdata_dir_path,
    )


def ocr_image_series_with_tesseract(
    image_series: ImageSeries,
    *,
    recognizer: TesseractOcrRecognizer | None = None,
    detect_italics: bool = False,
    language: str = "eng",
    legacy_tessdata_dir_path: Path | None = None,
) -> Series:
    """OCR an image subtitle series with Tesseract.

    Arguments:
        image_series: image subtitle series
        recognizer: Tesseract-compatible recognizer
        detect_italics: whether to run a legacy-engine pass for italics
        language: Tesseract language code
        legacy_tessdata_dir_path: optional tessdata directory for legacy OCR
    Returns:
        text subtitle series
    """
    if recognizer is None:
        tesseract_recognizer = get_tesseract_ocr_recognizer(
            detect_italics=detect_italics,
            language=language,
            legacy_tessdata_dir_path=legacy_tessdata_dir_path,
        )
    else:
        tesseract_recognizer = recognizer

    events = []
    subtitle_count = len(image_series.events)
    for subtitle_idx, subtitle in enumerate(image_series, 1):
        logger.info(f"OCRing subtitle {subtitle_idx}/{subtitle_count} with Tesseract")
        image_subtitle = cast(ImageSubtitle, subtitle)
        text = tesseract_recognizer.recognize_image(image_subtitle.img)
        events.append(
            Subtitle(
                start=image_subtitle.start,
                end=image_subtitle.end,
                text=text,
            )
        )
    return Series(events=events)
