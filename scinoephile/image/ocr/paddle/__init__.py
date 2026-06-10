#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR support for image subtitles.

Package hierarchy (modules may import from any above):
* bounding_box / preprocessing
* text_result
* paddle_recognizer
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack, cast

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

from .paddle_recognizer import PaddleRecognizer
from .preprocessing import preprocess_paddle_ocr_image

__all__ = [
    "PaddleRecognizer",
    "PaddleRecognizerKwargs",
    "get_paddle_language_code",
    "get_paddle_recognizer",
    "ocr_image_series_with_paddle",
]


class PaddleRecognizerKwargs(TypedDict, total=False):
    """Additional keyword arguments forwarded to PaddleRecognizer."""

    language: Language
    """Scinoephile language."""

    min_confidence: float
    """Minimum confidence to include."""


def get_paddle_recognizer(
    *,
    cache_dir_path: Path | None = None,
    **kwargs: Unpack[PaddleRecognizerKwargs],
) -> PaddleRecognizer:
    """Get PaddleOCR recognizer with provided configuration.

    Arguments:
        cache_dir_path: directory in which to cache OCR results
        **kwargs: additional keyword arguments for PaddleRecognizer
    Returns:
        PaddleOCR recognizer
    """
    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("paddleocr")
    return PaddleRecognizer(cache_dir_path=cache_dir_path, **kwargs)


def get_paddle_language_code(language: Language) -> str:
    """Get the PaddleOCR language code.

    Arguments:
        language: Scinoephile language
    Returns:
        PaddleOCR language code
    Raises:
        ValueError: if language is not supported by PaddleOCR
    """
    from scinoephile.image.ocr.language import (  # noqa: PLC0415
        get_paddle_language_code as get_code,
    )

    return get_code(language)


def ocr_image_series_with_paddle(
    image_series: ImageSeries,
    *,
    recognizer: PaddleRecognizer | None = None,
    language: Language = Language.eng,
) -> Series:
    """OCR an image subtitle series with PaddleOCR.

    Arguments:
        image_series: image subtitle series
        recognizer: PaddleOCR-compatible recognizer
        language: Scinoephile language
    Returns:
        text subtitle series
    """
    try:
        if recognizer is None:
            paddle_recognizer = get_paddle_recognizer(language=language)
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
    except ScinoephileError:
        raise
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to OCR image series with PaddleOCR: {exc}"
        ) from exc
