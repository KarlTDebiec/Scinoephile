#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of get_yue_audio_series_for_transcription."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from pydub import AudioSegment

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common.file import get_temp_file_path
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.multilang.yue_zho.transcription import (
    get_yue_audio_series_for_transcription,
)


def test_get_yue_audio_series_for_transcription_supports_stream_index():
    """Test media loading helper probes media and loads requested audio stream."""
    zhongwen_series = Series.from_string(
        "1\n00:00:01,000 --> 00:00:02,000\n你好\n",
        format_="srt",
    )
    full_audio = AudioSegment.silent(duration=3000)

    with get_temp_file_path(".mp4") as media_path:
        media_path.touch()
        with patch(
            "scinoephile.multilang.yue_zho.transcription.ffmpeg.probe",
            return_value={
                "streams": [
                    {"codec_type": "video"},
                    {"codec_type": "audio", "channels": 2},
                    {"codec_type": "audio", "channels": 6},
                ]
            },
        ):
            with patch(
                "scinoephile.multilang.yue_zho.transcription.AudioSeries.extract_audio_track"
            ) as extract_audio_track:
                with patch(
                    "scinoephile.multilang.yue_zho.transcription.AudioSegment.from_wav",
                    return_value=full_audio,
                ):
                    yuewen_series = get_yue_audio_series_for_transcription(
                        zhongwen=zhongwen_series,
                        media_path=media_path,
                        stream_index=1,
                    )

    assert isinstance(yuewen_series, AudioSeries)
    assert [event.text for event in yuewen_series.events] == ["你好"]
    extract_audio_track.assert_called_once()
    assert extract_audio_track.call_args.args[2] == 1
    assert extract_audio_track.call_args.args[3] == 6


def test_get_yue_audio_series_for_transcription_rejects_invalid_stream_index():
    """Test media loading helper rejects invalid stream indexes."""
    zhongwen_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )

    with get_temp_file_path(".mp4") as media_path:
        media_path.touch()
        with patch(
            "scinoephile.multilang.yue_zho.transcription.ffmpeg.probe",
            return_value={"streams": [{"codec_type": "audio", "channels": 2}]},
        ):
            with pytest.raises(ScinoephileError, match="Invalid audio stream index 1"):
                get_yue_audio_series_for_transcription(
                    zhongwen=zhongwen_series,
                    media_path=media_path,
                    stream_index=1,
                )
