#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Google Lens OCR support for image subtitles."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

if TYPE_CHECKING:
    from .google_lens_recognizer import GoogleLensRecognizer

__all__ = [
    "GoogleLensRecognizer",
    "get_google_lens_recognizer",
    "ocr_image_series_with_lens",
]


def __getattr__(name: str):
    """Lazily import Google Lens-backed classes."""
    if name == "GoogleLensRecognizer":
        from .google_lens_recognizer import GoogleLensRecognizer  # noqa: PLC0415

        return GoogleLensRecognizer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def get_google_lens_recognizer(
    *,
    api_key: str | None = None,
    cache_dir_path: Path | None = None,
    client_region: str | None = None,
    client_time_zone: str | None = None,
    language: str = "en",
    max_concurrent: int = 5,
    proxy: str | None = None,
    timeout: int = 60,
) -> GoogleLensRecognizer:
    """Get Google Lens recognizer with provided configuration.

    Arguments:
        api_key: optional Google Lens API key override
        cache_dir_path: directory in which to cache OCR results
        client_region: optional Google Lens client region
        client_time_zone: optional Google Lens client time zone
        language: Google Lens OCR language code
        max_concurrent: maximum concurrent Lens requests
        proxy: optional proxy URL
        timeout: request timeout in seconds
    Returns:
        Google Lens recognizer
    """
    google_lens_recognizer_cls = globals().get("GoogleLensRecognizer")
    if google_lens_recognizer_cls is None:
        from .google_lens_recognizer import GoogleLensRecognizer  # noqa: PLC0415

        google_lens_recognizer_cls = GoogleLensRecognizer

    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("google-lens")
    return google_lens_recognizer_cls(
        api_key=api_key,
        cache_dir_path=cache_dir_path,
        client_region=client_region,
        client_time_zone=client_time_zone,
        language=language,
        max_concurrent=max_concurrent,
        proxy=proxy,
        timeout=timeout,
    )


def ocr_image_series_with_lens(
    image_series: ImageSeries,
    *,
    api_key: str | None = None,
    client_region: str | None = None,
    client_time_zone: str | None = None,
    language: str = "en",
    max_concurrent: int = 5,
    proxy: str | None = None,
    recognizer: GoogleLensRecognizer | None = None,
    timeout: int = 60,
) -> Series:
    """OCR an image subtitle series with Google Lens.

    Arguments:
        image_series: image subtitle series
        api_key: optional Google Lens API key override
        client_region: optional Google Lens client region
        client_time_zone: optional Google Lens client time zone
        language: Google Lens OCR language code
        max_concurrent: maximum concurrent Lens requests
        proxy: optional proxy URL
        recognizer: Google Lens-compatible recognizer
        timeout: request timeout in seconds
    Returns:
        text subtitle series
    """
    if recognizer is None:
        lens_recognizer = get_google_lens_recognizer(
            api_key=api_key,
            client_region=client_region,
            client_time_zone=client_time_zone,
            language=language,
            max_concurrent=max_concurrent,
            proxy=proxy,
            timeout=timeout,
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
