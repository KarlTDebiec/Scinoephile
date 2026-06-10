#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tesseract OCR support for image subtitles.

Package hierarchy (modules may import from any above):
* hocr / preprocessing
* tesseract_recognizer
"""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import TypedDict, Unpack, cast

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

from .tesseract_recognizer import TesseractRecognizer

__all__ = [
    "TesseractRecognizer",
    "TesseractRecognizerKwargs",
    "get_tesseract_language_code",
    "ocr_image_series_with_tesseract",
]

logger = getLogger(__name__)


class TesseractRecognizerKwargs(TypedDict, total=False):
    """Additional keyword arguments forwarded to TesseractRecognizer."""

    cache_dir_path: Path | None
    """Directory in which to cache OCR results."""

    detect_italics: bool
    """Whether to run a legacy-engine pass for italics."""

    executable_path: Path | str
    """Tesseract executable path or command name."""

    language: Language
    """Scinoephile language."""

    oem: int | None
    """Tesseract OCR engine mode, or None to omit --oem."""

    psm: int
    """Tesseract page segmentation mode."""

    scale: int
    """Image preprocessing scale."""

    skip_executable_validation: bool
    """Whether to skip executable validation."""

    tessdata_dir_path: Path | None
    """Optional tessdata directory."""


def get_tesseract_language_code(language: Language) -> str:
    """Get the Tesseract language code.

    Arguments:
        language: Scinoephile language
    Returns:
        Tesseract language code
    Raises:
        ValueError: if language is not supported by Tesseract OCR
    """
    from scinoephile.image.ocr.language import (  # noqa: PLC0415
        get_tesseract_language_code as get_code,
    )

    return get_code(language)


def ocr_image_series_with_tesseract(
    image_series: ImageSeries,
    **kwargs: Unpack[TesseractRecognizerKwargs],
) -> Series:
    """OCR an image subtitle series with Tesseract.

    Arguments:
        image_series: image subtitle series
        **kwargs: additional keyword arguments for TesseractRecognizer
    Returns:
        text subtitle series
    """
    try:
        recognizer_kwargs = dict(kwargs)
        if "cache_dir_path" not in recognizer_kwargs:
            recognizer_kwargs["cache_dir_path"] = get_runtime_cache_dir_path(
                "tesseract"
            )
        tesseract_recognizer = TesseractRecognizer(
            **cast(TesseractRecognizerKwargs, recognizer_kwargs)
        )

        events = []
        subtitle_count = len(image_series.events)
        for subtitle_idx, subtitle in enumerate(image_series, 1):
            logger.info(
                f"OCRing subtitle {subtitle_idx}/{subtitle_count} with Tesseract"
            )
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
    except ScinoephileError:
        raise
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to OCR image series with Tesseract: {exc}"
        ) from exc
