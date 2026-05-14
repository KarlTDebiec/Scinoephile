#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR support for image subtitles.

Package hierarchy (modules may import from any above):
* bounding_box / preprocessing
* text_result
* paddle_ocr_recognizer
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack, cast

from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

from .paddle_ocr_recognizer import PaddleOcrRecognizer
from .preprocessing import preprocess_paddle_ocr_image

__all__ = [
    "PaddleOcrRecognizer",
    "PaddleOcrRecognizerKwargs",
    "get_paddle_ocr_recognizer",
    "ocr_image_series_with_paddle",
]


class PaddleOcrRecognizerKwargs(TypedDict, total=False):
    """Additional keyword arguments forwarded to PaddleOcrRecognizer."""

    language: str
    """PaddleOCR language code."""

    min_confidence: float
    """Minimum confidence to include."""


def get_paddle_ocr_recognizer(
    *,
    cache_dir_path: Path | None = None,
    **kwargs: Unpack[PaddleOcrRecognizerKwargs],
) -> PaddleOcrRecognizer:
    """Get PaddleOCR recognizer with provided configuration.

    Arguments:
        cache_dir_path: directory in which to cache OCR results
        **kwargs: additional keyword arguments for PaddleOcrRecognizer
    Returns:
        PaddleOCR recognizer
    """
    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("paddleocr")
    return PaddleOcrRecognizer(cache_dir_path=cache_dir_path, **kwargs)


def ocr_image_series_with_paddle(
    image_series: ImageSeries,
    *,
    recognizer: PaddleOcrRecognizer | None = None,
    language: str = "en",
) -> Series:
    """OCR an image subtitle series with PaddleOCR.

    Arguments:
        image_series: image subtitle series
        recognizer: PaddleOCR-compatible recognizer
        language: PaddleOCR language code
    Returns:
        text subtitle series
    """
    if recognizer is None:
        paddle_recognizer = get_paddle_ocr_recognizer(language=language)
    else:
        paddle_recognizer = recognizer

    events = []
    for subtitle in image_series:
        image_subtitle = cast(ImageSubtitle, subtitle)
        preprocessed_image = preprocess_paddle_ocr_image(image_subtitle.img)
        text = paddle_recognizer.recognize_image(preprocessed_image)
        events.append(
            Subtitle(
                start=image_subtitle.start,
                end=image_subtitle.end,
                text=text,
            )
        )
    return Series(events=events)
