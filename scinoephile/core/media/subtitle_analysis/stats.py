#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream statistics."""

from __future__ import annotations

import json
from logging import getLogger
from pathlib import Path

from scinoephile.core.media.subtitle_stream import SubtitleStream
from scinoephile.core.subtitles import Series
from scinoephile.image.subtitles import ImageSeries

from .artifacts import (
    cache_subtitle_stream_artifacts,
    get_cached_subtitle_artifact_path,
    is_valid_subtitle_artifact_cache,
)
from .image_cache import (
    get_or_create_image_subtitle_dir_path,
    load_image_subtitle_manifest,
    save_image_subtitle_manifest,
    update_image_subtitle_stats_from_html,
)
from .types import SubtitleStatsCache, SubtitleStreamStats

__all__ = [
    "SUBTITLE_STATS_CACHE_VERSION",
    "count_subtitle_stream_events",
    "format_stream_span_time",
    "get_subtitle_series_stats",
    "get_subtitle_stream_stats",
]

logger = getLogger(__name__)

IMAGE_SUBTITLE_EXTENSIONS = {"sup"}
"""Subtitle artifact extensions that contain image subtitles."""
SUBTITLE_STATS_CACHE_VERSION = 1
"""Subtitle stats cache schema version."""


def count_subtitle_stream_events(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None = None,
) -> int:
    """Count subtitle events in a subtitle stream using cached artifacts.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to count
        cache_dir_path: cache directory path
    Returns:
        number of subtitle events
    """
    return get_subtitle_stream_stats(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    ).event_count


def format_stream_span_time(time_ms: int) -> str:
    """Format a stream span timestamp.

    Arguments:
        time_ms: time in milliseconds
    Returns:
        timestamp formatted as HH:MM:SS
    """
    total_seconds = time_ms // 1000
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_subtitle_series_stats(series: Series | ImageSeries) -> SubtitleStreamStats:
    """Get subtitle stats from a loaded subtitle series.

    Arguments:
        series: loaded subtitle series
    Returns:
        subtitle stream statistics
    """
    return SubtitleStreamStats(
        event_count=len(series),
        first_start_ms=get_first_start_ms(series),
        last_end_ms=get_last_end_ms(series),
    )


def get_subtitle_stream_stats(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None = None,
) -> SubtitleStreamStats:
    """Get subtitle stream event count and span from cached artifacts.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to inspect
        cache_dir_path: cache directory path
    Returns:
        subtitle stream statistics
    """
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    if not is_valid_subtitle_artifact_cache(artifact_path):
        cache_subtitle_stream_artifacts(
            infile_path,
            [stream],
            cache_dir_path=cache_dir_path,
        )

    if stream.extension in IMAGE_SUBTITLE_EXTENSIONS:
        image_dir_path = get_or_create_image_subtitle_dir_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        )
        return get_image_subtitle_stats(image_dir_path)

    stats_cache_path = artifact_path.parent / "stats.json"
    if is_valid_subtitle_stats_cache(stats_cache_path):
        logger.info(f"Loaded subtitle stats from cache: {stats_cache_path}")
        return load_subtitle_stats_cache(stats_cache_path)

    stats = get_subtitle_series_stats(Series.load(artifact_path))
    save_subtitle_stats_cache(stats, stats_cache_path)
    logger.info(f"Saved subtitle stats to cache: {stats_cache_path}")
    return stats


def get_first_start_ms(series: Series | ImageSeries) -> int | None:
    """Get first subtitle start time from a series.

    Arguments:
        series: loaded subtitle series
    Returns:
        first subtitle start time in milliseconds, if available
    """
    if not series:
        return None
    return min(event.start for event in series)


def get_image_subtitle_stats(image_dir_path: Path) -> SubtitleStreamStats:
    """Get image subtitle stats from cached manifest or HTML metadata.

    Arguments:
        image_dir_path: rendered image subtitle cache directory path
    Returns:
        subtitle stream statistics
    """
    manifest = load_image_subtitle_manifest(image_dir_path)
    if "first_start_ms" not in manifest or "last_end_ms" not in manifest:
        manifest = update_image_subtitle_stats_from_html(image_dir_path, manifest)
    return SubtitleStreamStats(
        event_count=int(manifest["event_count"]),
        first_start_ms=manifest.get("first_start_ms"),
        last_end_ms=manifest.get("last_end_ms"),
    )


def get_last_end_ms(series: Series | ImageSeries) -> int | None:
    """Get last subtitle end time from a series.

    Arguments:
        series: loaded subtitle series
    Returns:
        last subtitle end time in milliseconds, if available
    """
    if not series:
        return None
    return max(event.end for event in series)


def is_valid_subtitle_stats_cache(cache_path: Path) -> bool:
    """Check whether a subtitle stats cache is valid.

    Arguments:
        cache_path: stats cache path
    Returns:
        whether the cache is valid
    """
    try:
        cache = load_subtitle_stats_cache(cache_path)
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False
    if cache.event_count < 0:
        return False
    return True


def load_subtitle_stats_cache(cache_path: Path) -> SubtitleStreamStats:
    """Load subtitle stats from cache.

    Arguments:
        cache_path: stats cache path
    Returns:
        subtitle stream statistics
    """
    with cache_path.open("r", encoding="utf-8") as file:
        raw = json.load(file)
    if int(raw["version"]) != SUBTITLE_STATS_CACHE_VERSION:
        raise ValueError(f"Unsupported subtitle stats cache version: {raw['version']}")
    first_start_ms = raw["first_start_ms"]
    if first_start_ms is not None:
        first_start_ms = int(first_start_ms)
    last_end_ms = raw["last_end_ms"]
    if last_end_ms is not None:
        last_end_ms = int(last_end_ms)
    return SubtitleStreamStats(
        event_count=int(raw["event_count"]),
        first_start_ms=first_start_ms,
        last_end_ms=last_end_ms,
    )


def save_subtitle_stats_cache(
    stats: SubtitleStreamStats,
    cache_path: Path,
):
    """Save subtitle stats to cache.

    Arguments:
        stats: subtitle stream statistics
        cache_path: stats cache path
    """
    cache: SubtitleStatsCache = {
        "version": SUBTITLE_STATS_CACHE_VERSION,
        "event_count": stats.event_count,
        "first_start_ms": stats.first_start_ms,
        "last_end_ms": stats.last_end_ms,
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False, sort_keys=True)


def save_image_subtitle_stats_cache(
    stats: SubtitleStreamStats,
    image_dir_path: Path,
):
    """Save image subtitle stats into the rendered manifest.

    Arguments:
        stats: subtitle stream statistics
        image_dir_path: rendered image subtitle cache directory path
    """
    manifest = load_image_subtitle_manifest(image_dir_path)
    manifest["first_start_ms"] = stats.first_start_ms
    manifest["last_end_ms"] = stats.last_end_ms
    save_image_subtitle_manifest(manifest, image_dir_path)
