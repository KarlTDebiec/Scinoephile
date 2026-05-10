#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Media stream probing utilities."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import Any, cast

import ffmpeg

from scinoephile.core.exceptions import ScinoephileError

from .stream import Stream
from .subtitle_analysis import (
    analyze_subtitle_stream_script,
    cache_subtitle_stream_artifacts,
    get_subtitle_stream_stats,
)
from .subtitle_stream import SubtitleStream

__all__ = ["get_media_streams"]

logger = getLogger(__name__)


def get_media_streams(
    infile_path: Path,
    *,
    details: bool = False,
    cache_dir_path: Path | None = None,
) -> list[Stream]:
    """Return stream objects in a media file.

    Arguments:
        infile_path: media input file to inspect
        details: whether to include expensive additional details
        cache_dir_path: cache directory path
    Returns:
        media stream metadata
    Raises:
        ScinoephileError: if ffprobe fails
    """
    try:
        probe = ffmpeg.probe(str(infile_path))
    except ffmpeg.Error as exc:
        raise ScinoephileError(f"Could not probe media file {infile_path}") from exc

    streams = []
    for stream in probe.get("streams", []):
        if not isinstance(stream, dict):
            continue
        parsed_stream = Stream.from_ffprobe_stream(cast("dict[str, Any]", stream))
        if parsed_stream is None:
            continue
        if isinstance(parsed_stream, SubtitleStream):
            parsed_stream = parsed_stream.without_stats()
        streams.append(parsed_stream)

    if details:
        return _with_details(
            infile_path,
            streams,
            cache_dir_path=cache_dir_path,
        )
    return streams


def _with_details(
    infile_path: Path,
    streams: list[Stream],
    *,
    cache_dir_path: Path | None = None,
) -> list[Stream]:
    """Return media stream metadata enriched with expensive details.

    Arguments:
        infile_path: media input file to inspect
        streams: media streams to enrich
        cache_dir_path: cache directory path
    Returns:
        enriched media stream metadata
    """
    subtitle_streams = [
        stream for stream in streams if isinstance(stream, SubtitleStream)
    ]
    if subtitle_streams:
        cache_subtitle_stream_artifacts(
            infile_path,
            subtitle_streams,
            cache_dir_path=cache_dir_path,
        )
    return [
        _with_subtitle_details(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        )
        if isinstance(stream, SubtitleStream)
        else stream
        for stream in streams
    ]


def _with_subtitle_details(
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
    if stream.is_chinese:
        analysis = analyze_subtitle_stream_script(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        )
        stream = stream.with_script(analysis.script)
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
    return stream.with_stats(
        subtitle_count=stats.event_count,
        first_start_ms=stats.first_start_ms,
        last_end_ms=stats.last_end_ms,
    )
