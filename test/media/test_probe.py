#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media probing utilities."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scinoephile.core.media import AudioStream, Stream, SubtitleStream, VideoStream
from scinoephile.media.probe import get_streams, get_subtitle_streams


def test_get_subtitle_streams(tmp_path: Path):
    """Test subtitle stream metadata parsing."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with patch(
        "scinoephile.media.probe.ffmpeg.probe",
        return_value={
            "streams": [
                {"index": 0, "codec_type": "video", "codec_name": "h264"},
                {
                    "index": 2,
                    "codec_type": "subtitle",
                    "codec_name": "subrip",
                    "tags": {"language": "ENG", "title": "English"},
                    "disposition": {"forced": 0, "hearing_impaired": 1},
                    "nb_read_packets": "123",
                },
            ],
        },
    ):
        streams = get_subtitle_streams(infile_path)

    assert len(streams) == 1
    stream = streams[0]
    assert stream.index == 2
    assert stream.language == "eng"
    assert stream.codec_name == "subrip"
    assert stream.title == "English"
    assert stream.sdh is True
    assert stream.subtitle_count == 123


def test_get_subtitle_streams_accepts_unknown_packet_count(tmp_path: Path):
    """Test ffprobe's N/A packet count is treated as unknown.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with patch(
        "scinoephile.media.probe.ffmpeg.probe",
        return_value={
            "streams": [
                {
                    "index": 2,
                    "codec_type": "subtitle",
                    "codec_name": "subrip",
                    "nb_read_packets": "N/A",
                },
            ],
        },
    ):
        streams = get_subtitle_streams(infile_path)

    assert len(streams) == 1
    assert streams[0].subtitle_count is None


def test_get_streams_returns_all_typed_streams(tmp_path: Path):
    """Test media stream probing returns all typed stream models."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with patch(
        "scinoephile.media.probe.ffmpeg.probe",
        return_value={
            "streams": [
                {
                    "index": 0,
                    "codec_type": "video",
                    "codec_name": "hevc",
                    "width": 3840,
                    "height": 2160,
                },
                {
                    "index": 1,
                    "codec_type": "audio",
                    "codec_name": "flac",
                    "channels": 2,
                    "tags": {"language": "jpn"},
                },
                {
                    "index": 2,
                    "codec_type": "subtitle",
                    "codec_name": "subrip",
                    "tags": {"language": "eng"},
                },
                {"index": 3, "codec_type": "data", "codec_name": "bin_data"},
                "not a stream",
            ],
        },
    ):
        streams = get_streams(infile_path)

    assert len(streams) == 4
    assert isinstance(streams[0], VideoStream)
    assert streams[0].width == 3840
    assert streams[0].height == 2160
    assert isinstance(streams[1], AudioStream)
    assert streams[1].language == "jpn"
    assert streams[1].channels == 2
    assert isinstance(streams[2], SubtitleStream)
    assert streams[2].language == "eng"
    assert isinstance(streams[3], Stream)
    assert streams[3].codec_type == "data"


def test_get_streams_skips_streams_without_nonnegative_index(tmp_path: Path):
    """Test media stream probing skips streams without usable indexes."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with patch(
        "scinoephile.media.probe.ffmpeg.probe",
        return_value={
            "streams": [
                {"codec_type": "audio", "channels": 2},
                {"index": None, "codec_type": "audio", "channels": 2},
                {"index": -1, "codec_type": "audio", "channels": 2},
                {"index": "bad", "codec_type": "audio", "channels": 2},
                {"index": 1, "codec_type": "audio", "channels": 2},
            ],
        },
    ):
        streams = get_streams(infile_path)

    assert len(streams) == 1
    assert streams[0].index == 1


def test_get_streams_normalizes_missing_codecs(tmp_path: Path):
    """Test media stream probing normalizes missing codec fields."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with patch(
        "scinoephile.media.probe.ffmpeg.probe",
        return_value={
            "streams": [
                {"index": 0},
                {"index": 1, "codec_type": "data"},
            ],
        },
    ):
        streams = get_streams(infile_path)

    assert streams[0].codec_type == "unknown"
    assert streams[0].codec_name == "unknown"
    assert streams[1].codec_type == "data"
    assert streams[1].codec_name == "data"
