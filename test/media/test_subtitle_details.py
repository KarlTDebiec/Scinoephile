#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle stream detail enrichment."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scinoephile.media.subtitles.details import with_stream_details

from scinoephile.core.media import SubtitleStream, VideoStream


def test_with_stream_details_enriches_subtitle_streams(tmp_path: Path):
    """Test stream detail enrichment includes subtitle script and stats."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    cache_dir_path = tmp_path / "cache"
    streams = [
        VideoStream(index=0, codec_name="h264"),
        SubtitleStream(index=2, codec_name="subrip", language="zho"),
    ]

    with (
        patch("scinoephile.media.subtitles.details.cache_subtitle_streams") as cache,
        patch(
            "scinoephile.media.subtitles.details.analyze_subtitle_stream_script",
            return_value=SimpleNamespace(script="zho-Hant"),
        ) as analyze,
        patch(
            "scinoephile.media.subtitles.details.get_subtitle_stream_stats",
            return_value=SimpleNamespace(
                event_count=12,
                first_start_ms=62_500,
                last_end_ms=3_725_250,
            ),
        ) as stats,
    ):
        detailed_streams = with_stream_details(
            infile_path,
            streams,
            cache_dir_path=cache_dir_path,
        )

    assert detailed_streams[0] is streams[0]
    assert isinstance(detailed_streams[1], SubtitleStream)
    assert detailed_streams[1].language == "zho-Hant"
    assert detailed_streams[1].subtitle_count == 12
    assert detailed_streams[1].span == "00:01:02-01:02:05"
    cache.assert_called_once()
    assert [stream.index for stream in cache.call_args.args[1]] == [2]
    assert cache.call_args.kwargs == {"cache_dir_path": cache_dir_path}
    analyze.assert_called_once()
    assert analyze.call_args.kwargs == {"cache_dir_path": cache_dir_path}
    stats.assert_called_once()
    assert stats.call_args.kwargs == {"cache_dir_path": cache_dir_path}
