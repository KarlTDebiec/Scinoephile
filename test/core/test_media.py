#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media stream utilities."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.core.media.subtitles import (
    extract_subtitle_stream,
    get_subtitle_streams,
)


def test_get_subtitle_streams(tmp_path: Path):
    """Test subtitle stream metadata parsing."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with patch(
        "scinoephile.core.media.subtitles.ffmpeg.probe",
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
        streams = get_subtitle_streams(infile_path, counts=True)

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
