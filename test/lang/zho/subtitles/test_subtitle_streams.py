#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Chinese subtitle stream helpers."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scinoephile.core.media import AudioStream, SubtitleStream, VideoStream
from scinoephile.lang.zho.subtitles.streams import get_zho_subtitle_streams


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
            "scinoephile.lang.zho.subtitles.streams.get_detailed_subtitle_streams",
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
        ) as details_mock,
        patch(
            "scinoephile.lang.zho.subtitles.streams.analyze_zho_subtitle_stream_script",
            return_value=SimpleNamespace(script="zho-Hant"),
        ) as analysis_mock,
    ):
        streams = get_zho_subtitle_streams(
            infile_path,
            cache_dir_path=cache_dir_path,
        )

    details_mock.assert_called_once_with(
        infile_path,
        cache_dir_path=cache_dir_path / "media" / "subtitles",
        overwrite_cache=False,
        streams=None,
    )
    analysis_mock.assert_called_once_with(
        infile_path,
        streams[0],
        cache_dir_path=cache_dir_path,
        overwrite_cache=False,
        subtitle_cache_is_fresh=False,
    )
    assert [stream.index for stream in streams] == [2, 3]
    assert streams[0].language == "zho-Hant"
    assert streams[0].subtitle_count == 12
    assert streams[0].span == "00:01:02-01:02:05"
    assert streams[1].language == "eng"
    assert streams[1].subtitle_count == 8


def test_get_zho_subtitle_streams_preserves_yue_language(tmp_path: Path):
    """Test Chinese stream probing preserves Yue while adding detected script.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")

    with (
        patch(
            "scinoephile.lang.zho.subtitles.streams.get_detailed_subtitle_streams",
            return_value=[
                SubtitleStream(
                    index=2,
                    codec_name="subrip",
                    language="yue",
                ),
            ],
        ),
        patch(
            "scinoephile.lang.zho.subtitles.streams.analyze_zho_subtitle_stream_script",
            return_value=SimpleNamespace(script="zho-Hant"),
        ),
    ):
        streams = get_zho_subtitle_streams(infile_path)

    assert streams[0].language == "yue-Hant"


def test_get_zho_subtitle_streams_does_not_overwrite_subtitle_cache_twice(
    tmp_path: Path,
):
    """Test script analysis reuses subtitle cache refreshed during detail probing.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, codec_name="subrip", language="zho")

    with (
        patch(
            "scinoephile.lang.zho.subtitles.streams.get_detailed_subtitle_streams",
            return_value=[stream],
        ) as details_mock,
        patch(
            "scinoephile.lang.zho.subtitles.streams.analyze_zho_subtitle_stream_script",
            return_value=SimpleNamespace(script="zho-Hant"),
        ) as analysis_mock,
    ):
        get_zho_subtitle_streams(infile_path, overwrite_cache=True)

    details_mock.assert_called_once_with(
        infile_path,
        cache_dir_path=None,
        overwrite_cache=True,
        streams=None,
    )
    analysis_mock.assert_called_once_with(
        infile_path,
        stream,
        cache_dir_path=None,
        overwrite_cache=True,
        subtitle_cache_is_fresh=True,
    )


def test_get_zho_subtitle_streams_normalizes_chi_language(tmp_path: Path):
    """Test Chinese stream probing replaces chi with zho before adding script.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")

    with (
        patch(
            "scinoephile.lang.zho.subtitles.streams.get_detailed_subtitle_streams",
            return_value=[
                SubtitleStream(
                    index=2,
                    codec_name="subrip",
                    language="chi",
                ),
            ],
        ),
        patch(
            "scinoephile.lang.zho.subtitles.streams.analyze_zho_subtitle_stream_script",
            return_value=SimpleNamespace(script=None),
        ),
    ):
        streams = get_zho_subtitle_streams(infile_path)

    assert streams[0].language == "zho-Unknown"


def test_get_zho_subtitle_streams_uses_provided_streams(tmp_path: Path):
    """Test Chinese stream probing reuses provided mixed streams.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    streams = [
        VideoStream(index=0, codec_type="video", codec_name="h264"),
        AudioStream(index=1, codec_type="audio", codec_name="aac"),
        SubtitleStream(
            index=2,
            codec_type="subtitle",
            codec_name="subrip",
            language="zho",
        ),
    ]

    with (
        patch(
            "scinoephile.lang.zho.subtitles.streams.get_detailed_subtitle_streams",
            return_value=[streams[2]],
        ),
        patch(
            "scinoephile.lang.zho.subtitles.streams.analyze_zho_subtitle_stream_script",
            return_value=SimpleNamespace(script="zho-Hant"),
        ),
    ):
        zho_streams = get_zho_subtitle_streams(infile_path, streams=streams)

    assert [stream.index for stream in zho_streams] == [2]
    assert zho_streams[0].language == "zho-Hant"
