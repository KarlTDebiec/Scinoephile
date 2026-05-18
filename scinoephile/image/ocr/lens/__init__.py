#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Google Lens OCR support for image subtitles."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

from .google_lens_recognizer import GoogleLensRecognizer

__all__ = [
    "GoogleLensRecognizer",
    "get_google_lens_recognizer",
    "ocr_image_series_with_lens",
]


def get_google_lens_recognizer(
    *,
    cache_dir_path: Path | None = None,
    language: str = "en",
    retries: int = 3,
) -> GoogleLensRecognizer:
    """Get Google Lens recognizer with provided configuration.

    Arguments:
        cache_dir_path: directory in which to cache OCR results
        language: Google Lens OCR language code
        retries: Google Lens OCR request attempts per uncached image
    Returns:
        Google Lens recognizer
    """
    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("google-lens")
    return GoogleLensRecognizer(
        cache_dir_path=cache_dir_path,
        language=language,
        retries=retries,
    )


def ocr_image_series_with_lens(
    image_series: ImageSeries,
    *,
    language: str = "en",
    retries: int = 3,
    recognizer: GoogleLensRecognizer | None = None,
) -> Series:
    """OCR an image subtitle series with Google Lens.

    Arguments:
        image_series: image subtitle series
        language: Google Lens OCR language code
        retries: Google Lens OCR request attempts per uncached image
        recognizer: Google Lens-compatible recognizer
    Returns:
        text subtitle series
    """
    if recognizer is None:
        lens_recognizer = get_google_lens_recognizer(
            language=language,
            retries=retries,
        )
    else:
        lens_recognizer = recognizer

    events = []
    for subtitle in image_series:
        image_subtitle = cast(ImageSubtitle, subtitle)
        text = lens_recognizer.recognize_image(image_subtitle.img)
        events.append(
            Subtitle(
                start=image_subtitle.start,
                end=image_subtitle.end,
                text=text,
            )
        )
    return Series(events=events)
