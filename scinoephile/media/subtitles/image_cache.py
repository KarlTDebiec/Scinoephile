#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Media-backed rendered image subtitle cache."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from shutil import rmtree
from uuid import uuid4

from scinoephile.core.media import SubtitleStream
from scinoephile.image.subtitles import ImageSeries
from scinoephile.image.subtitles.cache import (
    IMAGE_SERIES_CACHE_VERSION,
    is_valid_image_subtitle_cache,
    save_image_subtitle_manifest,
)
from scinoephile.media.subtitles.cache import (
    cache_subtitle_streams,
    get_cached_subtitle_stream_path,
)

__all__ = ["get_or_create_image_subtitle_dir_path"]

logger = getLogger(__name__)


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

    stream_path = get_cached_subtitle_stream_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    cache_subtitle_streams(
        infile_path,
        [stream],
        cache_dir_path=cache_dir_path,
    )

    image_series = ImageSeries.load(stream_path)
    first_start_ms = None
    last_end_ms = None
    if image_series:
        first_start_ms = min(event.start for event in image_series)
        last_end_ms = max(event.end for event in image_series)

    image_dir_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir_path = image_dir_path.parent / f"{image_dir_path.name}-tmp-{uuid4().hex}"
    image_series.save(temp_dir_path)
    save_image_subtitle_manifest(
        {
            "version": IMAGE_SERIES_CACHE_VERSION,
            "event_count": len(image_series),
            "image_count": len(list(temp_dir_path.glob("*.png"))),
            "first_start_ms": first_start_ms,
            "last_end_ms": last_end_ms,
            "source_name": stream_path.name,
            "source_size": stream_path.stat().st_size,
        },
        temp_dir_path,
    )
    if image_dir_path.exists():
        rmtree(image_dir_path)
    temp_dir_path.replace(image_dir_path)
    logger.info(f"Saved image subtitle series to cache: {image_dir_path}")
    return image_dir_path


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
        get_cached_subtitle_stream_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        ).parent
        / "image-series"
    )
