#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle artifact cache."""

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
    "SUBTITLE_ARTIFACT_CACHE_VERSION",
    "cache_subtitle_stream_artifacts",
    "get_cached_subtitle_artifact_path",
]

logger = getLogger(__name__)

SUBTITLE_ARTIFACT_CACHE_VERSION = 1
"""Subtitle artifact cache schema version."""


def cache_subtitle_stream_artifacts(
    infile_path: Path,
    streams: list[SubtitleStream],
    *,
    cache_dir_path: Path | None = None,
):
    """Cache extracted subtitle stream artifacts using one ffmpeg command.

    Arguments:
        infile_path: media input file
        streams: subtitle streams to cache
        cache_dir_path: cache directory path
    """
    missing: list[tuple[SubtitleStream, Path]] = []
    for stream in streams:
        artifact_path = get_cached_subtitle_artifact_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        )
        if not _is_valid_subtitle_artifact_cache(artifact_path):
            missing.append((stream, artifact_path))
        else:
            logger.info(f"Loaded subtitle artifact from cache: {artifact_path}")

    if not missing:
        return

    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("media", "subtitles")
    temp_dir_path = cache_dir_path / f"subtitle-artifacts-tmp-{uuid4().hex}"
    temp_dir_path.mkdir(parents=True, exist_ok=False)
    temp_artifact_paths: list[tuple[Path, Path]] = []
    command = ["ffmpeg", "-y", "-i", str(infile_path)]
    for stream, artifact_path in missing:
        temp_artifact_path = temp_dir_path / artifact_path.name
        temp_artifact_paths.append((temp_artifact_path, artifact_path))
        command.extend(
            [
                "-map",
                f"0:{stream.index}",
                "-c:s",
                stream.output_codec,
                str(temp_artifact_path),
            ]
        )
    try:
        run_command(command)
        for temp_artifact_path, artifact_path in temp_artifact_paths:
            if temp_artifact_path.exists():
                artifact_path.parent.mkdir(parents=True, exist_ok=True)
                temp_artifact_path.replace(artifact_path)
            logger.info(f"Saved subtitle artifact to cache: {artifact_path}")
    finally:
        rmtree(temp_dir_path, ignore_errors=True)


def get_cached_subtitle_artifact_path(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None = None,
) -> Path:
    """Get the cache path for an extracted subtitle stream artifact.

    Arguments:
        infile_path: media input file
        stream: subtitle stream
        cache_dir_path: cache directory path
    Returns:
        subtitle artifact cache path
    """
    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("media", "subtitles")
    cache_key = _get_subtitle_stream_cache_key(infile_path, stream)
    return cache_dir_path / cache_key / f"{stream.index}.{stream.extension}"


def _get_subtitle_stream_cache_key(
    infile_path: Path,
    stream: SubtitleStream,
) -> str:
    """Get a stable cache key for extracted subtitle artifacts.

    Arguments:
        infile_path: media input file
        stream: subtitle stream
    Returns:
        hexadecimal cache key
    """
    resolved_path = infile_path.resolve()
    stat = resolved_path.stat()
    payload = {
        "path": str(resolved_path),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "stream_index": stream.index,
        "codec_name": stream.codec_name,
        "subtitle_artifact_cache_version": SUBTITLE_ARTIFACT_CACHE_VERSION,
    }
    encoded_payload = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded_payload).hexdigest()


def _is_valid_subtitle_artifact_cache(artifact_path: Path) -> bool:
    """Check whether an extracted subtitle artifact cache is valid.

    Arguments:
        artifact_path: extracted subtitle artifact cache path
    Returns:
        whether the artifact cache is valid
    """
    try:
        return artifact_path.stat().st_size > 0
    except FileNotFoundError:
        return False
