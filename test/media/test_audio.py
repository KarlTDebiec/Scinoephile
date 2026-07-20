#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media audio extraction utilities."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import ffmpeg
from pytest import raises

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.media.audio_stream import AudioStream
from scinoephile.media.audio import extract_audio


class FakeFfmpegInput:
    """Fake ffmpeg input chain that records output arguments."""

    def __init__(self, run_exception: Exception | None = None):
        """Initialize."""
        self.output_args: tuple[object, ...] | None = None
        self.output_kwargs: dict[str, object] | None = None
        self.run_kwargs: dict[str, object] | None = None
        self.run_exception = run_exception
        """Exception to raise when run."""

    def output(self, *args: object, **kwargs: object) -> FakeFfmpegInput:
        """Record ffmpeg output arguments.

        Arguments:
            *args: ffmpeg output positional arguments
            **kwargs: ffmpeg output keyword arguments
        Returns:
            fake ffmpeg input chain
        """
        self.output_args = args
        self.output_kwargs = kwargs
        return self

    def run(self, **kwargs: object):
        """Record ffmpeg run arguments.

        Arguments:
            **kwargs: ffmpeg run keyword arguments
        """
        self.run_kwargs = kwargs
        if self.run_exception is not None:
            raise self.run_exception


def test_extract_audio_selects_stream_and_extracts_track(tmp_path: Path):
    """Test extraction selects the requested stream and forwards its channel count.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "movie.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "audio.wav"
    stream = AudioStream(index=3, codec_type="audio", channels=6)

    with (
        patch("scinoephile.media.audio._get_audio_stream", return_value=stream),
        patch("scinoephile.media.audio._extract_audio_track") as extract_track,
    ):
        selected = extract_audio(
            infile_path,
            outfile_path,
            stream_index=3,
        )

    assert selected is stream
    extract_track.assert_called_once_with(
        infile_path.resolve(),
        outfile_path.resolve(),
        3,
        6,
    )


def test_extract_audio_track_filters_overall_stream_index(tmp_path: Path):
    """Test center-channel extraction filters the absolute media stream index.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    fake_ffmpeg_input = FakeFfmpegInput()

    with (
        patch(
            "scinoephile.media.audio._get_audio_stream",
            return_value=AudioStream(index=12, codec_type="audio", channels=6),
        ),
        patch(
            "scinoephile.media.audio.ffmpeg.input",
            return_value=fake_ffmpeg_input,
        ),
    ):
        extract_audio(infile_path, tmp_path / "audio.wav")

    assert fake_ffmpeg_input.output_kwargs is not None
    assert fake_ffmpeg_input.output_kwargs["filter_complex"] == (
        "[0:12]pan=mono|c0=c2[out]"
    )


def test_extract_audio_track_maps_overall_stream_index(tmp_path: Path):
    """Test audio extraction maps the absolute media stream index.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    fake_ffmpeg_input = FakeFfmpegInput()

    with (
        patch(
            "scinoephile.media.audio._get_audio_stream",
            return_value=AudioStream(index=12, codec_type="audio", channels=2),
        ),
        patch(
            "scinoephile.media.audio.ffmpeg.input",
            return_value=fake_ffmpeg_input,
        ),
    ):
        extract_audio(infile_path, tmp_path / "audio.wav")

    assert fake_ffmpeg_input.output_kwargs is not None
    assert fake_ffmpeg_input.output_kwargs["map"] == "0:12"


def test_extract_audio_track_wraps_ffmpeg_errors(tmp_path: Path):
    """Test audio extraction errors are user-facing.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    fake_ffmpeg_input = FakeFfmpegInput(
        ffmpeg.Error("ffmpeg", b"", b"failed"),
    )

    with (
        patch(
            "scinoephile.media.audio._get_audio_stream",
            return_value=AudioStream(index=12, codec_type="audio", channels=2),
        ),
        patch(
            "scinoephile.media.audio.ffmpeg.input",
            return_value=fake_ffmpeg_input,
        ),
        raises(
            ScinoephileError,
            match="Could not extract audio stream 12",
        ) as excinfo,
    ):
        extract_audio(infile_path, tmp_path / "audio.wav")

    assert isinstance(excinfo.value.__cause__, ffmpeg.Error)


def test_extract_audio_requires_overwrite_for_existing_output(tmp_path: Path):
    """Test extraction preserves an existing output unless overwrite is enabled.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "movie.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "audio.wav"
    outfile_path.touch()

    with raises(ScinoephileError, match="use --overwrite"):
        extract_audio(infile_path, outfile_path)


def test_extract_audio_requires_wav_output(tmp_path: Path):
    """Test extraction rejects an output extension inconsistent with its format.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "movie.mkv"
    infile_path.touch()

    with raises(ScinoephileError, match=r"\.wav extension"):
        extract_audio(infile_path, tmp_path / "audio.mp3")
