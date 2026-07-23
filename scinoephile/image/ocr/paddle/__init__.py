#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR support for image subtitles.

Package hierarchy (modules may import from any above):
* bounding_box / preprocessing
* text_result
* paddle_recognizer
"""

from __future__ import annotations

from logging import getLogger
from typing import Unpack, cast

from scinoephile.core import ScinoephileError
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

from .paddle_recognizer import PaddleRecognizer, PaddleRecognizerKwargs

__all__ = [
    "PaddleRecognizer",
    "PaddleRecognizerKwargs",
    "ocr_image_series_with_paddle",
]

logger = getLogger(__name__)


def ocr_image_series_with_paddle(
    image_series: ImageSeries,
    **kwargs: Unpack[PaddleRecognizerKwargs],
) -> Series:
    """OCR an image subtitle series with PaddleOCR.

    Arguments:
        image_series: image subtitle series
        **kwargs: additional keyword arguments for PaddleRecognizer
    Returns:
        text subtitle series
    """
    try:
        from .preprocessing import preprocess_paddle_ocr_image  # noqa: PLC0415

        if "cache_dir_path" not in kwargs:
            kwargs["cache_dir_path"] = get_runtime_cache_dir_path("paddleocr")
        paddle_recognizer = PaddleRecognizer(**kwargs)

        events = []
        subtitle_count = len(image_series.events)
        for subtitle_idx, subtitle in enumerate(image_series, 1):
            logger.info(
                f"OCRing subtitle {subtitle_idx}/{subtitle_count} with PaddleOCR"
            )
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
