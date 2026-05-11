#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream cache."""

from __future__ import annotations

import hashlib
import json
from logging import getLogger
from pathlib import Path
from shutil import rmtree
from uuid import uuid4

from scinoephile.common.subprocess import run_command
from scinoephile.core.media import SubtitleStream
from scinoephile.core.paths import get_runtime_cache_dir_path

__all__ = [
    "cache_subtitle_streams",
    "get_cached_subtitle_stream_path",
]

logger = getLogger(__name__)


def cache_subtitle_streams(
    infile_path: Path,
    streams: list[SubtitleStream],
    *,
    cache_dir_path: Path | None = None,
):
    """Cache extracted subtitle streams using one ffmpeg command.

    Arguments:
        infile_path: media input file
        streams: subtitle streams to cache
        cache_dir_path: cache directory path
    """
    missing: list[tuple[SubtitleStream, Path]] = []
    for stream in streams:
        stream_path = get_cached_subtitle_stream_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        )
        try:
            stream_is_cached = stream_path.stat().st_size > 0
        except FileNotFoundError:
            stream_is_cached = False
        if stream_is_cached:
            logger.info(f"Loaded subtitle stream from cache: {stream_path}")
        else:
            missing.append((stream, stream_path))

    if not missing:
        return

    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("media", "subtitles")
    temp_dir_path = cache_dir_path / f"subtitle-streams-tmp-{uuid4().hex}"
    temp_dir_path.mkdir(parents=True, exist_ok=False)
    temp_stream_paths: list[tuple[Path, Path]] = []
    command = ["ffmpeg", "-y", "-i", str(infile_path)]
    for stream, stream_path in missing:
        temp_stream_path = temp_dir_path / stream_path.name
        temp_stream_paths.append((temp_stream_path, stream_path))
        command.extend(
            [
                "-map",
                f"0:{stream.index}",
                "-c:s",
                stream.output_codec,
                str(temp_stream_path),
            ]
        )
    try:
        run_command(command)
        for temp_stream_path, stream_path in temp_stream_paths:
            if temp_stream_path.exists():
                stream_path.parent.mkdir(parents=True, exist_ok=True)
                temp_stream_path.replace(stream_path)
            logger.info(f"Saved subtitle stream to cache: {stream_path}")
    finally:
        rmtree(temp_dir_path, ignore_errors=True)


def get_cached_subtitle_stream_path(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None = None,
) -> Path:
    """Get the cache path for an extracted subtitle stream.

    Arguments:
        infile_path: media input file
        stream: subtitle stream
        cache_dir_path: cache directory path
    Returns:
        subtitle stream cache path
    """
    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("media", "subtitles")
    resolved_path = infile_path.resolve()
    stat = resolved_path.stat()
    payload = {
        "path": str(resolved_path),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "stream_index": stream.index,
        "codec_name": stream.codec_name,
    }
    encoded_payload = json.dumps(payload, sort_keys=True).encode("utf-8")
    cache_key = hashlib.sha256(encoded_payload).hexdigest()
    return cache_dir_path / cache_key / f"{stream.index}.{stream.extension}"
