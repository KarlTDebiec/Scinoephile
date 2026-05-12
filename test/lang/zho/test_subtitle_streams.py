#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Chinese subtitle stream helpers."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scinoephile.core.media import AudioStream, SubtitleStream, VideoStream
from scinoephile.lang.zho.subtitle_streams import get_zho_subtitle_streams


def test_get_zho_subtitle_streams_adds_script_and_regular_details(tmp_path: Path):
    """Test Chinese stream probing enriches script and regular details.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    cache_dir_path = tmp_path / "cache"

    with (
        patch(
            "scinoephile.lang.zho.subtitle_streams.get_streams",
            return_value=[
                VideoStream(index=0, codec_name="h264"),
                AudioStream(index=1, codec_name="aac", language="eng"),
                SubtitleStream(index=2, codec_name="subrip", language="zho"),
                SubtitleStream(index=3, codec_name="subrip", language="eng"),
            ],
        ) as get_streams,
        patch(
            "scinoephile.lang.zho.subtitle_streams.analyze_zho_subtitle_stream_script",
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
        patch("scinoephile.media.subtitles.details.cache_subtitle_streams"),
    ):
        streams = get_zho_subtitle_streams(
            infile_path,
            cache_dir_path=cache_dir_path,
        )

    get_streams.assert_called_once_with(infile_path)
    analyze.assert_called_once()
    assert analyze.call_args.args[1].index == 2
    assert analyze.call_args.kwargs == {"cache_dir_path": cache_dir_path}
    assert stats.call_count == 2
    assert [stream.index for stream in streams] == [2, 3]
    assert streams[0].language == "zho-Hant"
    assert streams[0].subtitle_count == 12
    assert streams[0].span == "00:01:02-01:02:05"
    assert streams[1].language == "eng"
    assert streams[1].subtitle_count == 12
