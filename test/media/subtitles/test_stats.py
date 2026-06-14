#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle stream stats."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scinoephile.core.media import SubtitleStream
from scinoephile.media.subtitles.stats import get_subtitle_stream_stats
from test.helpers.media_subtitles import cache_image_subtitles, cache_subtitle_stream


def test_get_text_subtitle_stream_stats_from_cached_stream(tmp_path: Path):
    """Test text subtitle stream stats read cached extracted subtitles.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache_subtitle_stream(
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
    cache_image_subtitles(
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
