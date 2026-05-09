#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tesseract OCR support for image subtitles."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

from .tesseract_ocr_recognizer import (
    Tesseract3OcrRecognizer,
    Tesseract5OcrRecognizer,
    TesseractOcrRecognizer,
)

__all__ = [
    "Tesseract3OcrRecognizer",
    "Tesseract5OcrRecognizer",
    "TesseractOcrRecognizer",
    "get_tesseract3_ocr_recognizer",
    "get_tesseract5_ocr_recognizer",
    "ocr_image_series_with_tesseract3",
    "ocr_image_series_with_tesseract5",
]


def get_tesseract3_ocr_recognizer(
    *,
    cache_dir_path: Path | None = None,
    executable_path: Path | str = "tesseract",
    language: str = "eng",
    oem: int | None = None,
    psm: int = 6,
    scale: int = 2,
    skip_executable_validation: bool = False,
    tessdata_dir_path: Path | None = None,
) -> Tesseract3OcrRecognizer:
    """Get Tesseract 3 recognizer with provided configuration.

    Arguments:
        cache_dir_path: directory in which to cache OCR results
        executable_path: Tesseract executable path or command name
        language: Tesseract language code
        oem: Tesseract OCR engine mode, or None to omit --oem
        psm: Tesseract page segmentation mode
        scale: image preprocessing scale
        skip_executable_validation: whether to skip executable validation
        tessdata_dir_path: optional tessdata directory
    Returns:
        Tesseract 3 recognizer
    """
    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("tesseract3")
    return Tesseract3OcrRecognizer(
        cache_dir_path=cache_dir_path,
        executable_path=executable_path,
        language=language,
        oem=oem,
        psm=psm,
        scale=scale,
        skip_executable_validation=skip_executable_validation,
        tessdata_dir_path=tessdata_dir_path,
    )


def get_tesseract5_ocr_recognizer(
    *,
    cache_dir_path: Path | None = None,
    executable_path: Path | str = "tesseract",
    language: str = "eng",
    oem: int | None = 3,
    psm: int = 6,
    scale: int = 2,
    skip_executable_validation: bool = False,
    tessdata_dir_path: Path | None = None,
) -> Tesseract5OcrRecognizer:
    """Get Tesseract 5 recognizer with provided configuration.

    Arguments:
        cache_dir_path: directory in which to cache OCR results
        executable_path: Tesseract executable path or command name
        language: Tesseract language code
        oem: Tesseract OCR engine mode, or None to omit --oem
        psm: Tesseract page segmentation mode
        scale: image preprocessing scale
        skip_executable_validation: whether to skip executable validation
        tessdata_dir_path: optional tessdata directory
    Returns:
        Tesseract 5 recognizer
    """
    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("tesseract5")
    return Tesseract5OcrRecognizer(
        cache_dir_path=cache_dir_path,
        executable_path=executable_path,
        language=language,
        oem=oem,
        psm=psm,
        scale=scale,
        skip_executable_validation=skip_executable_validation,
        tessdata_dir_path=tessdata_dir_path,
    )


def ocr_image_series_with_tesseract3(
    image_series: ImageSeries,
    *,
    recognizer: Tesseract3OcrRecognizer | None = None,
    language: str = "eng",
) -> Series:
    """OCR an image subtitle series with Tesseract 3.

    Arguments:
        image_series: image subtitle series
        recognizer: Tesseract 3-compatible recognizer
        language: Tesseract language code
    Returns:
        text subtitle series
    """
    if recognizer is None:
        tesseract_recognizer = get_tesseract3_ocr_recognizer(language=language)
    else:
        tesseract_recognizer = recognizer

    return _ocr_image_series_with_tesseract(
        image_series, recognizer=tesseract_recognizer
    )


def ocr_image_series_with_tesseract5(
    image_series: ImageSeries,
    *,
    recognizer: Tesseract5OcrRecognizer | None = None,
    language: str = "eng",
) -> Series:
    """OCR an image subtitle series with Tesseract 5.

    Arguments:
        image_series: image subtitle series
        recognizer: Tesseract 5-compatible recognizer
        language: Tesseract language code
    Returns:
        text subtitle series
    """
    if recognizer is None:
        tesseract_recognizer = get_tesseract5_ocr_recognizer(language=language)
    else:
        tesseract_recognizer = recognizer

    return _ocr_image_series_with_tesseract(
        image_series, recognizer=tesseract_recognizer
    )


def _ocr_image_series_with_tesseract(
    image_series: ImageSeries,
    *,
    recognizer: TesseractOcrRecognizer,
) -> Series:
    """OCR an image subtitle series with Tesseract.

    Arguments:
        image_series: image subtitle series
        recognizer: Tesseract-compatible recognizer
    Returns:
        text subtitle series
    """
    events = []
    for subtitle in image_series:
        image_subtitle = cast(ImageSubtitle, subtitle)
        text = recognizer.recognize_image(image_subtitle.img)
        events.append(
            Subtitle(
                start=image_subtitle.start,
                end=image_subtitle.end,
                text=text,
            )
        )
    return Series(events=events)
