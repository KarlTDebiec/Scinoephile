#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR processing for image subtitle series."""

from __future__ import annotations

from typing import cast

from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

from .engine import PaddleOcrRecognizer, PaddleOcrRecognizerProtocol
from .preprocessing import preprocess_paddle_ocr_image

__all__ = ["ocr_image_series_with_paddle"]


def ocr_image_series_with_paddle(
    image_series: ImageSeries,
    *,
    recognizer: PaddleOcrRecognizerProtocol | None = None,
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
    paddle_recognizer = recognizer
    if paddle_recognizer is None:
        paddle_recognizer = PaddleOcrRecognizer(language=language)

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
