#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR support for image subtitles."""

from __future__ import annotations

from typing import cast

from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

from .bounding_box import PaddleOcrBoundingBox
from .engine import PaddleOcrRecognizer
from .preprocessing import preprocess_paddle_ocr_image
from .result import (
    format_paddle_ocr_text,
    group_paddle_ocr_text_results,
)
from .text_result import PaddleOcrTextResult

__all__ = [
    "PaddleOcrBoundingBox",
    "PaddleOcrRecognizer",
    "PaddleOcrTextResult",
    "format_paddle_ocr_text",
    "group_paddle_ocr_text_results",
    "ocr_image_series_with_paddle",
    "preprocess_paddle_ocr_image",
]


def ocr_image_series_with_paddle(
    image_series: ImageSeries,
    *,
    recognizer: object | None = None,
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
        paddle_recognizer = PaddleOcrRecognizer(
            cache_dir_path=get_runtime_cache_dir_path("paddleocr"),
            language=language,
        )
    else:
        paddle_recognizer = cast(PaddleOcrRecognizer, recognizer)

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
