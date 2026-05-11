#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media probing utilities."""

from __future__ import annotations

from inspect import signature
from pathlib import Path
from unittest.mock import patch

from scinoephile import media
from scinoephile.core.media import AudioStream, Stream, SubtitleStream, VideoStream
from scinoephile.media import probe as media_probe
from scinoephile.media.probe import get_streams, get_subtitle_streams


def test_media_package_does_not_export_core_stream_classes():
    """Test media package does not re-export core stream models."""
    assert not hasattr(media, "SubtitleStream")


def test_probe_public_api_is_minimal():
    """Test media probe exports only public probing functions."""
    assert "from_ffprobe_stream" not in media_probe.__all__
    assert list(signature(get_streams).parameters) == ["infile_path"]
    assert list(signature(get_subtitle_streams).parameters) == ["infile_path"]


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
    ) as probe:
        streams = get_subtitle_streams(infile_path)

    probe.assert_called_once_with(str(infile_path))
    assert len(streams) == 1
    assert streams[0].index == 2
    assert streams[0].language == "eng"
    assert streams[0].codec_name == "subrip"
    assert streams[0].title == "English"
    assert streams[0].sdh is True
    assert streams[0].subtitle_count == 123
    assert streams[0].extension == "srt"
    assert streams[0].output_codec == "subrip"
    assert (
        streams[0].description
        == "Stream #0:2(eng): Subtitle: subrip (title=English, subtitles=123)"
    )


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
    ) as probe:
        streams = get_streams(infile_path)

    probe.assert_called_once_with(str(infile_path))
    assert len(streams) == 4
    assert isinstance(streams[0], VideoStream)
    assert streams[0].description == "Stream #0:0: Video: hevc (3840x2160)"
    assert isinstance(streams[1], AudioStream)
    assert streams[1].description == "Stream #0:1(jpn): Audio: flac (channels=2)"
    assert isinstance(streams[2], SubtitleStream)
    assert streams[2].description == "Stream #0:2(eng): Subtitle: subrip"
    assert isinstance(streams[3], Stream)
    assert streams[3].description == "Stream #0:3: Data: bin_data"


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
    assert streams[0].description == "Stream #0:0: Unknown: unknown"
    assert streams[1].codec_type == "data"
    assert streams[1].codec_name == "data"
    assert streams[1].description == "Stream #0:1: Data: data"
