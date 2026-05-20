#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of AudioSeries.load_from_media."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from pydub import AudioSegment

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common.file import get_temp_file_path
from scinoephile.core import ScinoephileError


class FakeFfmpegInput:
    """Fake ffmpeg input chain that records output arguments."""

    def __init__(self):
        """Initialize."""
        self.output_args: tuple[object, ...] | None = None
        self.output_kwargs: dict[str, object] | None = None
        self.run_kwargs: dict[str, object] | None = None

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


def test_audio_series_extract_audio_track_maps_overall_stream_index():
    """Test audio extraction maps the absolute media stream index."""
    fake_ffmpeg_input = FakeFfmpegInput()

    with patch(
        "scinoephile.audio.subtitles.series.ffmpeg.input",
        return_value=fake_ffmpeg_input,
    ):
        AudioSeries.extract_audio_track(
            Path("video.mkv"),
            Path("audio.wav"),
            12,
            2,
        )

    assert fake_ffmpeg_input.output_kwargs is not None
    assert fake_ffmpeg_input.output_kwargs["map"] == "0:12"


def test_audio_series_extract_audio_track_filters_overall_stream_index():
    """Test center-channel extraction filters the absolute media stream index."""
    fake_ffmpeg_input = FakeFfmpegInput()

    with patch(
        "scinoephile.audio.subtitles.series.ffmpeg.input",
        return_value=fake_ffmpeg_input,
    ):
        AudioSeries.extract_audio_track(
            Path("video.mkv"),
            Path("audio.wav"),
            12,
            6,
        )

    assert fake_ffmpeg_input.output_kwargs is not None
    assert fake_ffmpeg_input.output_kwargs["filter_complex"] == (
        "[0:12]pan=mono|c0=c2[out]"
    )


def test_audio_series_load_from_media_supports_stream_index():
    """Test media loading probes media and loads the requested audio stream."""
    full_audio = AudioSegment.silent(duration=3000)

    with get_temp_file_path(".srt") as subtitle_path:
        subtitle_path.write_text(
            "1\n00:00:01,000 --> 00:00:02,000\n你好\n", encoding="utf-8"
        )
        with get_temp_file_path(".mp4") as media_path:
            media_path.touch()
            with patch(
                "scinoephile.media.probe.ffmpeg.probe",
                return_value={
                    "streams": [
                        {"index": 0, "codec_type": "video"},
                        {"index": 1, "codec_type": "audio", "channels": 2},
                        {"index": 12, "codec_type": "audio", "channels": 6},
                    ]
                },
            ):
                with patch(
                    "scinoephile.audio.subtitles.series.AudioSeries.extract_audio_track"
                ) as extract_audio_track:
                    with patch(
                        "scinoephile.audio.subtitles.series.AudioSegment.from_wav",
                        return_value=full_audio,
                    ):
                        yuewen_series = AudioSeries.load_from_media(
                            media_path=media_path,
                            subtitle_path=subtitle_path,
                            stream_index=12,
                        )

    assert isinstance(yuewen_series, AudioSeries)
    assert [event.text for event in yuewen_series.events] == ["你好"]
    extract_audio_track.assert_called_once()
    assert extract_audio_track.call_args.args[2] == 12
    assert extract_audio_track.call_args.args[3] == 6


def test_audio_series_load_from_media_defaults_to_first_audio_stream():
    """Test media loading defaults to the first probed audio stream."""
    full_audio = AudioSegment.silent(duration=3000)

    with get_temp_file_path(".srt") as subtitle_path:
        subtitle_path.write_text(
            "1\n00:00:01,000 --> 00:00:02,000\n你好\n", encoding="utf-8"
        )
        with get_temp_file_path(".mp4") as media_path:
            media_path.touch()
            with patch(
                "scinoephile.media.probe.ffmpeg.probe",
                return_value={
                    "streams": [
                        {"index": 0, "codec_type": "video"},
                        {"codec_type": "audio", "channels": 2},
                        {"index": -1, "codec_type": "audio", "channels": 2},
                        {"index": 1, "codec_type": "audio", "channels": 2},
                        {"index": 12, "codec_type": "audio", "channels": 6},
                    ]
                },
            ):
                with patch(
                    "scinoephile.audio.subtitles.series.AudioSeries.extract_audio_track"
                ) as extract_audio_track:
                    with patch(
                        "scinoephile.audio.subtitles.series.AudioSegment.from_wav",
                        return_value=full_audio,
                    ):
                        yuewen_series = AudioSeries.load_from_media(
                            media_path=media_path,
                            subtitle_path=subtitle_path,
                        )

    assert isinstance(yuewen_series, AudioSeries)
    assert [event.text for event in yuewen_series.events] == ["你好"]
    extract_audio_track.assert_called_once()
    assert extract_audio_track.call_args.args[2] == 1
    assert extract_audio_track.call_args.args[3] == 2


def test_audio_series_load_from_media_rejects_invalid_stream_index():
    """Test media loading rejects missing stream indexes."""
    with get_temp_file_path(".srt") as subtitle_path:
        subtitle_path.write_text(
            "1\n00:00:00,000 --> 00:00:01,000\n你好\n", encoding="utf-8"
        )
        with get_temp_file_path(".mp4") as media_path:
            media_path.touch()
            with patch(
                "scinoephile.media.probe.ffmpeg.probe",
                return_value={
                    "streams": [{"index": 1, "codec_type": "audio", "channels": 2}]
                },
            ):
                with pytest.raises(ScinoephileError, match="No stream index 2"):
                    AudioSeries.load_from_media(
                        media_path=media_path,
                        subtitle_path=subtitle_path,
                        stream_index=2,
                    )


def test_audio_series_load_from_media_rejects_non_audio_stream_index():
    """Test media loading rejects overall stream indexes that are not audio."""
    with get_temp_file_path(".srt") as subtitle_path:
        subtitle_path.write_text(
            "1\n00:00:00,000 --> 00:00:01,000\n你好\n", encoding="utf-8"
        )
        with get_temp_file_path(".mp4") as media_path:
            media_path.touch()
            with patch(
                "scinoephile.media.probe.ffmpeg.probe",
                return_value={
                    "streams": [
                        {"index": 0, "codec_type": "video"},
                        {"index": 1, "codec_type": "audio", "channels": 2},
                    ]
                },
            ):
                with pytest.raises(
                    ScinoephileError, match="Stream index 0 is not an audio stream"
                ):
                    AudioSeries.load_from_media(
                        media_path=media_path,
                        subtitle_path=subtitle_path,
                        stream_index=0,
                    )
