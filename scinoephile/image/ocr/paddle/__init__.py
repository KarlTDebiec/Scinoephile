#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR support for image subtitles."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

from .preprocessing import preprocess_paddle_ocr_image

if TYPE_CHECKING:
    from .paddle_ocr_recognizer import PaddleOcrRecognizer

__all__ = [
    "PaddleOcrRecognizer",
    "get_paddle_ocr_recognizer",
    "ocr_image_series_with_paddle",
]


def __getattr__(name: str):
    """Lazily import PaddleOCR-backed classes."""
    if name == "PaddleOcrRecognizer":
        from .paddle_ocr_recognizer import PaddleOcrRecognizer  # noqa: PLC0415

        return PaddleOcrRecognizer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def get_paddle_ocr_recognizer(
    *,
    cache_dir_path: Path | None = None,
    language: str = "en",
    min_confidence: float = 0.0,
) -> PaddleOcrRecognizer:
    """Get PaddleOCR recognizer with provided configuration.

    Arguments:
        cache_dir_path: directory in which to cache OCR results
        language: PaddleOCR language code
        min_confidence: minimum confidence to include
    Returns:
        PaddleOCR recognizer
    """
    paddle_ocr_recognizer_cls = globals().get("PaddleOcrRecognizer")
    if paddle_ocr_recognizer_cls is None:
        from .paddle_ocr_recognizer import PaddleOcrRecognizer  # noqa: PLC0415

        paddle_ocr_recognizer_cls = PaddleOcrRecognizer

    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("paddleocr")
    return paddle_ocr_recognizer_cls(
        cache_dir_path=cache_dir_path,
        language=language,
        min_confidence=min_confidence,
    )


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
