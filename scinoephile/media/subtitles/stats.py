#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream statistics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scinoephile.core.media import SubtitleStream
from scinoephile.core.subtitles import Series
from scinoephile.image.subtitles import ImageSeries

from .cache import cache_subtitles, get_subtitle_cache_path

__all__ = [
    "SubtitleStreamStats",
    "get_subtitle_stream_stats",
]


@dataclass(frozen=True)
class SubtitleStreamStats:
    """Derived subtitle stream statistics."""

    event_count: int
    """Number of subtitle events."""
    first_start_ms: int | None
    """First subtitle start time in milliseconds."""
    last_end_ms: int | None
    """Last subtitle end time in milliseconds."""


def get_subtitle_stream_stats(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None = None,
) -> SubtitleStreamStats:
    """Get subtitle stream event count and span from cached streams.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to inspect
        cache_dir_path: cache directory path
    Returns:
        subtitle stream statistics
    """
    cache_subtitles(infile_path, [stream], cache_dir_path=cache_dir_path)
    stream_path = get_subtitle_cache_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    if stream.extension == "sup":
        image_dir_path = stream_path.parent / "image-series"
        series = ImageSeries.load(image_dir_path)
    else:
        series = Series.load(stream_path)

    if series:
        first_start_ms = min(event.start for event in series)
        last_end_ms = max(event.end for event in series)
    else:
        first_start_ms = None
        last_end_ms = None
    return SubtitleStreamStats(
        event_count=len(series),
        first_start_ms=first_start_ms,
        last_end_ms=last_end_ms,
    )
