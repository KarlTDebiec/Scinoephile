#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of WhisperTranscriber."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from scinoephile.audio.transcription import get_segment_split_at_idx
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcribed_word import TranscribedWord
from scinoephile.audio.transcription.whisper_transcriber import WhisperTranscriber


def test_get_cache_path_separates_vad_modes_with_shared_cache_dir():
    """Test Whisper cache paths differ by VAD mode within one cache directory."""
    vad_on_transcriber = object.__new__(WhisperTranscriber)
    vad_on_transcriber.cache_dir_path = Path("/tmp/whisper")
    vad_on_transcriber.model_name = "custom/model"
    vad_on_transcriber.language = "yue"
    vad_on_transcriber.use_demucs = False
    vad_on_transcriber.use_vad = True

    vad_off_transcriber = object.__new__(WhisperTranscriber)
    vad_off_transcriber.cache_dir_path = Path("/tmp/whisper")
    vad_off_transcriber.model_name = "custom/model"
    vad_off_transcriber.language = "yue"
    vad_off_transcriber.use_demucs = False
    vad_off_transcriber.use_vad = False

    audio = Mock(raw_data=b"audio")
    vad_on_cache_path = vad_on_transcriber._get_cache_path(audio)
    vad_off_cache_path = vad_off_transcriber._get_cache_path(audio)

    assert vad_on_cache_path is not None
    assert vad_off_cache_path is not None
    assert vad_on_cache_path.parent == Path("/tmp/whisper")
    assert vad_off_cache_path.parent == Path("/tmp/whisper")
    assert vad_on_cache_path != vad_off_cache_path


def test_get_cache_path_separates_models():
    """Test Whisper cache paths differ for different model names."""
    transcriber_one = object.__new__(WhisperTranscriber)
    transcriber_one.cache_dir_path = Path("/tmp/whisper")
    transcriber_one.model_name = "model/one"
    transcriber_one.language = "yue"
    transcriber_one.use_demucs = False
    transcriber_one.use_vad = True

    transcriber_two = object.__new__(WhisperTranscriber)
    transcriber_two.cache_dir_path = Path("/tmp/whisper")
    transcriber_two.model_name = "model/two"
    transcriber_two.language = "yue"
    transcriber_two.use_demucs = False
    transcriber_two.use_vad = True

    audio = Mock(raw_data=b"audio")
    cache_path_one = transcriber_one._get_cache_path(audio)
    cache_path_two = transcriber_two._get_cache_path(audio)

    assert cache_path_one is not None
    assert cache_path_two is not None
    assert cache_path_one != cache_path_two


def test_get_cache_path_can_use_original_audio_with_processed_input():
    """Test cache path can be derived from original audio bytes."""
    transcriber = object.__new__(WhisperTranscriber)
    transcriber.cache_dir_path = Path("/tmp/whisper")
    transcriber.model_name = "custom/model"
    transcriber.language = "yue"
    transcriber.use_demucs = False
    transcriber.use_vad = True

    original_audio = Mock(raw_data=b"original-audio")
    processed_audio = Mock(raw_data=b"processed-audio")
    original_cache_path = transcriber._get_cache_path(original_audio)
    processed_cache_path = transcriber._get_cache_path(processed_audio)

    assert original_cache_path is not None
    assert processed_cache_path is not None
    assert original_cache_path != processed_cache_path


def test_get_cache_path_separates_demucs_modes():
    """Test Whisper cache paths differ for Demucs-on and Demucs-off runs."""
    demucs_on_transcriber = object.__new__(WhisperTranscriber)
    demucs_on_transcriber.cache_dir_path = Path("/tmp/whisper")
    demucs_on_transcriber.model_name = "custom/model"
    demucs_on_transcriber.language = "yue"
    demucs_on_transcriber.use_demucs = True
    demucs_on_transcriber.use_vad = True

    demucs_off_transcriber = object.__new__(WhisperTranscriber)
    demucs_off_transcriber.cache_dir_path = Path("/tmp/whisper")
    demucs_off_transcriber.model_name = "custom/model"
    demucs_off_transcriber.language = "yue"
    demucs_off_transcriber.use_demucs = False
    demucs_off_transcriber.use_vad = True

    audio = Mock(raw_data=b"audio")
    demucs_on_cache_path = demucs_on_transcriber._get_cache_path(audio)
    demucs_off_cache_path = demucs_off_transcriber._get_cache_path(audio)

    assert demucs_on_cache_path is not None
    assert demucs_off_cache_path is not None
    assert demucs_on_cache_path != demucs_off_cache_path


def test_normalize_transcription_segments_coalesces_malformed_duplicate_pair():
    """Test malformed empty-text and duplicate-text segments are coalesced."""
    transcriber = object.__new__(WhisperTranscriber)
    transcriber.model_name = "custom/model"
    transcriber.use_vad = True

    segments = [
        TranscribedSegment(
            id=8,
            seek=11520,
            start=156.4,
            end=159.97,
            text="",
            tokens=[],
            temperature=0.0,
            avg_logprob=-1.45,
            compression_ratio=0.0,
            no_speech_prob=1.11e-6,
            words=[
                TranscribedWord(text="照", start=156.4, end=156.85, confidence=0.385),
                TranscribedWord(
                    text="先生",
                    start=156.85,
                    end=157.19,
                    confidence=0.99,
                ),
                TranscribedWord(
                    text="你就",
                    start=157.19,
                    end=158.31,
                    confidence=0.686,
                ),
            ],
        ),
        TranscribedSegment(
            id=9,
            seek=14520,
            start=156.4,
            end=161.29,
            text="照先生你就",
            tokens=[1, 2, 3],
            temperature=0.0,
            avg_logprob=-0.44,
            compression_ratio=0.76,
            no_speech_prob=1.53e-6,
            words=None,
        ),
    ]

    normalized_segments = transcriber._normalize_transcription_segments(
        segments,
        source="cache",
        cache_path=Path("/tmp/whisper.json"),
    )

    assert len(normalized_segments) == 1
    assert normalized_segments[0].id == 9
    assert normalized_segments[0].start == 156.4
    assert normalized_segments[0].end == 161.29
    assert normalized_segments[0].text == "照先生你就"
    assert normalized_segments[0].words is not None
    assert [word.text for word in normalized_segments[0].words] == [
        "照",
        "先生",
        "你就",
    ]


def test_get_segment_split_at_idx_includes_segment_details_in_error():
    """Test split error includes identifying segment details."""
    segment = TranscribedSegment(
        id=9,
        seek=14520,
        start=156.4,
        end=161.29,
        text="照先生你就展示畀朕睇下係",
        words=None,
    )

    try:
        get_segment_split_at_idx(segment, 3)
    except ValueError as exc:
        assert str(exc) == (
            "Cannot split segment without word timing data: "
            "id=9 start=156.4 end=161.29 text='照先生你就展示畀朕睇下係' text_len=12."
        )
    else:
        raise AssertionError("Expected ValueError")
