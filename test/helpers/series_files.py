#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared helpers for writing subtitle series fixtures."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core.subtitles import Series, Subtitle

__all__ = [
    "get_ocr_text_series",
    "get_text_series",
    "write_srt_series",
]


def get_ocr_text_series(*texts: str) -> Series:
    """Build a text subtitle series matching OCR workflow test timings.

    Arguments:
        *texts: subtitle event texts
    Returns:
        subtitle series with one event per text
    """
    return get_text_series(
        *texts,
        start_ms=1000,
        duration_ms=1000,
        step_ms=2000,
    )


def get_text_series(
    *texts: str,
    start_ms: int = 0,
    duration_ms: int = 500,
    step_ms: int = 1000,
) -> Series:
    """Build a compact subtitle series from text events.

    Arguments:
        *texts: subtitle event texts
        start_ms: start time for the first subtitle, in milliseconds
        duration_ms: duration for each subtitle, in milliseconds
        step_ms: time between subtitle starts, in milliseconds
    Returns:
        subtitle series with one event per text
    """
    return Series(
        events=[
            Subtitle(
                start=start_ms + (idx * step_ms),
                end=start_ms + (idx * step_ms) + duration_ms,
                text=text,
            )
            for idx, text in enumerate(texts)
        ]
    )


def write_srt_series(path: Path, text: str) -> Series:
    """Write a one-subtitle SRT fixture.

    Arguments:
        path: path to write
        text: subtitle text
    Returns:
        written subtitle series
    """
    source = f"1\n00:00:00,000 --> 00:00:01,000\n{text}\n"
    path.write_text(source, encoding="utf-8")
    return Series.from_string(source, format_="srt")
