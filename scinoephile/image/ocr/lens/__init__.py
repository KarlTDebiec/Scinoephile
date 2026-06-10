#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Google Lens OCR support for image subtitles."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack, cast

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

from .lens_recognizer import LensRecognizer

__all__ = [
    "GoogleLensRecognizerKwargs",
    "LensRecognizer",
    "get_lens_recognizer",
    "get_lens_language_code",
    "ocr_image_series_with_lens",
]


class GoogleLensRecognizerKwargs(TypedDict, total=False):
    """Additional keyword arguments forwarded to LensRecognizer."""

    language: Language
    """Scinoephile language."""

    retries: int
    """Google Lens OCR request attempts per uncached image."""


def get_lens_recognizer(
    *,
    cache_dir_path: Path | None = None,
    **kwargs: Unpack[GoogleLensRecognizerKwargs],
) -> LensRecognizer:
    """Get Google Lens recognizer with provided configuration.

    Arguments:
        cache_dir_path: directory in which to cache OCR results
        **kwargs: additional keyword arguments for LensRecognizer
    Returns:
        Google Lens recognizer
    """
    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("google-lens")
    return LensRecognizer(cache_dir_path=cache_dir_path, **kwargs)


def get_lens_language_code(language: Language) -> str:
    """Get the Google Lens language code.

    Arguments:
        language: Scinoephile language
    Returns:
        Google Lens language code
    Raises:
        ValueError: if language is not supported by Google Lens OCR
    """
    from scinoephile.image.ocr.language import (  # noqa: PLC0415
        get_lens_language_code as get_code,
    )

    return get_code(language)


def ocr_image_series_with_lens(
    image_series: ImageSeries,
    *,
    language: Language = Language.eng,
    retries: int = 3,
    recognizer: LensRecognizer | None = None,
) -> Series:
    """OCR an image subtitle series with Google Lens.

    Arguments:
        image_series: image subtitle series
        language: Scinoephile language
        retries: Google Lens OCR request attempts per uncached image
        recognizer: Google Lens-compatible recognizer
    Returns:
        text subtitle series
    """
    try:
        if recognizer is None:
            lens_recognizer = get_lens_recognizer(language=language, retries=retries)
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
    except ScinoephileError:
        raise
    except (
        ImportError,
        OSError,
        RuntimeError,
        ValueError,
    ) as exc:
        raise ScinoephileError(
            f"Unable to OCR image series with Google Lens: {exc}"
        ) from exc
