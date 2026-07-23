#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of core media stream models."""

from __future__ import annotations

from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.core.media.audio_stream import AudioStream
from scinoephile.core.media.stream import Stream
from scinoephile.core.media.subtitle_stream import SubtitleStream
from scinoephile.core.media.video_stream import VideoStream


def test_stream_descriptions():
    """Test stream descriptions."""
    video = VideoStream(
        index=0,
        codec_type="video",
        codec_name="hevc",
        width=3840,
        height=2160,
    )
    audio = AudioStream(
        index=1,
        codec_type="audio",
        codec_name="flac",
        channels=2,
        language="jpn",
    )
    subtitle = SubtitleStream(index=2, language="eng", codec_name="subrip")
    generic = Stream(index=3, codec_type="data", codec_name="bin_data")

    assert video.description == "Stream #0:0: Video: hevc (3840x2160)"
    assert audio.description == "Stream #0:1(jpn): Audio: flac (channels=2)"
    assert subtitle.description == "Stream #0:2(eng): Subtitle: subrip"
    assert generic.description == "Stream #0:3: Data: bin_data"


def test_stream_language_normalizes_script_subtags():
    """Test stream language normalization preserves script subtag case."""
    assert Stream(index=1, language="ENG").language == "eng"
    assert Stream(index=1, language="ZHO-UNKNOWN").language == "zho-Unknown"

    stream = SubtitleStream(index=2, language="ZHO-HANT", codec_name="subrip")

    assert stream.language == "zho-Hant"
    assert stream.description == "Stream #0:2(zho-Hant): Subtitle: subrip"
    assert stream.outfile_filename == "zho-Hant-2.srt"


def test_stream_details_start_with_base_details():
    """Test stream subclass details extend base details consistently."""
    video = VideoStream(
        index=0,
        codec_type="video",
        codec_name="hevc",
        title="Main",
        width=3840,
        height=2160,
    )
    subtitle = SubtitleStream(
        index=2,
        language="zho",
        codec_name="subrip",
        title="Chinese",
        subtitle_count=12,
        first_start_ms=62_500,
        last_end_ms=3_725_250,
    )

    assert video.description == "Stream #0:0: Video: hevc (title=Main, 3840x2160)"
    assert subtitle.description == (
        "Stream #0:2(zho): Subtitle: subrip "
        "(title=Chinese, subtitles=12, span=00:01:02-01:02:05)"
    )


def test_subtitle_stream_outfile_filename():
    """Test subtitle stream output filename generation."""
    stream = SubtitleStream(index=2, language="eng", codec_name="subrip")

    assert stream.outfile_filename == "eng-2.srt"


def test_subtitle_stream_supports_eia_608_output():
    """Test EIA-608 subtitles are extracted as SubRip SRT files."""
    stream = SubtitleStream(index=19, language="eng", codec_name="eia_608")

    assert stream.extension == "srt"
    assert stream.output_codec == "subrip"
    assert stream.outfile_filename == "eng-19.srt"


def test_subtitle_stream_outfile_filename_requires_language():
    """Test subtitle stream output filename rejects missing language."""
    stream = SubtitleStream(index=2, language=None, codec_name="subrip")

    try:
        stream.outfile_filename
    except ValueError as exc:
        assert str(exc) == "Subtitle stream must have a language to build output path"
    else:
        raise AssertionError("Expected ValueError")


def test_subtitle_stream_rejects_unknown_codec():
    """Test subtitle stream output properties reject unknown codecs."""
    stream = SubtitleStream(index=2, language="eng", codec_name="unknown")

    with raises(ScinoephileError, match="Unsupported subtitle codec unknown"):
        stream.extension
