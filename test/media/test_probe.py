#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media probing utilities."""

from __future__ import annotations

from inspect import signature
from pathlib import Path
from unittest.mock import patch

from scinoephile import media
from scinoephile.core.media import AudioStream, Stream, SubtitleStream, VideoStream
from scinoephile.media.probe import (
    from_ffprobe_stream,
    get_streams,
    get_subtitle_streams,
)


def test_media_package_does_not_export_core_stream_classes():
    """Test media package does not re-export core stream models."""
    assert not hasattr(media, "SubtitleStream")


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

    assert "details" not in signature(get_subtitle_streams).parameters
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


def test_get_streams_returns_typed_streams(tmp_path: Path):
    """Test media stream probing returns typed stream models."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with patch(
        "scinoephile.media.probe.ffmpeg.probe",
        return_value={
            "streams": [
                {"index": 0, "codec_type": "video", "codec_name": "h264"},
                "not a stream",
            ],
        },
    ) as probe:
        streams = get_streams(infile_path)

    probe.assert_called_once_with(str(infile_path))
    assert len(streams) == 1
    assert isinstance(streams[0], VideoStream)
    assert streams[0].index == 0
    assert streams[0].codec_name == "h264"


def test_get_streams_filters_stream_types(tmp_path: Path):
    """Test media stream probing filters by stream type."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with patch(
        "scinoephile.media.probe.ffmpeg.probe",
        return_value={
            "streams": [
                {"index": 0, "codec_type": "video", "codec_name": "h264"},
                {"index": 1, "codec_type": "audio", "codec_name": "aac"},
                {"index": 2, "codec_type": "subtitle", "codec_name": "subrip"},
            ],
        },
    ):
        streams = get_streams(
            infile_path,
            video=False,
            audio=False,
            subtitles=True,
        )

    assert len(streams) == 1
    assert isinstance(streams[0], SubtitleStream)
    assert streams[0].index == 2


def test_get_streams_filters_generic_streams(tmp_path: Path):
    """Test media stream probing excludes generic streams when filtered."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with patch(
        "scinoephile.media.probe.ffmpeg.probe",
        return_value={
            "streams": [
                {"index": 3, "codec_type": "data", "codec_name": "bin_data"},
            ],
        },
    ):
        streams = get_streams(
            infile_path,
            video=False,
            audio=False,
            subtitles=True,
        )

    assert streams == []


def test_from_ffprobe_stream_returns_typed_streams():
    """Test generic stream parsing returns typed stream models."""
    video = from_ffprobe_stream(
        {
            "index": 0,
            "codec_type": "video",
            "codec_name": "hevc",
            "width": 3840,
            "height": 2160,
        }
    )
    audio = from_ffprobe_stream(
        {
            "index": 1,
            "codec_type": "audio",
            "codec_name": "flac",
            "channels": 2,
            "tags": {"language": "jpn"},
        }
    )
    subtitle = from_ffprobe_stream(
        {
            "index": 2,
            "codec_type": "subtitle",
            "codec_name": "subrip",
            "tags": {"language": "eng"},
        }
    )

    assert isinstance(video, VideoStream)
    assert video.description == "Stream #0:0: Video: hevc (3840x2160)"
    assert isinstance(audio, AudioStream)
    assert audio.description == "Stream #0:1(jpn): Audio: flac (channels=2)"
    assert isinstance(subtitle, SubtitleStream)
    assert subtitle.description == "Stream #0:2(eng): Subtitle: subrip"


def test_from_ffprobe_stream_normalizes_missing_codecs():
    """Test generic stream parsing normalizes missing codec fields."""
    no_codec_type = from_ffprobe_stream({"index": 0})
    no_codec_name = from_ffprobe_stream({"index": 1, "codec_type": "data"})

    assert isinstance(no_codec_type, Stream)
    assert no_codec_type.codec_type == "unknown"
    assert no_codec_type.codec_name == "unknown"
    assert no_codec_type.description == "Stream #0:0: Unknown: unknown"
    assert isinstance(no_codec_name, Stream)
    assert no_codec_name.codec_type == "data"
    assert no_codec_name.codec_name == "data"
    assert no_codec_name.description == "Stream #0:1: Data: data"
