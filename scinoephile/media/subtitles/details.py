#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream detail enrichment."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from logging import getLogger
from pathlib import Path

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.media import Stream, SubtitleStream
from scinoephile.media.probe import get_subtitle_streams

from .cache import cache_subtitles
from .stats import get_subtitle_stream_stats

__all__ = ["get_detailed_subtitle_streams"]

logger = getLogger(__name__)


def get_detailed_subtitle_streams(
    infile_path: Path,
    *,
    cache_dir_path: Path | None = None,
    overwrite_cache: bool = False,
    streams: Sequence[Stream] | None = None,
) -> list[SubtitleStream]:
    """Get subtitle stream metadata enriched with expensive subtitle details.

    Arguments:
        infile_path: media input file to inspect
        cache_dir_path: cache directory path
        overwrite_cache: whether to replace matching cached subtitle artifacts
        streams: optional pre-probed media streams
    Returns:
        enriched subtitle stream metadata
    """
    if streams is None:
        subtitle_streams = get_subtitle_streams(infile_path)
    else:
        subtitle_streams = [
            stream for stream in streams if isinstance(stream, SubtitleStream)
        ]
    if subtitle_streams:
        cache_subtitles(
            infile_path,
            subtitle_streams,
            cache_dir_path=cache_dir_path,
            overwrite_cache=overwrite_cache,
        )

    detailed_streams = []
    for stream in subtitle_streams:
        try:
            stats = get_subtitle_stream_stats(
                infile_path,
                stream,
                cache_dir_path=cache_dir_path,
            )
        except (ScinoephileError, ValueError, IndexError) as exc:
            logger.warning(
                f"Could not read subtitle stats for stream #{stream.index}: {exc}"
            )
            detailed_streams.append(stream)
            continue
        detailed_streams.append(
            replace(
                stream,
                subtitle_count=stats.event_count,
                first_start_ms=stats.first_start_ms,
                last_end_ms=stats.last_end_ms,
            )
        )
    return detailed_streams
