#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream statistics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scinoephile.core.media import SubtitleStream
from scinoephile.core.subtitles import Series
from scinoephile.media.subtitles.cache import (
    cache_subtitle_streams,
    get_cached_subtitle_stream_path,
    get_or_create_image_subtitle_dir_path,
    load_image_subtitle_manifest,
)

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
    if stream.extension == "sup":
        image_dir_path = get_or_create_image_subtitle_dir_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        )
        return _get_image_subtitle_stats(image_dir_path)

    cache_subtitle_streams(
        infile_path,
        [stream],
        cache_dir_path=cache_dir_path,
    )
    stream_path = get_cached_subtitle_stream_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    return _get_subtitle_series_stats(Series.load(stream_path))


def _get_first_start_ms(series: Series) -> int | None:
    """Get first subtitle start time from a series.

    Arguments:
        series: loaded subtitle series
    Returns:
        first subtitle start time in milliseconds, if available
    """
    if not series:
        return None
    return min(event.start for event in series)


def _get_image_subtitle_stats(image_dir_path: Path) -> SubtitleStreamStats:
    """Get image subtitle stats from cached manifest or HTML metadata.

    Arguments:
        image_dir_path: rendered image subtitle cache directory path
    Returns:
        subtitle stream statistics
    """
    manifest = load_image_subtitle_manifest(image_dir_path)
    return SubtitleStreamStats(
        event_count=int(manifest["event_count"]),
        first_start_ms=manifest.get("first_start_ms"),
        last_end_ms=manifest.get("last_end_ms"),
    )


def _get_last_end_ms(series: Series) -> int | None:
    """Get last subtitle end time from a series.

    Arguments:
        series: loaded subtitle series
    Returns:
        last subtitle end time in milliseconds, if available
    """
    if not series:
        return None
    return max(event.end for event in series)


def _get_subtitle_series_stats(series: Series) -> SubtitleStreamStats:
    """Get subtitle stats from a loaded subtitle series.

    Arguments:
        series: loaded subtitle series
    Returns:
        subtitle stream statistics
    """
    return SubtitleStreamStats(
        event_count=len(series),
        first_start_ms=_get_first_start_ms(series),
        last_end_ms=_get_last_end_ms(series),
    )
