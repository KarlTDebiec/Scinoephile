#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of YueTranscriber internals."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock, patch

from scinoephile.audio.transcription import TranscribedSegment
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.multilang.yue_zho.transcription.transcriber import (
    DemucsMode,
    VADMode,
    YueTranscriber,
)


def test_transcribe_block_audio_applies_demucs_before_vad_retry():
    """Test block transcription applies Demucs before VAD retry."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.vad_mode = VADMode.AUTO
    transcriber.demucs_mode = DemucsMode.ON
    transcriber.demucs_separator = Mock()
    transcriber.vad_transcriber = Mock(return_value=[Mock(text="   ")])
    transcriber.no_vad_transcriber = Mock(return_value=[Mock(text="你好")])
    transcriber.vad_transcriber.get_cached_transcription.return_value = None
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = None

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"
    separated_audio = Mock()
    transcriber.demucs_separator.return_value = separated_audio

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == transcriber.no_vad_transcriber.return_value
    transcriber.demucs_separator.assert_called_once_with(input_audio)
    transcriber.vad_transcriber.assert_called_once_with(
        separated_audio, cache_audio=input_audio
    )
    transcriber.no_vad_transcriber.assert_called_once_with(
        separated_audio, cache_audio=input_audio
    )


def test_transcribe_block_audio_uses_vad_cache_before_demucs():
    """Test VAD cache hit short-circuits before Demucs preprocessing."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.vad_mode = VADMode.ON
    transcriber.demucs_mode = DemucsMode.ON
    transcriber.demucs_separator = Mock()
    transcriber.vad_transcriber = Mock()
    transcriber.no_vad_transcriber = None

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"
    cached_segments = [Mock(text="cached")]
    transcriber.vad_transcriber.get_cached_transcription.return_value = cached_segments

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == cached_segments
    transcriber.vad_transcriber.get_cached_transcription.assert_called_once_with(
        input_audio
    )
    transcriber.demucs_separator.assert_not_called()
    transcriber.vad_transcriber.assert_not_called()


def test_transcribe_block_audio_auto_ignores_no_vad_cache_before_vad_attempt():
    """Test AUTO mode still tries VAD before using only no-VAD cached output."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.vad_mode = VADMode.AUTO
    transcriber.demucs_mode = DemucsMode.OFF
    transcriber.demucs_separator = None
    transcriber.vad_transcriber = Mock(return_value=[Mock(text="你好")])
    transcriber.no_vad_transcriber = Mock()
    transcriber.vad_transcriber.get_cached_transcription.return_value = None
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = [
        Mock(text="cached-no-vad")
    ]

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == transcriber.vad_transcriber.return_value
    transcriber.vad_transcriber.get_cached_transcription.assert_called_once_with(
        input_audio
    )
    transcriber.no_vad_transcriber.get_cached_transcription.assert_not_called()
    transcriber.vad_transcriber.assert_called_once_with(
        input_audio, cache_audio=input_audio
    )
    transcriber.no_vad_transcriber.assert_not_called()


def test_transcribe_block_audio_treats_cached_empty_segments_as_hit():
    """Test cached empty segment lists short-circuit without retranscribing."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.vad_mode = VADMode.ON
    transcriber.demucs_mode = DemucsMode.ON
    transcriber.demucs_separator = Mock()
    transcriber.vad_transcriber = Mock()
    transcriber.no_vad_transcriber = None

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"
    transcriber.vad_transcriber.get_cached_transcription.return_value = []

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == []
    transcriber.vad_transcriber.get_cached_transcription.assert_called_once_with(
        input_audio
    )
    transcriber.demucs_separator.assert_not_called()
    transcriber.vad_transcriber.assert_not_called()


def test_transcribe_block_audio_auto_retries_when_vad_cache_is_whitespace_only():
    """Test AUTO mode ignores cached whitespace-only VAD output and retries."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.vad_mode = VADMode.AUTO
    transcriber.demucs_mode = DemucsMode.OFF
    transcriber.demucs_separator = None
    transcriber.vad_transcriber = Mock(return_value=[Mock(text="   ")])
    transcriber.no_vad_transcriber = Mock(return_value=[Mock(text="你好")])
    transcriber.vad_transcriber.get_cached_transcription.return_value = [
        Mock(text="   ")
    ]
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = [
        Mock(text="cached-no-vad")
    ]

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == transcriber.no_vad_transcriber.return_value
    transcriber.vad_transcriber.get_cached_transcription.assert_called_once_with(
        input_audio
    )
    transcriber.no_vad_transcriber.get_cached_transcription.assert_not_called()
    transcriber.vad_transcriber.assert_called_once_with(
        input_audio, cache_audio=input_audio
    )
    transcriber.no_vad_transcriber.assert_called_once_with(
        input_audio, cache_audio=input_audio
    )


def test_get_whisper_transcriber_sets_use_demucs():
    """Test Whisper transcriber cache keys distinguish Demucs mode."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.model_name = "custom/model"
    transcriber.demucs_mode = DemucsMode.ON

    whisper_transcriber = transcriber._get_whisper_transcriber(use_vad=True)

    assert whisper_transcriber.use_demucs is True


def test_process_block_leaves_text_unchanged_without_conversion():
    """Test process_block skips OpenCC conversion by default."""
    transcriber = YueTranscriber.__new__(YueTranscriber)
    transcriber.convert = None
    transcriber.aligner = Mock()
    expected_series = Mock()
    transcriber.aligner.align.return_value = SimpleNamespace(yuewen=expected_series)
    transcriber.aligner.update_all_test_cases = Mock()
    segments = [TranscribedSegment(id=0, seek=0, start=0.0, end=1.0, text="學校")]
    yuewen_block = Mock()
    yuewen_block.audio = Mock()
    yuewen_block.__getitem__ = Mock(return_value=SimpleNamespace(start=1.25))
    zhongwen_block = Mock()
    interim_series = Mock()

    with patch.object(
        YueTranscriber,
        "_transcribe_block_audio",
        return_value=segments,
    ):
        with patch(
            "scinoephile.multilang.yue_zho.transcription.transcriber.get_series_from_segments",
            return_value=interim_series,
        ) as patched_get_series:
            with patch(
                "scinoephile.multilang.yue_zho.transcription.transcriber.get_segment_zho_converted"
            ) as patched_convert:
                output_series = transcriber.process_block(yuewen_block, zhongwen_block)

    assert output_series is expected_series
    patched_convert.assert_not_called()
    patched_get_series.assert_called_once_with(
        segments,
        audio=yuewen_block.audio,
        offset=1.25,
    )
    transcriber.aligner.align.assert_called_once_with(zhongwen_block, interim_series)
    transcriber.aligner.update_all_test_cases.assert_called_once_with()


def test_process_block_converts_text_when_requested():
    """Test process_block applies OpenCC conversion when configured."""
    transcriber = YueTranscriber.__new__(YueTranscriber)
    transcriber.convert = OpenCCConfig.hk2s
    transcriber.aligner = Mock()
    expected_series = Mock()
    transcriber.aligner.align.return_value = SimpleNamespace(yuewen=expected_series)
    transcriber.aligner.update_all_test_cases = Mock()
    segments = [TranscribedSegment(id=0, seek=0, start=0.0, end=1.0, text="學校")]
    converted_segments = [Mock()]
    yuewen_block = Mock()
    yuewen_block.audio = Mock()
    yuewen_block.__getitem__ = Mock(return_value=SimpleNamespace(start=0.5))
    zhongwen_block = Mock()

    with patch.object(
        YueTranscriber,
        "_transcribe_block_audio",
        return_value=segments,
    ):
        with patch(
            "scinoephile.multilang.yue_zho.transcription.transcriber.get_series_from_segments",
            return_value=Mock(),
        ) as patched_get_series:
            with patch(
                "scinoephile.multilang.yue_zho.transcription.transcriber.get_segment_zho_converted",
                side_effect=converted_segments,
            ) as patched_convert:
                output_series = transcriber.process_block(yuewen_block, zhongwen_block)

    assert output_series is expected_series
    patched_convert.assert_called_once_with(segments[0], OpenCCConfig.hk2s)
    patched_get_series.assert_called_once_with(
        converted_segments,
        audio=yuewen_block.audio,
        offset=0.5,
    )
