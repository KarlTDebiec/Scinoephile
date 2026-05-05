#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media stream utilities."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

from scinoephile.core.media import SubtitleStream
from scinoephile.core.media.subtitles import (
    extract_subtitle_stream,
    extract_subtitles,
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


def test_extract_subtitles_filters_languages_and_runs_ffmpeg(tmp_path: Path):
    """Test subtitle extraction filters by language and maps matching streams."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    ffmpeg_input = Mock()

    with (
        patch(
            "scinoephile.core.media.subtitles.ffmpeg.probe",
            return_value={
                "streams": [
                    {
                        "index": 2,
                        "codec_type": "subtitle",
                        "codec_name": "subrip",
                        "tags": {"language": "eng"},
                    },
                    {
                        "index": 3,
                        "codec_type": "subtitle",
                        "codec_name": "ass",
                        "tags": {"language": "jpn"},
                    },
                    {
                        "index": 4,
                        "codec_type": "subtitle",
                        "codec_name": "hdmv_pgs_subtitle",
                        "tags": {"language": "zho"},
                    },
                ],
            },
        ),
        patch(
            "scinoephile.core.media.subtitles.ffmpeg.input",
            return_value=ffmpeg_input,
        ),
    ):
        extracted_paths = extract_subtitles(
            infile_path=infile_path,
            languages=["eng", "zho"],
            output_dir_path=output_dir_path,
        )

    assert extracted_paths == [
        output_dir_path / "eng-2.srt",
        output_dir_path / "zho-4.sup",
    ]
    ffmpeg_input.output.assert_any_call(
        str(output_dir_path / "eng-2.srt"),
        map="0:2",
        **{"c:s": "subrip"},
    )
    ffmpeg_input.output.assert_any_call(
        str(output_dir_path / "zho-4.sup"),
        map="0:4",
        **{"c:s": "copy"},
    )
    assert ffmpeg_input.output.return_value.run.call_count == 2


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
