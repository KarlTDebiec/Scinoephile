#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of AudioSeries.load_from_media."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from pydub import AudioSegment

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common.file import get_temp_file_path
from scinoephile.core import ScinoephileError


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
                "scinoephile.audio.subtitles.series.ffmpeg.probe",
                return_value={
                    "streams": [
                        {"codec_type": "video"},
                        {"codec_type": "audio", "channels": 2},
                        {"codec_type": "audio", "channels": 6},
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
                            stream_index=1,
                        )

    assert isinstance(yuewen_series, AudioSeries)
    assert [event.text for event in yuewen_series.events] == ["你好"]
    extract_audio_track.assert_called_once()
    assert extract_audio_track.call_args.args[2] == 1
    assert extract_audio_track.call_args.args[3] == 6


def test_audio_series_load_from_media_rejects_invalid_stream_index():
    """Test media loading rejects invalid stream indexes."""
    with get_temp_file_path(".srt") as subtitle_path:
        subtitle_path.write_text(
            "1\n00:00:00,000 --> 00:00:01,000\n你好\n", encoding="utf-8"
        )
        with get_temp_file_path(".mp4") as media_path:
            media_path.touch()
            with patch(
                "scinoephile.audio.subtitles.series.ffmpeg.probe",
                return_value={"streams": [{"codec_type": "audio", "channels": 2}]},
            ):
                with pytest.raises(
                    ScinoephileError, match="Invalid audio stream index 1"
                ):
                    AudioSeries.load_from_media(
                        media_path=media_path,
                        subtitle_path=subtitle_path,
                        stream_index=1,
                    )
