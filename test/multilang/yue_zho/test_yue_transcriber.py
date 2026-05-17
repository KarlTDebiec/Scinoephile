#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of YueTranscriber internals."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from scinoephile.audio.transcription import TranscribedSegment, TranscribedWord
from scinoephile.audio.transcription.mimo_transcriber import MimoTranscriptionError
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.multilang.yue_zho.transcription.transcriber import (
    DemucsMode,
    MimoRuntime,
    TranscriptionBackend,
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
    cached_segments = [_get_transcribed_segment("cached")]
    transcriber.vad_transcriber.get_cached_transcription.return_value = cached_segments

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == cached_segments
    transcriber.vad_transcriber.get_cached_transcription.assert_called_once_with(
        input_audio
    )
    transcriber.demucs_separator.assert_not_called()
    transcriber.vad_transcriber.assert_not_called()


def test_transcribe_block_audio_auto_uses_no_vad_cache_when_vad_cache_misses():
    """Test AUTO mode uses usable no-VAD cache after a VAD-cache miss."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.vad_mode = VADMode.AUTO
    transcriber.demucs_mode = DemucsMode.OFF
    transcriber.demucs_separator = None
    transcriber.vad_transcriber = Mock(return_value=[Mock(text="你好")])
    transcriber.no_vad_transcriber = Mock()
    transcriber.vad_transcriber.get_cached_transcription.return_value = None
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = [
        _get_transcribed_segment("cached-no-vad")
    ]

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"

    output = transcriber._transcribe_block_audio(input_audio)

    assert (
        output == transcriber.no_vad_transcriber.get_cached_transcription.return_value
    )
    transcriber.vad_transcriber.get_cached_transcription.assert_called_once_with(
        input_audio
    )
    transcriber.no_vad_transcriber.get_cached_transcription.assert_called_once_with(
        input_audio
    )
    transcriber.vad_transcriber.assert_not_called()
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


def test_transcribe_block_audio_auto_uses_no_vad_cache_when_vad_cache_is_whitespace():
    """Test AUTO mode uses no-VAD cache after whitespace-only VAD cache."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.vad_mode = VADMode.AUTO
    transcriber.demucs_mode = DemucsMode.OFF
    transcriber.demucs_separator = None
    transcriber.vad_transcriber = Mock(return_value=[Mock(text="   ")])
    transcriber.no_vad_transcriber = Mock(return_value=[Mock(text="你好")])
    transcriber.vad_transcriber.get_cached_transcription.return_value = [
        _get_transcribed_segment("   ", include_words=False)
    ]
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = [
        _get_transcribed_segment("cached-no-vad")
    ]

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"

    output = transcriber._transcribe_block_audio(input_audio)

    assert (
        output == transcriber.no_vad_transcriber.get_cached_transcription.return_value
    )
    transcriber.vad_transcriber.get_cached_transcription.assert_called_once_with(
        input_audio
    )
    transcriber.no_vad_transcriber.get_cached_transcription.assert_called_once_with(
        input_audio
    )
    transcriber.vad_transcriber.assert_not_called()
    transcriber.no_vad_transcriber.assert_not_called()


def test_transcribe_block_audio_auto_retries_when_vad_cache_has_text_without_words():
    """Test AUTO mode uses no-VAD cache after unusable cached VAD output."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.vad_mode = VADMode.AUTO
    transcriber.demucs_mode = DemucsMode.OFF
    transcriber.demucs_separator = None
    transcriber.vad_transcriber = Mock(return_value=[Mock(text="你好")])
    transcriber.no_vad_transcriber = Mock(return_value=[Mock(text="fallback")])
    transcriber.vad_transcriber.get_cached_transcription.return_value = [
        TranscribedSegment(id=0, seek=0, start=0.0, end=1.0, text="你好", words=None)
    ]
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = [
        _get_transcribed_segment("cached-no-vad")
    ]

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"

    output = transcriber._transcribe_block_audio(input_audio)

    assert (
        output == transcriber.no_vad_transcriber.get_cached_transcription.return_value
    )
    transcriber.vad_transcriber.get_cached_transcription.assert_called_once_with(
        input_audio
    )
    transcriber.no_vad_transcriber.get_cached_transcription.assert_called_once_with(
        input_audio
    )
    transcriber.vad_transcriber.assert_not_called()
    transcriber.no_vad_transcriber.assert_not_called()


def test_transcribe_block_audio_auto_retries_when_vad_result_has_text_without_words():
    """Test AUTO mode retries when VAD transcription lacks word timings."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.vad_mode = VADMode.AUTO
    transcriber.demucs_mode = DemucsMode.OFF
    transcriber.demucs_separator = None
    transcriber.vad_transcriber = Mock(
        return_value=[
            TranscribedSegment(
                id=0,
                seek=0,
                start=0.0,
                end=1.0,
                text="你好",
                words=None,
            )
        ]
    )
    transcriber.no_vad_transcriber = Mock(return_value=[Mock(text="fallback")])
    transcriber.vad_transcriber.get_cached_transcription.return_value = None
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = None

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == transcriber.no_vad_transcriber.return_value
    transcriber.vad_transcriber.get_cached_transcription.assert_called_once_with(
        input_audio
    )
    transcriber.vad_transcriber.assert_called_once_with(
        input_audio, cache_audio=input_audio
    )
    transcriber.no_vad_transcriber.assert_called_once_with(
        input_audio, cache_audio=input_audio
    )


def test_transcribe_block_audio_whisper_uses_mimo_fallback_when_unusable():
    """Test Whisper primary mode can fall back to MiMo for unusable output."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.backend = TranscriptionBackend.WHISPER
    transcriber.vad_mode = VADMode.OFF
    transcriber.demucs_mode = DemucsMode.OFF
    transcriber.demucs_separator = None
    transcriber.mimo_fallback = True
    transcriber.no_vad_transcriber = Mock(
        return_value=[
            TranscribedSegment(
                id=0,
                seek=0,
                start=0.0,
                end=1.0,
                text="你好",
                words=None,
            )
        ]
    )
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = None
    transcriber.vad_transcriber = None
    transcriber.mimo_transcriber = Mock(return_value=[_get_transcribed_segment("mimo")])

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == transcriber.mimo_transcriber.return_value
    transcriber.no_vad_transcriber.assert_called_once_with(
        input_audio, cache_audio=input_audio
    )
    transcriber.mimo_transcriber.assert_called_once_with(
        input_audio, cache_audio=input_audio
    )


def test_transcribe_block_audio_whisper_skips_mimo_fallback_when_usable():
    """Test Whisper primary mode does not call MiMo when Whisper works."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.backend = TranscriptionBackend.WHISPER
    transcriber.vad_mode = VADMode.OFF
    transcriber.demucs_mode = DemucsMode.OFF
    transcriber.demucs_separator = None
    transcriber.mimo_fallback = True
    transcriber.no_vad_transcriber = Mock(return_value=[_get_transcribed_segment("ok")])
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = None
    transcriber.vad_transcriber = None
    transcriber.mimo_transcriber = Mock()

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == transcriber.no_vad_transcriber.return_value
    transcriber.mimo_transcriber.assert_not_called()


@pytest.mark.parametrize(
    "error_message",
    [
        "Inconsistent number of segments: 8 != 7",
        "other failure",
    ],
)
def test_transcribe_block_audio_auto_retries_when_vad_raises_assertion(
    error_message: str,
):
    """Test AUTO mode retries on VAD assertion failures.

    Arguments:
        error_message: assertion message raised by VAD transcription
    """
    transcriber = object.__new__(YueTranscriber)
    transcriber.vad_mode = VADMode.AUTO
    transcriber.demucs_mode = DemucsMode.OFF
    transcriber.demucs_separator = None
    transcriber.vad_transcriber = Mock(side_effect=AssertionError(error_message))
    transcriber.no_vad_transcriber = Mock(return_value=[Mock(text="fallback")])
    transcriber.vad_transcriber.get_cached_transcription.return_value = None
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = None

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == transcriber.no_vad_transcriber.return_value
    transcriber.vad_transcriber.get_cached_transcription.assert_called_once_with(
        input_audio
    )
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


def test_get_mimo_transcriber_forwards_runtime():
    """Test YueTranscriber forwards the selected MiMo runtime."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.mimo_model_name = "custom/model"
    transcriber.mimo_tokenizer_name = "custom/tokenizer"
    transcriber.mimo_runtime = MimoRuntime.MLX
    transcriber.mimo_language = "auto"
    transcriber.mimo_max_tokens = 1024
    transcriber.mimo_chunk_duration_seconds = 20.0
    transcriber.mimo_chunk_overlap_seconds = 1.5
    transcriber.mimo_worker_command = None
    transcriber.mimo_aligner_backend = "whisperx"
    transcriber.mimo_aligner_language = "zh"
    transcriber.mimo_aligner_model_name = None
    transcriber.mimo_aligner_worker_command = ("python", "aligner_worker.py")
    transcriber.demucs_mode = DemucsMode.OFF
    transcriber.vad_mode = VADMode.AUTO

    mimo_transcriber = transcriber._get_mimo_transcriber()

    assert mimo_transcriber.mimo_runtime == MimoRuntime.MLX
    assert mimo_transcriber.language == "auto"
    assert mimo_transcriber.max_tokens == 1024
    assert mimo_transcriber.chunk_duration_seconds == 20.0
    assert mimo_transcriber.chunk_overlap_seconds == 1.5
    assert mimo_transcriber.aligner_worker_command == (
        "python",
        "aligner_worker.py",
    )


def test_transcribe_block_audio_mimo_uses_mimo_cache_before_demucs():
    """Test MiMo cache hit short-circuits before Demucs preprocessing."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.backend = TranscriptionBackend.MIMO
    transcriber.demucs_mode = DemucsMode.ON
    transcriber.demucs_separator = Mock()
    transcriber.mimo_transcriber = Mock()
    transcriber.mimo_transcriber.get_cached_transcription.return_value = [
        _get_transcribed_segment("cached-mimo")
    ]

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == transcriber.mimo_transcriber.get_cached_transcription.return_value
    transcriber.mimo_transcriber.get_cached_transcription.assert_called_once_with(
        input_audio
    )
    transcriber.demucs_separator.assert_not_called()
    transcriber.mimo_transcriber.assert_not_called()


def test_transcribe_block_audio_mimo_applies_demucs_then_transcribes():
    """Test MiMo transcription receives separated audio and original cache audio."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.backend = TranscriptionBackend.MIMO
    transcriber.demucs_mode = DemucsMode.ON
    transcriber.demucs_separator = Mock()
    transcriber.mimo_transcriber = Mock(return_value=[_get_transcribed_segment("你好")])
    transcriber.mimo_transcriber.get_cached_transcription.return_value = None

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"
    separated_audio = Mock()
    transcriber.demucs_separator.return_value = separated_audio

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == transcriber.mimo_transcriber.return_value
    transcriber.demucs_separator.assert_called_once_with(input_audio)
    transcriber.mimo_transcriber.assert_called_once_with(
        separated_audio, cache_audio=input_audio
    )


def test_transcribe_block_audio_mimo_falls_back_to_whisper_when_enabled():
    """Test MiMo backend can fall back to Whisper-style VAD behavior."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.backend = TranscriptionBackend.MIMO
    transcriber.demucs_mode = DemucsMode.OFF
    transcriber.mimo_fallback = True
    transcriber.mimo_transcriber = Mock(side_effect=MimoTranscriptionError("failed"))
    transcriber.mimo_transcriber.get_cached_transcription.return_value = None
    transcriber.vad_mode = VADMode.ON
    transcriber.vad_transcriber = Mock(
        return_value=[_get_transcribed_segment("fallback")]
    )
    transcriber.vad_transcriber.get_cached_transcription.return_value = None
    transcriber.no_vad_transcriber = None

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == transcriber.vad_transcriber.return_value
    transcriber.mimo_transcriber.assert_called_once_with(
        input_audio, cache_audio=input_audio
    )
    transcriber.vad_transcriber.assert_called_once_with(
        input_audio, cache_audio=input_audio
    )


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


def _get_transcribed_segment(
    text: str, *, include_words: bool = True
) -> TranscribedSegment:
    """Get a transcribed segment for test assertions.

    Arguments:
        text: segment text
        include_words: whether to include word timings matching text
    Returns:
        transcribed segment
    """
    words = None
    if include_words:
        words = [
            TranscribedWord(text=text, start=0.0, end=1.0, confidence=1.0),
        ]
    return TranscribedSegment(
        id=0,
        seek=0,
        start=0.0,
        end=1.0,
        text=text,
        words=words,
    )
