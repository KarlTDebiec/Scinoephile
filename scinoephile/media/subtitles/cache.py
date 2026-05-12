#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream cache."""

from __future__ import annotations

import hashlib
import json
from logging import getLogger
from pathlib import Path

import ffmpeg

from scinoephile.core.media import SubtitleStream
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.image.subtitles import ImageSeries

__all__ = [
    "cache_subtitles",
    "get_subtitle_cache_path",
]

logger = getLogger(__name__)


def cache_subtitles(
    infile_path: Path,
    streams: list[SubtitleStream],
    *,
    cache_dir_path: Path | None = None,
):
    """Cache extracted subtitle streams.

    Arguments:
        infile_path: media input file
        streams: subtitle streams to cache
        cache_dir_path: cache directory path
    """
    # Validate arguments
    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("media", "subtitles")

    # Determine which subtitle streams are missing from cache and need to be extracted
    missing: list[tuple[SubtitleStream, Path]] = []
    for stream in streams:
        stream_path = get_subtitle_cache_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        )
        if stream_path.exists():
            logger.info(f"Loaded subtitle stream from cache: {stream_path}")
        else:
            missing.append((stream, stream_path))

    # Extract subtitle streams
    if missing:
        input_stream = ffmpeg.input(str(infile_path))
        output_streams = []
        for stream, stream_path in missing:
            if not stream_path.parent.exists():
                stream_path.parent.mkdir(parents=True)
                logger.info(f"Created cache directory: {stream_path.parent}")
            output_streams.append(
                input_stream.output(
                    str(stream_path),
                    **{
                        "map": f"0:{stream.index}",
                        "c:s": stream.output_codec,
                    },
                )
            )
        ffmpeg.merge_outputs(*output_streams).run(
            quiet=False,
            overwrite_output=True,
        )
        for _, stream_path in missing:
            logger.info(f"Saved subtitle stream to cache: {stream_path}")

    # Render cached SUP subtitle streams to image directories
    for stream in streams:
        if stream.extension != "sup":
            continue
        stream_path = get_subtitle_cache_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        )
        image_dir_path = stream_path.parent / "image-series"
        if (image_dir_path / "index.html").exists():
            logger.info(f"Loaded image subtitle series from cache: {image_dir_path}")
            continue
        image_series = ImageSeries.load(stream_path)
        image_series.save(image_dir_path)
        logger.info(f"Saved image subtitle series to cache: {image_dir_path}")


def get_subtitle_cache_path(
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
    # Validate arguments
    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("media", "subtitles")

    # Calculate stats, prepare key, and return path
    stat = infile_path.stat()
    payload = {
        "path": str(infile_path),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "stream_index": stream.index,
        "codec_name": stream.codec_name,
    }
    encoded_payload = json.dumps(payload, sort_keys=True).encode("utf-8")
    cache_key = hashlib.sha256(encoded_payload).hexdigest()
    return cache_dir_path / cache_key / f"{stream.index}.{stream.extension}"
