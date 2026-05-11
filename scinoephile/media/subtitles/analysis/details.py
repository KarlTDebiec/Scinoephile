#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream detail enrichment."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from logging import getLogger
from pathlib import Path

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.media import Stream, SubtitleStream
from scinoephile.lang.zho.language import get_zho_script_language, is_zho_language
from scinoephile.media.subtitles.cache import cache_subtitle_stream_artifacts

from .script import analyze_subtitle_stream_script
from .stats import get_subtitle_stream_stats

__all__ = [
    "with_stream_details",
    "with_subtitle_details",
]

logger = getLogger(__name__)


def with_stream_details(
    infile_path: Path,
    streams: Iterable[Stream],
    *,
    cache_dir_path: Path | None = None,
) -> list[Stream]:
    """Return stream metadata enriched with expensive subtitle details.

    Arguments:
        infile_path: media input file to inspect
        streams: streams to enrich
        cache_dir_path: cache directory path
    Returns:
        enriched stream metadata, with non-subtitle streams passed through unchanged
    """
    stream_list = list(streams)
    subtitle_streams = []
    for stream in stream_list:
        if isinstance(stream, SubtitleStream):
            subtitle_streams.append(stream)  # noqa: PERF401

    if subtitle_streams:
        cache_subtitle_stream_artifacts(
            infile_path,
            subtitle_streams,
            cache_dir_path=cache_dir_path,
        )

    detailed_streams = []
    for stream in stream_list:
        if isinstance(stream, SubtitleStream):
            detailed_streams.append(
                with_subtitle_details(
                    infile_path,
                    stream,
                    cache_dir_path=cache_dir_path,
                )
            )
        else:
            detailed_streams.append(stream)
    return detailed_streams


def with_subtitle_details(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None = None,
) -> SubtitleStream:
    """Return subtitle stream metadata enriched with script and statistics.

    Arguments:
        infile_path: media input file to inspect
        stream: subtitle stream to enrich
        cache_dir_path: cache directory path
    Returns:
        enriched subtitle stream metadata
    """
    if stream.language is not None and is_zho_language(stream.language):
        analysis = analyze_subtitle_stream_script(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        )
        stream = replace(
            stream,
            language=get_zho_script_language(stream.language, analysis.script),
        )
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
        return stream
    return replace(
        stream,
        subtitle_count=stats.event_count,
        first_start_ms=stats.first_start_ms,
        last_end_ms=stats.last_end_ms,
    )
