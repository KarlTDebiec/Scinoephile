#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of AudioSeries.load_from_media."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pydub import AudioSegment
from pytest import raises

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common.file import get_temp_file_path
from scinoephile.core import ScinoephileError
from scinoephile.media.audio import AudioExtractionMode


def test_audio_series_load_from_media_without_subtitles_returns_complete_audio():
    """Test whole-media audio loading returns an empty WAV-backed series."""
    with get_temp_file_path(".mp4") as media_path:
        media_path.touch()
        with patch(
            "scinoephile.audio.subtitles.series.load_audio_segment",
            return_value=AudioSegment.silent(duration=3126),
        ) as load_audio:
            series = AudioSeries.load_from_media(
                str(media_path), stream_index=12, mode=AudioExtractionMode.CENTER_HEAVY
            )

    load_audio.assert_called_once_with(
        media_path.resolve(), stream_index=12, mode=AudioExtractionMode.CENTER_HEAVY
    )
    assert len(series.audio) == 3126
    assert series.events == []
    assert series.format == "wav"


def test_audio_series_load_from_media_supports_stream_index():
    """Test media loading forwards the requested audio stream."""
    with get_temp_file_path(".srt") as subtitle_path:
        subtitle_path.write_text(
            "1\n00:00:01,000 --> 00:00:02,000\n你好\n", encoding="utf-8"
        )
        with get_temp_file_path(".mp4") as media_path:
            media_path.touch()
            with patch(
                "scinoephile.audio.subtitles.series.load_audio_segment",
                return_value=AudioSegment.silent(duration=3126),
            ) as load_audio:
                yuewen_series = AudioSeries.load_from_media(
                    media_path=media_path, subtitle_path=subtitle_path, stream_index=12
                )

    load_audio.assert_called_once_with(
        media_path.resolve(), stream_index=12, mode=AudioExtractionMode.ORIGINAL
    )
    assert isinstance(yuewen_series, AudioSeries)
    assert [event.text for event in yuewen_series.events] == ["你好"]
    assert len(yuewen_series.audio) == 3126


def test_audio_series_load_from_media_defaults_to_first_audio_stream():
    """Test media loading defaults to the first audio stream."""
    with get_temp_file_path(".srt") as subtitle_path:
        subtitle_path.write_text(
            "1\n00:00:01,000 --> 00:00:02,000\n你好\n", encoding="utf-8"
        )
        with get_temp_file_path(".mp4") as media_path:
            media_path.touch()
            with patch(
                "scinoephile.audio.subtitles.series.load_audio_segment",
                return_value=AudioSegment.silent(duration=3012),
            ) as load_audio:
                yuewen_series = AudioSeries.load_from_media(
                    media_path=media_path, subtitle_path=subtitle_path
                )

    load_audio.assert_called_once_with(
        media_path.resolve(), stream_index=None, mode=AudioExtractionMode.ORIGINAL
    )
    assert isinstance(yuewen_series, AudioSeries)
    assert [event.text for event in yuewen_series.events] == ["你好"]
    assert len(yuewen_series.audio) == 3012


def test_audio_series_load_from_media_wraps_subtitle_path_errors(tmp_path: Path):
    """Test subtitle path errors are user-facing.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    media_path = tmp_path / "media.mkv"
    media_path.touch()
    with raises(
        ScinoephileError, match="Unable to load AudioSeries from media"
    ) as excinfo:
        AudioSeries.load_from_media(
            media_path=media_path, subtitle_path=tmp_path / "missing.srt"
        )

    assert isinstance(excinfo.value.__cause__, OSError)
