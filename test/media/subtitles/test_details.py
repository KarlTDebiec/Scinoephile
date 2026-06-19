#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle stream detail enrichment."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scinoephile.core.media import AudioStream, SubtitleStream, VideoStream
from scinoephile.media.subtitles.details import get_detailed_subtitle_streams


def test_get_detailed_subtitle_streams_enriches_subtitle_stats(tmp_path: Path):
    """Test detailed subtitle stream probing includes neutral subtitle stats."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    cache_dir_path = tmp_path / "cache"
    subtitle_streams = [
        SubtitleStream(index=2, codec_name="subrip", language="zho"),
    ]

    with (
        patch(
            "scinoephile.media.subtitles.details.get_subtitle_streams",
            return_value=subtitle_streams,
        ),
        patch("scinoephile.media.subtitles.details.cache_subtitles"),
        patch(
            "scinoephile.media.subtitles.details.get_subtitle_stream_stats",
            return_value=SimpleNamespace(
                event_count=12,
                first_start_ms=62_500,
                last_end_ms=3_725_250,
            ),
        ),
    ):
        detailed_streams = get_detailed_subtitle_streams(
            infile_path,
            cache_dir_path=cache_dir_path,
        )

    assert len(detailed_streams) == 1
    assert detailed_streams[0].language == "zho"
    assert detailed_streams[0].subtitle_count == 12
    assert detailed_streams[0].span == "00:01:02-01:02:05"


def test_get_detailed_subtitle_streams_uses_provided_subtitle_streams(
    tmp_path: Path,
):
    """Test detailed subtitle enrichment can reuse provided mixed streams.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    cache_dir_path = tmp_path / "cache"
    streams = [
        VideoStream(index=0, codec_type="video", codec_name="h264"),
        AudioStream(index=1, codec_type="audio", codec_name="aac"),
        SubtitleStream(index=2, codec_type="subtitle", codec_name="subrip"),
    ]

    with (
        patch(
            "scinoephile.media.subtitles.details.get_subtitle_streams",
        ),
        patch("scinoephile.media.subtitles.details.cache_subtitles"),
        patch(
            "scinoephile.media.subtitles.details.get_subtitle_stream_stats",
            return_value=SimpleNamespace(
                event_count=12,
                first_start_ms=62_500,
                last_end_ms=3_725_250,
            ),
        ),
    ):
        detailed_streams = get_detailed_subtitle_streams(
            infile_path,
            cache_dir_path=cache_dir_path,
            streams=streams,
        )

    assert [stream.index for stream in detailed_streams] == [2]
    assert detailed_streams[0].subtitle_count == 12
