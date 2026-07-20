#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of AudioSeries.load_from_media."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from pytest import raises

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common.file import get_temp_file_path
from scinoephile.core import ScinoephileError


def test_audio_series_load_from_media_supports_stream_index():
    """Test media loading probes media and loads the requested audio stream."""
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
                    "scinoephile.audio.subtitles.series.extract_audio",
                    side_effect=_write_selected_audio,
                ):
                    yuewen_series = AudioSeries.load_from_media(
                        media_path=media_path,
                        subtitle_path=subtitle_path,
                        stream_index=12,
                    )

    assert isinstance(yuewen_series, AudioSeries)
    assert [event.text for event in yuewen_series.events] == ["你好"]
    assert len(yuewen_series.audio) == 3126


def test_audio_series_load_from_media_defaults_to_first_audio_stream():
    """Test media loading defaults to the first probed audio stream."""
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
                    "scinoephile.audio.subtitles.series.extract_audio",
                    side_effect=_write_selected_audio,
                ):
                    yuewen_series = AudioSeries.load_from_media(
                        media_path=media_path,
                        subtitle_path=subtitle_path,
                    )

    assert isinstance(yuewen_series, AudioSeries)
    assert [event.text for event in yuewen_series.events] == ["你好"]
    assert len(yuewen_series.audio) == 3012


def test_audio_series_load_from_media_wraps_input_path_errors(tmp_path: Path):
    """Test media loading path errors are user-facing.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    with raises(
        ScinoephileError,
        match="Unable to load AudioSeries from media .*missing.mkv",
    ) as excinfo:
        AudioSeries.load_from_media(
            media_path=tmp_path / "missing.mkv",
            subtitle_path=tmp_path / "missing.srt",
        )

    assert isinstance(excinfo.value.__cause__, OSError)


def test_audio_series_load_from_media_wraps_decode_errors():
    """Test media loading audio decode errors are user-facing."""
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
                with patch("scinoephile.audio.subtitles.series.extract_audio"):
                    with patch(
                        "scinoephile.audio.subtitles.series.AudioSegment.from_wav",
                        side_effect=CouldntDecodeError("invalid audio"),
                    ):
                        with raises(
                            ScinoephileError,
                            match="Unable to load AudioSeries from media",
                        ) as excinfo:
                            AudioSeries.load_from_media(
                                media_path=media_path,
                                subtitle_path=subtitle_path,
                            )

    assert isinstance(excinfo.value.__cause__, CouldntDecodeError)


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
                with raises(ScinoephileError, match="No stream index 2"):
                    AudioSeries.load_from_media(
                        media_path=media_path,
                        subtitle_path=subtitle_path,
                        stream_index=2,
                    )


def test_audio_series_load_from_media_loads_wav_without_extraction():
    """Test a standalone WAV is loaded directly without ffmpeg extraction."""
    with get_temp_file_path(".srt") as subtitle_path:
        subtitle_path.write_text(
            "1\n00:00:00,000 --> 00:00:01,000\n你好\n", encoding="utf-8"
        )
        with get_temp_file_path(".wav") as media_path:
            AudioSegment.silent(duration=2000).export(media_path, format="wav")
            with patch("scinoephile.audio.subtitles.series.extract_audio") as extract:
                series = AudioSeries.load_from_media(
                    media_path=media_path,
                    subtitle_path=subtitle_path,
                )

    extract.assert_not_called()
    assert len(series.audio) == 2000


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
                with raises(
                    ScinoephileError, match="Stream index 0 is not an audio stream"
                ):
                    AudioSeries.load_from_media(
                        media_path=media_path,
                        subtitle_path=subtitle_path,
                        stream_index=0,
                    )


def _write_selected_audio(
    infile_path: Path,
    outfile_path: Path,
    *,
    stream_index: int | None = None,
    overwrite: bool = False,
):
    """Write a WAV whose duration identifies the selected stream.

    Arguments:
        infile_path: input media path
        outfile_path: output WAV path
        stream_index: selected audio stream index
        overwrite: whether an existing output may be replaced
    """
    _ = infile_path, overwrite
    if stream_index is None:
        stream_index = 1
    channels = 6 if stream_index == 12 else 2
    AudioSegment.silent(duration=3000 + stream_index * 10 + channels).export(
        outfile_path,
        format="wav",
    )
