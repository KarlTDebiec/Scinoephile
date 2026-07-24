#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tesseract OCR support for image subtitles.

Package hierarchy (modules may import from any above):
* hocr / preprocessing
* tesseract_recognizer
"""

from __future__ import annotations

from logging import getLogger
from typing import Unpack, cast

from scinoephile.core import ScinoephileError
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

from .tesseract_recognizer import TesseractRecognizer, TesseractRecognizerKwargs

__all__ = [
    "TesseractRecognizer",
    "TesseractRecognizerKwargs",
    "ocr_image_series_with_tesseract",
]

logger = getLogger(__name__)


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
        if kwargs.get("cache_dir_path") is None:
            kwargs["cache_dir_path"] = get_runtime_cache_dir_path("tesseract")
        tesseract_recognizer = TesseractRecognizer(**kwargs)

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
