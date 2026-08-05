#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media audio extraction utilities."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import ffmpeg
from pytest import mark, raises

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.media.audio_stream import AudioStream
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
        patch("scinoephile.media.audio.get_streams", return_value=[stream]),
        patch("scinoephile.media.audio._extract_audio_track") as extract_track,
    ):
        selected = extract_audio(infile_path, outfile_path, stream_index=3)

    assert selected is stream
    extract_track.assert_called_once_with(
        infile_path.resolve(),
        outfile_path.resolve(),
        3,
        6,
        AudioExtractionMode.TRANSCRIPTION,
    )


def test_extract_audio_transcription_filters_multichannel_center(tmp_path: Path):
    """Test transcription extraction isolates multichannel center at 16 kHz.

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
        extract_audio(infile_path, tmp_path / "audio.wav")

    assert fake_ffmpeg_input.output_kwargs is not None
    assert fake_ffmpeg_input.output_kwargs["filter_complex"] == (
        "[0:12]pan=mono|c0=c2[out]"
    )
    assert fake_ffmpeg_input.output_kwargs["map"] == "[out]"
    assert fake_ffmpeg_input.output_kwargs["ar"] == 16000
    assert "ac" not in fake_ffmpeg_input.output_kwargs


def test_extract_audio_transcription_downmixes_non_multichannel_stream(tmp_path: Path):
    """Test transcription downmixes other streams to mono at 16 kHz.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    fake_ffmpeg_input = FakeFfmpegInput()

    with (
        patch(
            "scinoephile.media.audio.get_streams",
            return_value=[AudioStream(index=12, codec_type="audio", channels=2)],
        ),
        patch("scinoephile.media.audio.ffmpeg.input", return_value=fake_ffmpeg_input),
    ):
        extract_audio(infile_path, tmp_path / "audio.wav")

    assert fake_ffmpeg_input.output_kwargs is not None
    assert fake_ffmpeg_input.output_kwargs["map"] == "0:12"
    assert fake_ffmpeg_input.output_kwargs["ac"] == 1
    assert fake_ffmpeg_input.output_kwargs["ar"] == 16000
    assert "filter_complex" not in fake_ffmpeg_input.output_kwargs


def test_extract_audio_native_center_extracts_center_at_source_rate(tmp_path: Path):
    """Test native center extraction isolates the absolute stream center channel.

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
            infile_path, tmp_path / "audio.wav", mode=AudioExtractionMode.NATIVE_CENTER
        )

    assert fake_ffmpeg_input.output_kwargs is not None
    assert fake_ffmpeg_input.output_kwargs["filter_complex"] == (
        "[0:12]pan=mono|c0=c2[out]"
    )
    assert fake_ffmpeg_input.output_kwargs["map"] == "[out]"
    assert "ar" not in fake_ffmpeg_input.output_kwargs


def test_extract_audio_native_center_heavy_uses_weighted_mix(tmp_path: Path):
    """Test native center-heavy extraction uses the requested coefficients.

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
            infile_path,
            tmp_path / "audio.wav",
            mode=AudioExtractionMode.NATIVE_CENTER_HEAVY,
        )

    assert fake_ffmpeg_input.output_kwargs is not None
    assert fake_ffmpeg_input.output_kwargs["filter_complex"] == (
        "[0:12]pan=mono|c0=0.70*c2+0.15*c0+0.15*c1[out]"
    )
    assert fake_ffmpeg_input.output_kwargs["map"] == "[out]"
    assert "ar" not in fake_ffmpeg_input.output_kwargs


@mark.parametrize(
    ("mode", "channel_count"),
    [(AudioExtractionMode.NATIVE_MONO, 1), (AudioExtractionMode.NATIVE_STEREO, 2)],
)
def test_extract_audio_native_complete_mix_preserves_rate(
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
    "mode", [AudioExtractionMode.NATIVE_CENTER, AudioExtractionMode.NATIVE_CENTER_HEAVY]
)
def test_extract_audio_center_modes_require_center_channel(
    tmp_path: Path, mode: AudioExtractionMode
):
    """Test center-dependent modes reject streams without a center channel.

    Arguments:
        tmp_path: temporary directory provided by pytest
        mode: center-dependent extraction mode
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with (
        patch(
            "scinoephile.media.audio.get_streams",
            return_value=[AudioStream(index=12, codec_type="audio", channels=2)],
        ),
        patch("scinoephile.media.audio.ffmpeg.input") as ffmpeg_input,
        raises(
            ScinoephileError,
            match=(
                rf"Audio extraction mode {mode.value} requires a stream with a "
                r"center channel; stream 12 has 2 channels"
            ),
        ),
    ):
        extract_audio(infile_path, tmp_path / "audio.wav", mode=mode)

    ffmpeg_input.assert_not_called()


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
