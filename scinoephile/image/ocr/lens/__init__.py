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
    "LensRecognizer",
    "LensRecognizerKwargs",
    "ocr_image_series_with_lens",
]


class LensRecognizerKwargs(TypedDict, total=False):
    """Additional keyword arguments forwarded to LensRecognizer."""

    cache_dir_path: Path | None
    """Directory in which to cache OCR results."""

    language: Language
    """Scinoephile language."""

    retries: int
    """Google Lens OCR request attempts per uncached image."""


def ocr_image_series_with_lens(
    image_series: ImageSeries,
    **kwargs: Unpack[LensRecognizerKwargs],
) -> Series:
    """OCR an image subtitle series with Google Lens.

    Arguments:
        image_series: image subtitle series
        **kwargs: additional keyword arguments for LensRecognizer
    Returns:
        text subtitle series
    """
    try:
        if "cache_dir_path" not in kwargs:
            kwargs["cache_dir_path"] = get_runtime_cache_dir_path("google-lens")
        lens_recognizer = LensRecognizer(**kwargs)

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
