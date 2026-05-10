#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media stream utilities."""

from __future__ import annotations

from inspect import signature
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scinoephile.core import ScinoephileError
from scinoephile.core.media import AudioStream, Stream, SubtitleStream, VideoStream
from scinoephile.core.media.streams import get_media_streams
from scinoephile.core.media.subtitles import (
    extract_subtitle_stream,
    get_subtitle_streams,
)


def test_get_subtitle_streams(tmp_path: Path):
    """Test subtitle stream metadata parsing."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with patch(
        "scinoephile.core.media.streams.ffmpeg.probe",
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

    assert "counts" not in signature(get_subtitle_streams).parameters
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
    assert streams[0].description == (
        "Stream #0:2(eng): Subtitle: subrip "
        "(extension=srt, title=English, sdh, subtitles=123)"
    )


def test_get_media_streams_filters_non_dict_streams(tmp_path: Path):
    """Test media stream probing returns only ffprobe stream objects."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with patch(
        "scinoephile.core.media.streams.ffmpeg.probe",
        return_value={
            "streams": [
                {"index": 0, "codec_type": "video", "codec_name": "h264"},
                "not a stream",
            ],
        },
    ) as probe:
        streams = get_media_streams(infile_path)

    probe.assert_called_once_with(str(infile_path))
    assert streams == [
        {"index": 0, "codec_type": "video", "codec_name": "h264"},
    ]


def test_stream_from_ffprobe_stream_returns_typed_streams():
    """Test generic stream parsing returns typed stream models."""
    video = Stream.from_ffprobe_stream(
        {
            "index": 0,
            "codec_type": "video",
            "codec_name": "hevc",
            "width": 3840,
            "height": 2160,
        }
    )
    audio = Stream.from_ffprobe_stream(
        {
            "index": 1,
            "codec_type": "audio",
            "codec_name": "flac",
            "channels": 2,
            "tags": {"language": "jpn"},
        }
    )
    subtitle = Stream.from_ffprobe_stream(
        {
            "index": 2,
            "codec_type": "subtitle",
            "codec_name": "subrip",
            "tags": {"language": "eng"},
        }
    )

    assert isinstance(video, VideoStream)
    assert video.probe_description == "Stream #0:0: Video: hevc (3840x2160)"
    assert isinstance(audio, AudioStream)
    assert audio.probe_description == "Stream #0:1(jpn): Audio: flac (channels=2)"
    assert isinstance(subtitle, SubtitleStream)
    assert subtitle.probe_description == "Stream #0:2(eng): Subtitle: subrip"


def test_subtitle_stream_get_probe_description_with_details(tmp_path: Path):
    """Test subtitle stream enriches its own probe description."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")

    with (
        patch(
            "scinoephile.core.media.subtitle_analysis.analyze_subtitle_stream_script"
        ) as analyze,
        patch(
            "scinoephile.core.media.subtitle_analysis.get_subtitle_stream_stats"
        ) as stats,
    ):
        analyze.return_value.script = "zho-Hant"
        stats.return_value.event_count = 12
        stats.return_value.first_start_ms = 62_500
        stats.return_value.last_end_ms = 3_725_250
        description = stream.get_probe_description(
            infile_path=infile_path,
            details=True,
        )

    assert description == (
        "Stream #0:2(zho-Hant): Subtitle: subrip (subtitles=12, span=00:01:02-01:02:05)"
    )


def test_subtitle_stream_outfile_filename():
    """Test subtitle stream output filename generation."""
    stream = SubtitleStream(index=2, language="eng", codec_name="subrip")

    assert stream.outfile_filename == "eng-2.srt"


def test_subtitle_stream_outfile_filename_requires_language():
    """Test subtitle stream output filename rejects missing language."""
    stream = SubtitleStream(index=2, language=None, codec_name="subrip")

    try:
        stream.outfile_filename
    except ValueError as exc:
        assert str(exc) == "Subtitle stream must have a language to build output path"
    else:
        raise AssertionError("Expected ValueError")


def test_extract_subtitle_stream_runs_ffmpeg(tmp_path: Path):
    """Test single-stream extraction runs ffmpeg and returns output path."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "subtitles" / "eng-2.srt"
    outfile_path.parent.mkdir()
    ffmpeg_input = Mock()

    with patch(
        "scinoephile.core.media.subtitles.ffmpeg.input",
        return_value=ffmpeg_input,
    ):
        extracted_path = extract_subtitle_stream(
            infile_path=infile_path,
            stream=SubtitleStream(index=2, language="eng", codec_name="subrip"),
            outfile_path=outfile_path,
        )

    assert extracted_path == outfile_path
    ffmpeg_input.output.assert_called_once_with(
        str(outfile_path),
        map="0:2",
        **{"c:s": "subrip"},
    )


def test_extract_subtitle_stream_rejects_unknown_codec(tmp_path: Path):
    """Test single-stream extraction rejects unknown subtitle codecs."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "subtitles" / "eng-2.srt"
    outfile_path.parent.mkdir()

    with pytest.raises(ScinoephileError, match="Unsupported subtitle codec unknown"):
        extract_subtitle_stream(
            infile_path=infile_path,
            stream=SubtitleStream(index=2, language="eng", codec_name="unknown"),
            outfile_path=outfile_path,
        )
