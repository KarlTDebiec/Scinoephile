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

import ffmpeg
from PIL import Image

from scinoephile.core.media import SubtitleStream
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

__all__ = [
    "cache_subtitles",
    "get_subtitle_cache_path",
    "get_or_create_image_subtitle_dir_path",
    "is_valid_image_subtitle_cache",
    "load_cached_image_subtitles",
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

    # If nothing to do, return early
    if not missing:
        return

    # Extract subtitle streams
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
    ffmpeg.merge_outputs(*output_streams).run(quiet=False, overwrite_output=True)
    for _, stream_path in missing:
        logger.info(f"Saved subtitle stream to cache: {stream_path}")


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


def get_or_create_image_subtitle_dir_path(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None,
) -> Path:
    """Get or create the rendered image subtitle cache directory.

    Arguments:
        infile_path: media input file
        stream: subtitle stream
        cache_dir_path: cache directory path
    Returns:
        rendered image subtitle cache directory path
    """
    image_dir_path = _get_cached_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    if is_valid_image_subtitle_cache(image_dir_path):
        logger.info(f"Loaded image subtitle series from cache: {image_dir_path}")
        return image_dir_path

    stream_path = get_subtitle_cache_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    cache_subtitles(infile_path, [stream], cache_dir_path=cache_dir_path)

    image_series = ImageSeries.load(stream_path)
    image_dir_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir_path = image_dir_path.parent / f"{image_dir_path.name}-tmp-{uuid4().hex}"
    image_series.save(temp_dir_path)
    if image_dir_path.exists():
        rmtree(image_dir_path)
    temp_dir_path.replace(image_dir_path)
    logger.info(f"Saved image subtitle series to cache: {image_dir_path}")
    return image_dir_path


def is_valid_image_subtitle_cache(image_dir_path: Path) -> bool:
    """Check whether a rendered image subtitle cache is valid.

    Arguments:
        image_dir_path: rendered image subtitle cache directory path
    Returns:
        whether the cache is valid
    """
    return image_dir_path.is_dir() and (image_dir_path / "index.html").exists()


def load_cached_image_subtitles(
    image_dir_path: Path,
    indexes: list[int],
) -> list[ImageSubtitle]:
    """Load selected cached image subtitle events.

    Arguments:
        image_dir_path: rendered image subtitle cache directory path
        indexes: zero-based subtitle event indexes
    Returns:
        image subtitle events
    """
    html_path = image_dir_path / "index.html"
    html_text = html_path.read_text(encoding="utf-8")
    html_events = ImageSeries._parse_html_events(html_text, image_dir_path)
    events = []
    for index in indexes:
        html_event = html_events[index]
        with Image.open(html_event["path"]) as opened:
            img = opened.copy()
        events.append(
            ImageSubtitle(
                start=html_event["start"],
                end=html_event["end"],
                img=img,
                text=html_event["text"],
            )
        )
    return events


def _get_cached_image_subtitle_dir_path(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None = None,
) -> Path:
    """Get the cache directory path for rendered image subtitles.

    Arguments:
        infile_path: media input file
        stream: subtitle stream
        cache_dir_path: cache directory path
    Returns:
        rendered image subtitle cache directory path
    """
    return (
        get_subtitle_cache_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        ).parent
        / "image-series"
    )
