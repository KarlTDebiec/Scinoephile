#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle stream stats."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from PIL import Image

from scinoephile.core.media import SubtitleStream
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from scinoephile.media.subtitles.cache import get_subtitle_cache_path
from scinoephile.media.subtitles.stats import get_subtitle_stream_stats


def test_get_text_subtitle_stream_stats_from_cached_stream(tmp_path: Path):
    """Test text subtitle stream stats read cached extracted subtitles.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    _cache_subtitle_stream(
        infile_path,
        stream,
        tmp_path / "cache",
        (
            "1\n00:00:02,500 --> 00:00:04,000\n第一行\n\n"
            "2\n00:01:02,000 --> 00:01:05,250\n第二行\n"
        ),
    )

    with patch("scinoephile.media.subtitles.cache.ffmpeg.input") as ffmpeg_input:
        stats = get_subtitle_stream_stats(
            infile_path,
            stream,
            cache_dir_path=tmp_path / "cache",
        )

    ffmpeg_input.assert_not_called()
    assert stats.event_count == 2
    assert stats.first_start_ms == 2500
    assert stats.last_end_ms == 65250


def test_get_image_subtitle_stream_stats_from_cached_images(tmp_path: Path):
    """Test image subtitle stats read cached rendered images.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="hdmv_pgs_subtitle")
    _cache_image_subtitles(
        infile_path,
        stream,
        tmp_path / "cache",
        event_count=7,
        first_start_ms=2500,
        last_end_ms=65_250,
    )

    stats = get_subtitle_stream_stats(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )

    assert stats.event_count == 7
    assert stats.first_start_ms == 2500
    assert stats.last_end_ms == 65250


def _cache_image_subtitles(
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
    _cache_subtitle_stream(infile_path, stream, cache_dir_path, b"not a real sup")
    image_dir_path = (
        get_subtitle_cache_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        ).parent
        / "image-series"
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


def _cache_subtitle_stream(
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
