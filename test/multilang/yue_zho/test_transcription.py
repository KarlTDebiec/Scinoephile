#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.multilang.yue_zho.transcription."""

from __future__ import annotations

from typing import cast
from unittest.mock import Mock, patch

import pytest
from pydub import AudioSegment

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common.file import get_temp_directory_path, get_temp_file_path
from scinoephile.core import ScinoephileError
from scinoephile.core.llms import TestCase
from scinoephile.core.subtitles import Series
from scinoephile.multilang.yue_zho.transcription import (
    get_yue_audio_series_for_transcription,
    get_yue_transcribed_vs_zho,
    get_yue_transcriber_vs_zho,
)


def test_get_yue_audio_series_for_transcription_supports_stream_index():
    """Test media loading helper probes media and loads requested audio stream."""
    zhongwen = Series.from_string(
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
            ) as extract_audio:
                with patch(
                    "scinoephile.multilang.yue_zho.transcription.AudioSegment.from_wav",
                    return_value=full_audio,
                ):
                    yuewen = get_yue_audio_series_for_transcription(
                        zhongwen=zhongwen,
                        media_path=media_path,
                        stream_index=1,
                    )

    assert isinstance(yuewen, AudioSeries)
    assert [event.text for event in yuewen.events] == ["你好"]
    extract_audio.assert_called_once()
    assert extract_audio.call_args.args[2] == 1
    assert extract_audio.call_args.args[3] == 6


def test_get_yue_audio_series_for_transcription_rejects_invalid_stream_index():
    """Test media loading helper rejects invalid stream indexes."""
    zhongwen = Series.from_string(
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
                    zhongwen=zhongwen,
                    media_path=media_path,
                    stream_index=1,
                )


def test_get_yue_transcribed_vs_zho_dispatches_media_and_stream_index():
    """Test transcription entrypoint dispatches media loading and block processing."""
    zhongwen = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    media_path = "/tmp/test_media.mp4"
    yuewen_audio = Mock(spec=AudioSeries)
    expected = Mock(spec=AudioSeries)
    transcriber = Mock()
    transcriber.process_all_blocks.return_value = expected

    with patch(
        "scinoephile.multilang.yue_zho.transcription.get_yue_audio_series_for_transcription",
        return_value=yuewen_audio,
    ) as patched_media_loader:
        result = get_yue_transcribed_vs_zho(
            zhongwen=zhongwen,
            media_path=media_path,
            stream_index=3,
            transcriber=transcriber,
        )

    assert result == expected
    patched_media_loader.assert_called_once_with(
        zhongwen=zhongwen,
        media_path=media_path,
        stream_index=3,
    )
    transcriber.process_all_blocks.assert_called_once_with(yuewen_audio, zhongwen)


def test_get_yue_transcriber_vs_zho_uses_writable_runtime_test_case_root():
    """Test default transcriber setup uses a writable runtime test-case root."""
    shifting_test_cases = [cast(TestCase, Mock())]
    merging_test_cases = [cast(TestCase, Mock())]

    with get_temp_directory_path() as temp_dir_path:
        runtime_test_case_dir_path = temp_dir_path / "test_cases"
        with patch(
            "scinoephile.multilang.yue_zho.transcription.get_runtime_cache_dir_path",
            return_value=runtime_test_case_dir_path,
        ):
            with patch(
                "scinoephile.multilang.yue_zho.transcription.YueTranscriber"
            ) as patched_transcriber:
                get_yue_transcriber_vs_zho(
                    shifting_test_cases=shifting_test_cases,
                    merging_test_cases=merging_test_cases,
                )
        patched_transcriber.assert_called_once_with(
            test_case_directory_path=runtime_test_case_dir_path,
            shifting_test_cases=shifting_test_cases,
            merging_test_cases=merging_test_cases,
        )
        assert (
            runtime_test_case_dir_path
            / "multilang"
            / "yue_zho"
            / "transcription"
            / "shifting"
        ).is_dir()
        assert (
            runtime_test_case_dir_path
            / "multilang"
            / "yue_zho"
            / "transcription"
            / "merging"
        ).is_dir()
