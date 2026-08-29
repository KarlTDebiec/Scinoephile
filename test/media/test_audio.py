#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media audio extraction utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import ffmpeg
from pytest import mark, raises

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.media import AudioStream, VideoStream
from scinoephile.media.audio import AudioExtractionMode, extract_audio


class FakeFfmpegInput:
    """Fake ffmpeg input chain that records output arguments."""

    def __init__(self, run_exception: Exception | None = None):
        """Initialize."""
        self.output_args: tuple[object, ...] | None = None
        self.output_kwargs: dict[str, object] | None = None
        self.run_kwargs: dict[str, object] | None = None
        self.run_exception = run_exception
        """Exception to raise when run."""

    def output(self, *args: object, **kwargs: Any) -> FakeFfmpegInput:
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

    def run(self, **kwargs: Any):
        """Record ffmpeg run arguments.

        Arguments:
            **kwargs: ffmpeg run keyword arguments
        """
        self.run_kwargs = kwargs
        if self.run_exception is not None:
            raise self.run_exception


def test_extract_audio_selects_stream_and_extracts_track(tmp_path: Path):
    """Test extraction selects and returns the requested stream.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "movie.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "audio.wav"
    stream = AudioStream(index=3, codec_type="audio")

    with (
        patch("scinoephile.media.audio.get_streams", return_value=[stream]),
        patch("scinoephile.media.audio._extract_audio_track") as extract_track,
    ):
        selected = extract_audio(infile_path, outfile_path, stream_index=3)

    assert selected is stream
    extract_track.assert_called_once_with(
        infile_path.resolve(), outfile_path.resolve(), 3, AudioExtractionMode.ORIGINAL
    )


def test_extract_audio_rejects_missing_stream_index(tmp_path: Path):
    """Test extraction rejects an unavailable absolute stream index.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "movie.mkv"
    infile_path.touch()

    with (
        patch(
            "scinoephile.media.audio.get_streams",
            return_value=[AudioStream(index=1, codec_type="audio")],
        ),
        raises(ScinoephileError, match="No stream index 2"),
    ):
        extract_audio(infile_path, tmp_path / "audio.wav", stream_index=2)


def test_extract_audio_rejects_non_audio_stream_index(tmp_path: Path):
    """Test extraction rejects a selected stream that is not audio.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "movie.mkv"
    infile_path.touch()

    with (
        patch(
            "scinoephile.media.audio.get_streams",
            return_value=[VideoStream(index=0, codec_type="video")],
        ),
        raises(ScinoephileError, match="Stream index 0 is not an audio stream"),
    ):
        extract_audio(infile_path, tmp_path / "audio.wav", stream_index=0)


@mark.parametrize("source_channel_count", [1, 2, 6])
def test_extract_audio_original_preserves_rate_and_channels(
    tmp_path: Path, source_channel_count: int
):
    """Test original extraction preserves the source rate and channel count.

    Arguments:
        tmp_path: temporary directory provided by pytest
        source_channel_count: source channel count
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    fake_ffmpeg_input = FakeFfmpegInput()

    with (
        patch(
            "scinoephile.media.audio.get_streams",
            return_value=[
                AudioStream(index=12, codec_type="audio", channels=source_channel_count)
            ],
        ),
        patch("scinoephile.media.audio.ffmpeg.input", return_value=fake_ffmpeg_input),
    ):
        extract_audio(infile_path, tmp_path / "audio.wav")

    assert fake_ffmpeg_input.output_kwargs is not None
    assert fake_ffmpeg_input.output_kwargs["map"] == "0:12"
    assert "ac" not in fake_ffmpeg_input.output_kwargs
    assert "ar" not in fake_ffmpeg_input.output_kwargs
    assert "filter_complex" not in fake_ffmpeg_input.output_kwargs


def test_extract_audio_center_extracts_center_at_source_rate(tmp_path: Path):
    """Test center extraction isolates the absolute stream center channel.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    fake_ffmpeg_input = FakeFfmpegInput()

    with (
        patch(
            "scinoephile.media.audio.get_streams",
            return_value=[AudioStream(index=12, codec_type="audio", channels=6)],
        ),
        patch("scinoephile.media.audio.ffmpeg.input", return_value=fake_ffmpeg_input),
    ):
        extract_audio(
            infile_path, tmp_path / "audio.wav", mode=AudioExtractionMode.CENTER
        )

    assert fake_ffmpeg_input.output_kwargs is not None
    assert fake_ffmpeg_input.output_kwargs["filter_complex"] == (
        "[0:12]channelmap=map=FC:channel_layout=mono[out]"
    )
    assert fake_ffmpeg_input.output_kwargs["map"] == "[out]"
    assert "ar" not in fake_ffmpeg_input.output_kwargs


def test_extract_audio_center_heavy_uses_weighted_mix(tmp_path: Path):
    """Test center-heavy extraction uses the requested coefficients.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    fake_ffmpeg_input = FakeFfmpegInput()

    with (
        patch(
            "scinoephile.media.audio.get_streams",
            return_value=[AudioStream(index=12, codec_type="audio", channels=6)],
        ),
        patch("scinoephile.media.audio.ffmpeg.input", return_value=fake_ffmpeg_input),
    ):
        extract_audio(
            infile_path, tmp_path / "audio.wav", mode=AudioExtractionMode.CENTER_HEAVY
        )

    assert fake_ffmpeg_input.output_kwargs is not None
    assert fake_ffmpeg_input.output_kwargs["filter_complex"] == (
        "[0:12]channelmap=map=FL|FR|FC:channel_layout=3.0,"
        "pan=mono|c0=0.15*c0+0.15*c1+0.70*c2[out]"
    )
    assert fake_ffmpeg_input.output_kwargs["map"] == "[out]"
    assert "ar" not in fake_ffmpeg_input.output_kwargs


@mark.parametrize(
    ("mode", "channel_count"),
    [(AudioExtractionMode.MONO, 1), (AudioExtractionMode.STEREO, 2)],
)
def test_extract_audio_complete_mix_preserves_rate(
    tmp_path: Path, mode: AudioExtractionMode, channel_count: int
):
    """Test native complete-stream downmixes use the requested channel count.

    Arguments:
        tmp_path: temporary directory provided by pytest
        mode: native complete-stream extraction mode
        channel_count: expected output channel count
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    fake_ffmpeg_input = FakeFfmpegInput()

    with (
        patch(
            "scinoephile.media.audio.get_streams",
            return_value=[AudioStream(index=12, codec_type="audio", channels=6)],
        ),
        patch("scinoephile.media.audio.ffmpeg.input", return_value=fake_ffmpeg_input),
    ):
        extract_audio(infile_path, tmp_path / "audio.wav", mode=mode)

    assert fake_ffmpeg_input.output_kwargs is not None
    assert fake_ffmpeg_input.output_kwargs["map"] == "0:12"
    assert fake_ffmpeg_input.output_kwargs["ac"] == channel_count
    assert "ar" not in fake_ffmpeg_input.output_kwargs


@mark.parametrize(
    "mode", [AudioExtractionMode.CENTER, AudioExtractionMode.CENTER_HEAVY]
)
def test_extract_audio_center_modes_require_center_channel(
    tmp_path: Path, mode: AudioExtractionMode
):
    """Test center-dependent modes explain FFmpeg channel-layout failures.

    Arguments:
        tmp_path: temporary directory provided by pytest
        mode: center-dependent extraction mode
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    fake_ffmpeg_input = FakeFfmpegInput(
        ffmpeg.Error(
            "ffmpeg", b"", b"input channel 'FC' not available from input layout 'quad'"
        )
    )

    with (
        patch(
            "scinoephile.media.audio.get_streams",
            return_value=[AudioStream(index=12, codec_type="audio", channels=4)],
        ),
        patch("scinoephile.media.audio.ffmpeg.input", return_value=fake_ffmpeg_input),
        raises(
            ScinoephileError, match=rf"mode {mode.value} requires .*front center \(FC\)"
        ) as excinfo,
    ):
        extract_audio(infile_path, tmp_path / "audio.wav", mode=mode)

    assert isinstance(excinfo.value.__cause__, ffmpeg.Error)


def test_extract_audio_track_wraps_ffmpeg_errors(tmp_path: Path):
    """Test audio extraction errors are user-facing.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    fake_ffmpeg_input = FakeFfmpegInput(ffmpeg.Error("ffmpeg", b"", b"failed"))

    with (
        patch(
            "scinoephile.media.audio.get_streams",
            return_value=[AudioStream(index=12, codec_type="audio", channels=2)],
        ),
        patch("scinoephile.media.audio.ffmpeg.input", return_value=fake_ffmpeg_input),
        raises(ScinoephileError, match="Could not extract audio stream 12") as excinfo,
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
