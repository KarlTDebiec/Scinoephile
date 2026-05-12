#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Chinese subtitle stream helpers."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scinoephile.core.media import SubtitleStream
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
            "scinoephile.lang.zho.subtitle_streams.get_detailed_subtitle_streams",
            return_value=[
                SubtitleStream(
                    index=2,
                    codec_name="subrip",
                    language="zho",
                    subtitle_count=12,
                    first_start_ms=62_500,
                    last_end_ms=3_725_250,
                ),
                SubtitleStream(
                    index=3,
                    codec_name="subrip",
                    language="eng",
                    subtitle_count=8,
                ),
            ],
        ) as get_detailed_subtitle_streams,
        patch(
            "scinoephile.lang.zho.subtitle_streams.analyze_zho_subtitle_stream_script",
            return_value=SimpleNamespace(script="zho-Hant"),
        ) as analyze,
    ):
        streams = get_zho_subtitle_streams(
            infile_path,
            cache_dir_path=cache_dir_path,
        )

    get_detailed_subtitle_streams.assert_called_once_with(
        infile_path,
        cache_dir_path=cache_dir_path,
    )
    analyze.assert_called_once()
    assert analyze.call_args.args[1].index == 2
    assert analyze.call_args.kwargs == {"cache_dir_path": cache_dir_path}
    assert [stream.index for stream in streams] == [2, 3]
    assert streams[0].language == "zho-Hant"
    assert streams[0].subtitle_count == 12
    assert streams[0].span == "00:01:02-01:02:05"
    assert streams[1].language == "eng"
    assert streams[1].subtitle_count == 8
