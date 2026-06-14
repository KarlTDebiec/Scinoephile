#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared helpers for media subtitle tests."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from scinoephile.core.media import SubtitleStream
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from scinoephile.media.subtitles.cache import get_subtitle_cache_path


def cache_image_subtitles(
    infile_path: Path,
    stream: SubtitleStream,
    cache_dir_path: Path,
    *,
    event_count: int,
    first_start_ms: int | None = None,
    last_end_ms: int | None = None,
) -> Path:
    """Write cached SUP data and rendered image subtitles.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to cache
        cache_dir_path: cache directory path
        event_count: number of rendered subtitle events to write
        first_start_ms: start timestamp for the first event, if overridden
        last_end_ms: end timestamp for the final event, if overridden
    Returns:
        rendered image subtitle directory path
    """
    cache_subtitle_stream(infile_path, stream, cache_dir_path, b"not a real sup")
    image_dir_path = get_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    events: list[ImageSubtitle] = []
    for index in range(event_count):
        start = index * 10_000
        if index == 0 and first_start_ms is not None:
            start = first_start_ms
        end = index * 10_000 + 500
        if index == event_count - 1 and last_end_ms is not None:
            end = last_end_ms
        events.append(
            ImageSubtitle(
                start=start,
                end=end,
                img=Image.new("RGBA", (10 + index, 8), (255, 255, 255, 0)),
            )
        )
    ImageSeries(events=events).save(image_dir_path)
    return image_dir_path


def cache_subtitle_stream(
    infile_path: Path,
    stream: SubtitleStream,
    cache_dir_path: Path,
    data: bytes | str,
) -> Path:
    """Write a cached extracted subtitle stream.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to cache
        cache_dir_path: cache directory path
        data: data to write to the cached stream
    Returns:
        cached subtitle stream path
    """
    stream_path = get_subtitle_cache_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    stream_path.parent.mkdir(parents=True)
    if isinstance(data, bytes):
        stream_path.write_bytes(data)
    else:
        stream_path.write_text(data, encoding="utf-8")
    return stream_path


def get_image_subtitle_dir_path(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path,
) -> Path:
    """Get the image subtitle cache directory path used by the media cache.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to cache
        cache_dir_path: cache directory path
    Returns:
        cached image subtitle directory path
    """
    return (
        get_subtitle_cache_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        ).parent
        / "image-series"
    )
