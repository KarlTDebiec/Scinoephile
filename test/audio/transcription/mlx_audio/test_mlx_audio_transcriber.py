#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of MlxAudioTranscriber."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock

import numpy as np
import pytest
from pydub import AudioSegment

from scinoephile.audio.transcription import (
    CtcAligner,
    DemucsMode,
    TranscribedSegment,
    TranscribedWord,
    TranscriptionAlignmentError,
    TranscriptionAlignmentIncompleteError,
    TranscriptionEmptyError,
    TranscriptionError,
    TranscriptionPreprocessingSettings,
    TranscriptionRecognitionError,
    VadMode,
)
from scinoephile.audio.transcription.mlx_audio.model_spec import (
    FIRERED_ASR2_MODEL,
    GLM_ASR_MODEL,
    MIMO_MODEL,
    QWEN3_ASR_MODEL,
    SENSEVOICE_MODEL,
    MlxAudioModelSpec,
)
from scinoephile.audio.transcription.mlx_audio.recognizer import (
    MlxAudioRecognizer,
    MlxAudioResult,
)
from scinoephile.audio.transcription.mlx_audio.transcriber import MlxAudioTranscriber
from scinoephile.audio.vad import (
    VadImplementation,
    VoiceActivityDetector,
    VoiceActivityTrace,
)
from scinoephile.core import Language


@pytest.fixture(autouse=True)
def use_apple_silicon_platform(monkeypatch: pytest.MonkeyPatch):
    """Run MLX-Audio transcriber tests as though on the supported platform."""
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mlx_audio.transcriber.platform.system",
        Mock(return_value="Darwin"),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mlx_audio.transcriber.platform.machine",
        Mock(return_value="arm64"),
    )


def _get_cache_path(
    transcriber: MlxAudioTranscriber,
    audio: AudioSegment,
    use_demucs: bool = False,
    use_vad: bool = False,
) -> Path:
    """Get the cache path for one preprocessing configuration."""
    settings = TranscriptionPreprocessingSettings(use_demucs, use_vad)
    cache_path = transcriber._cache.get_path(
        audio, transcriber._get_cache_identity(audio, settings)
    )
    assert cache_path is not None
    return cache_path


def test_init_defaults_demucs_and_vad_to_off():
    """Test MLX-Audio defaults Demucs and VAD to off."""
    transcriber = MlxAudioTranscriber(MIMO_MODEL)

    assert transcriber.demucs_mode is DemucsMode.OFF
    assert transcriber.vad_mode is VadMode.OFF
    assert transcriber.demucs_separator is None
    assert transcriber.model is MIMO_MODEL
    assert transcriber.language is Language.yue_hant
    assert transcriber.token_limit_guard is False


def test_get_cache_path_separates_model_configuration(runtime_cache_root_path: Path):
    """Test MLX-Audio cache paths differ by model configuration.

    Arguments:
        runtime_cache_root_path: isolated default runtime cache root
    """
    audio = _get_cache_audio()
    first_transcriber = _get_mlx_audio_transcriber(
        model=replace(
            MIMO_MODEL, name="custom/MiMo-V2.5-ASR-one", revision="revision-one"
        )
    )
    second_transcriber = _get_mlx_audio_transcriber(
        model=replace(
            MIMO_MODEL, name="custom/MiMo-V2.5-ASR-two", revision="revision-two"
        )
    )

    first_cache_path = _get_cache_path(first_transcriber, audio)
    second_cache_path = _get_cache_path(second_transcriber, audio)
    expected_cache_dir_path = runtime_cache_root_path / "audio/transcription/mlx_audio"

    assert first_cache_path.parent == expected_cache_dir_path
    assert second_cache_path.parent == expected_cache_dir_path
    assert first_cache_path != second_cache_path


def test_get_cache_path_separates_ctc_model_configuration():
    """Test MLX-Audio cache paths differ by CTC model configuration."""
    audio = _get_cache_audio()
    first_transcriber = _get_mlx_audio_transcriber(model=MIMO_MODEL)
    second_transcriber = _get_mlx_audio_transcriber(model=MIMO_MODEL)
    first_transcriber.ctc_aligner = CtcAligner(Language.yue_hant, "ctc/one")
    second_transcriber.ctc_aligner = CtcAligner(Language.yue_hant, "ctc/two")

    first_cache_path = _get_cache_path(first_transcriber, audio)
    second_cache_path = _get_cache_path(second_transcriber, audio)

    assert first_cache_path != second_cache_path


def test_get_cache_path_separates_model_revisions():
    """Test remote model revisions contribute to MLX-Audio cache identity."""
    audio = _get_cache_audio()
    first_transcriber = _get_mlx_audio_transcriber(
        model=replace(MIMO_MODEL, revision="revision-one")
    )
    second_transcriber = _get_mlx_audio_transcriber(
        model=replace(MIMO_MODEL, revision="revision-two")
    )

    assert _get_cache_path(first_transcriber, audio) != _get_cache_path(
        second_transcriber, audio
    )


def test_get_cache_path_uses_mlx_runtime_on_apple_silicon():
    """Test the cache identity includes MLX-Audio runtime provenance."""
    transcriber = _get_mlx_audio_transcriber(model=MIMO_MODEL)

    cache_identity = transcriber._get_cache_identity(
        _get_cache_audio(), TranscriptionPreprocessingSettings(False, False)
    )

    runtime_identity = cast(Mapping[str, object], cache_identity["runtime"])
    assert runtime_identity["distribution"] == "mlx-audio"
    assert runtime_identity["source_revision"] == (
        "ff0197c0ae9f9fd02072904c696f2533e329c06e"
    )


@pytest.mark.parametrize(
    ("system", "machine"),
    [("Linux", "arm64"), ("Darwin", "x86_64"), ("Windows", "ARM64")],
)
def test_init_rejects_unsupported_platform(
    monkeypatch: pytest.MonkeyPatch, system: str, machine: str
):
    """Test MLX-Audio fails during construction on unsupported platforms."""
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mlx_audio.transcriber.platform.system",
        Mock(return_value=system),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mlx_audio.transcriber.platform.machine",
        Mock(return_value=machine),
    )

    with pytest.raises(TranscriptionError, match="requires macOS on Apple Silicon"):
        MlxAudioTranscriber(MIMO_MODEL)


def test_get_cache_path_separates_generation_options():
    """Test MLX-Audio cache paths differ by generation options."""
    audio = _get_cache_audio()
    first_transcriber = _get_mlx_audio_transcriber(model=MIMO_MODEL)
    second_transcriber = _get_mlx_audio_transcriber(
        model=replace(MIMO_MODEL, max_tokens=1024)
    )
    third_transcriber = _get_mlx_audio_transcriber(model=MIMO_MODEL)
    fourth_transcriber = _get_mlx_audio_transcriber(model=MIMO_MODEL)
    third_transcriber.chunk_duration_seconds = 30.0
    fourth_transcriber.chunk_duration_seconds = 30.0
    fourth_transcriber.chunk_overlap_seconds = 2.0

    first_cache_path = _get_cache_path(first_transcriber, audio)
    second_cache_path = _get_cache_path(second_transcriber, audio)
    third_cache_path = _get_cache_path(third_transcriber, audio)
    fourth_cache_path = _get_cache_path(fourth_transcriber, audio)

    assert (
        len({first_cache_path, second_cache_path, third_cache_path, fourth_cache_path})
        == 4
    )


def test_token_limit_guard_cache_identity_depends_on_audio_duration(tmp_path: Path):
    """Share short caches while isolating long guarded MiMo transcriptions."""
    short_audio = AudioSegment.silent(duration=55_000, frame_rate=1_000)
    long_audio = AudioSegment.silent(duration=55_001, frame_rate=1_000)
    unguarded = MlxAudioTranscriber(
        model=MIMO_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        cache_root_path=tmp_path,
    )
    guarded = MlxAudioTranscriber(
        model=MIMO_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        cache_root_path=tmp_path,
        token_limit_guard=True,
    )

    assert _get_cache_path(guarded, short_audio) == _get_cache_path(
        unguarded, short_audio
    )
    assert _get_cache_path(guarded, long_audio) != _get_cache_path(
        unguarded, long_audio
    )

    settings = TranscriptionPreprocessingSettings(False, False)
    expected_segments = [_get_timed_segment("cached")]
    unguarded._cache.save(
        short_audio,
        unguarded._get_cache_identity(short_audio, settings),
        expected_segments,
    )
    assert guarded.get_cached_transcription(short_audio) == expected_segments

    guarded_cache_identity = guarded._get_cache_identity(long_audio, settings)
    assert guarded_cache_identity["chunk_duration_seconds"] == 53.0
    assert guarded_cache_identity["chunk_overlap_seconds"] == 1.0
    assert guarded_cache_identity["chunk_postprocessing_version"] == "2"
    assert guarded_cache_identity["token_limit_guard_fraction"] == 0.95
    assert "token_limit_guard_fraction" not in (
        guarded._get_cache_identity(short_audio, settings)
    )


def test_token_limit_guard_does_not_change_qwen_behavior(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Leave Qwen cache identity and full-window inference unchanged."""
    audio = AudioSegment.silent(duration=120_000, frame_rate=1_000)
    unguarded = MlxAudioTranscriber(
        model=QWEN3_ASR_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        cache_root_path=tmp_path,
    )
    guarded = MlxAudioTranscriber(
        model=QWEN3_ASR_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        cache_root_path=tmp_path,
        token_limit_guard=True,
    )
    expected_segments = [_get_timed_segment("qwen")]
    patched_transcribe = Mock(return_value=expected_segments)
    monkeypatch.setattr(
        guarded, "_transcribe_audio_window_with_retry", patched_transcribe
    )

    assert _get_cache_path(guarded, audio) == _get_cache_path(unguarded, audio)
    assert guarded.transcribe(audio) == expected_segments
    patched_transcribe.assert_called_once_with(audio, False)


def test_get_cache_path_separates_audio_formats():
    """Test MLX-Audio cache paths include audio format identity."""
    raw_data = b"\0\1" * 100
    audio_segments = [
        AudioSegment(data=raw_data, sample_width=2, frame_rate=16000, channels=1),
        AudioSegment(data=raw_data, sample_width=2, frame_rate=8000, channels=1),
        AudioSegment(data=raw_data, sample_width=2, frame_rate=16000, channels=2),
        AudioSegment(data=raw_data, sample_width=1, frame_rate=16000, channels=1),
    ]
    transcriber = _get_mlx_audio_transcriber(model=MIMO_MODEL)

    cache_paths = {
        _get_cache_path(transcriber, audio_segment) for audio_segment in audio_segments
    }

    assert len(cache_paths) == len(audio_segments)


@pytest.mark.parametrize(
    ("model", "expected_max_tokens"),
    [
        (MIMO_MODEL, 256),
        (QWEN3_ASR_MODEL, 8192),
        (SENSEVOICE_MODEL, None),
        (FIRERED_ASR2_MODEL, None),
        (GLM_ASR_MODEL, 128),
    ],
    ids=["mimo", "qwen3-asr", "sensevoice", "firered-asr2", "glm-asr"],
)
def test_models_define_generation_limits(
    model: MlxAudioModelSpec, expected_max_tokens: int | None
):
    """Test each model defines its generation limit.

    Arguments:
        model: MLX-Audio model
        expected_max_tokens: model generation limit
    """
    assert model.max_tokens == expected_max_tokens


def test_init_rejects_chunk_duration_that_rounds_to_zero():
    """Test chunk durations must advance by at least one millisecond."""
    with pytest.raises(ValueError, match="round to at least one millisecond"):
        MlxAudioTranscriber(MIMO_MODEL, chunk_duration_seconds=0.0004)


def test_get_cached_transcription_reads_mlx_audio_payload(tmp_path: Path):
    """Test MLX-Audio cache reads segment payloads from cache_identity-bearing files."""
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        cache_root_path=tmp_path,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
    )
    audio = _get_cache_audio()
    expected_segments = [_get_timed_segment("你好")]
    transcriber._cache.save(
        audio,
        transcriber._get_cache_identity(
            audio, TranscriptionPreprocessingSettings(False, False)
        ),
        expected_segments,
    )

    segments = transcriber.get_cached_transcription(audio)

    assert segments == expected_segments


def test_transcribe_recovers_from_malformed_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Test malformed cached output is replaced by a fresh transcription."""
    audio = _get_cache_audio()
    expected_segments = [_get_timed_segment("你好")]
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        cache_root_path=tmp_path,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
    )
    cache_path = _get_cache_path(transcriber, audio)
    cache_path.write_text("{", encoding="utf-8")
    patched_transcribe = Mock(return_value=expected_segments)
    monkeypatch.setattr(transcriber, "_transcribe_attempt", patched_transcribe)

    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    patched_transcribe.assert_called_once_with(
        audio, TranscriptionPreprocessingSettings(False, False)
    )
    assert (
        json.loads(cache_path.read_text(encoding="utf-8"))["segments"][0]["text"]
        == "你好"
    )


def test_malformed_cache_does_not_override_fresh_rejection(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Test a stale cache-read error does not replace fresh rejection behavior.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = _get_cache_audio()
    fresh_segments = [_get_timed_segment("fresh")]
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        cache_root_path=tmp_path,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
    )
    cache_path = _get_cache_path(transcriber, audio)
    cache_path.write_text("{", encoding="utf-8")
    monkeypatch.setattr(
        transcriber, "_transcribe_attempt", Mock(return_value=fresh_segments)
    )

    segments = transcriber.transcribe(audio, is_usable=lambda _segments: False)

    assert segments == []
    assert (
        json.loads(cache_path.read_text(encoding="utf-8"))["segments"][0]["text"]
        == "fresh"
    )


def test_transcribe_uses_direct_mlx_audio_inference(monkeypatch: pytest.MonkeyPatch):
    """Test MLX-Audio transcription uses direct typed inference."""
    captured: dict[str, object] = {}
    audio = AudioSegment.silent(duration=1000)
    expected_segments = [_get_timed_segment("你好")]
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL, demucs_mode=DemucsMode.OFF, vad_mode=VadMode.OFF
    )
    transcriber.ctc_aligner = Mock(
        model_name="ctc/test-model", model_revision=None, return_value=expected_segments
    )

    def fake_recognizer_call(
        _recognizer: MlxAudioRecognizer, audio_path: Path
    ) -> MlxAudioResult:
        """Capture direct MLX-Audio arguments and return transcript text."""
        captured["audio_path"] = audio_path
        return SimpleNamespace(text="你好", generation_tokens=0)

    monkeypatch.setattr(MlxAudioRecognizer, "__call__", fake_recognizer_call)
    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    assert transcriber.model_name == MIMO_MODEL.name
    assert isinstance(captured["audio_path"], Path)


def test_transcribe_chunks_audio_assigns_and_clips_words(
    monkeypatch: pytest.MonkeyPatch,
):
    """Assign overlap words by midpoint and clip retained timings to chunk cores."""
    audio = AudioSegment.silent(duration=4500)
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        chunk_duration_seconds=2.0,
        chunk_overlap_seconds=0.5,
    )
    recognizer_call = Mock(
        side_effect=[
            SimpleNamespace(text="one", generation_tokens=0),
            SimpleNamespace(text="two", generation_tokens=0),
            SimpleNamespace(text="three", generation_tokens=0),
        ]
    )
    transcriber.ctc_aligner = Mock(
        model_name="ctc/test-model",
        model_revision=None,
        side_effect=[
            [_get_timed_segment("one", start=0.1, end=0.9)],
            [
                TranscribedSegment(
                    id=0,
                    seek=0,
                    start=0.1,
                    end=2.7,
                    text="overlaptwo",
                    words=[
                        TranscribedWord(
                            text="overlap", start=0.1, end=0.3, confidence=0.9
                        ),
                        TranscribedWord(text="two", start=0.4, end=2.7, confidence=0.9),
                    ],
                )
            ],
            [_get_timed_segment("three", start=0.6, end=1.0)],
        ],
    )
    monkeypatch.setattr(MlxAudioRecognizer, "__call__", recognizer_call)
    segments = transcriber.transcribe(audio)

    assert recognizer_call.call_count == 3
    assert transcriber.ctc_aligner.call_count == 3
    assert [segment.text for segment in segments] == ["one", "two", "three"]
    assert [segment.id for segment in segments] == [0, 1, 2]
    assert [segment.start for segment in segments] == pytest.approx([0.1, 2.0, 4.1])
    assert [segment.end for segment in segments] == pytest.approx([0.9, 4.0, 4.5])
    assert segments[1].words is not None
    assert segments[1].words[0].start == pytest.approx(2.0)
    assert segments[1].words[0].end == pytest.approx(4.0)


def test_token_limit_guard_proactively_chunks_long_mimo_audio(
    monkeypatch: pytest.MonkeyPatch,
):
    """Keep complete overlapping MiMo inference windows within the guard."""
    audio = AudioSegment.silent(duration=108_000, frame_rate=1_000)
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        token_limit_guard=True,
    )
    recognizer_call = Mock(
        side_effect=[
            SimpleNamespace(text="one duplicate", generation_tokens=3),
            SimpleNamespace(text="duplicate two", generation_tokens=3),
            SimpleNamespace(text="two three", generation_tokens=3),
        ]
    )
    transcriber.ctc_aligner = Mock(
        model_name="ctc/test-model",
        model_revision=None,
        side_effect=[
            [_get_timed_segment("one", start=0.1, end=52.9)],
            [_get_timed_segment("two", start=1.1, end=53.9)],
            [_get_timed_segment("three", start=1.1, end=2.9)],
        ],
    )
    monkeypatch.setattr(MlxAudioRecognizer, "__call__", recognizer_call)

    segments = transcriber.transcribe(audio)

    assert recognizer_call.call_count == 3
    assert [len(call.args[0]) for call in transcriber.ctc_aligner.call_args_list] == [
        54_000,
        55_000,
        3_000,
    ]
    assert [segment.text for segment in segments] == ["one", "two", "three"]
    assert [segment.start for segment in segments] == pytest.approx([0.1, 53.1, 106.1])
    assert [segment.end for segment in segments] == pytest.approx([52.9, 105.9, 107.9])


def test_token_limit_guard_honors_shorter_explicit_chunks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Keep explicitly configured chunks shorter than the MiMo guard window."""
    audio = AudioSegment.silent(duration=61_000, frame_rate=1_000)
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        cache_root_path=tmp_path,
        chunk_duration_seconds=20.0,
        chunk_overlap_seconds=0.0,
        token_limit_guard=True,
    )
    patched_transcribe = Mock(
        side_effect=[
            [_get_timed_segment("one", end=20.0)],
            [_get_timed_segment("two", end=20.0)],
            [_get_timed_segment("three", end=20.0)],
            [_get_timed_segment("four", end=1.0)],
        ]
    )
    monkeypatch.setattr(
        transcriber, "_transcribe_audio_window_with_retry", patched_transcribe
    )

    segments = transcriber.transcribe(audio)

    assert [len(call.args[0]) for call in patched_transcribe.call_args_list] == [
        20_000,
        20_000,
        20_000,
        1_000,
    ]
    assert all(call.args[1] is True for call in patched_transcribe.call_args_list)
    assert [segment.text for segment in segments] == ["one", "two", "three", "four"]


def test_transcribe_splits_audio_after_generation_token_exhaustion(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test truncated MLX-Audio output is retried over smaller windows."""
    audio = AudioSegment.silent(duration=4000)
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        chunk_overlap_seconds=0.0,
    )
    recognizer_call = Mock(
        side_effect=[
            SimpleNamespace(text="truncated", generation_tokens=256),
            SimpleNamespace(text="one", generation_tokens=1),
            SimpleNamespace(text="two", generation_tokens=1),
        ]
    )
    transcriber.ctc_aligner = Mock(
        model_name="ctc/test-model",
        model_revision=None,
        side_effect=[
            [_get_timed_segment("one", end=2.0)],
            [_get_timed_segment("two", end=2.0)],
        ],
    )
    monkeypatch.setattr(MlxAudioRecognizer, "__call__", recognizer_call)
    segments = transcriber.transcribe(audio)

    assert recognizer_call.call_count == 3
    assert transcriber.ctc_aligner.call_count == 2
    assert [segment.text for segment in segments] == ["one", "two"]
    assert [segment.start for segment in segments] == pytest.approx([0.0, 2.0])
    assert [segment.end for segment in segments] == pytest.approx([2.0, 4.0])


def test_token_limit_guard_splits_audio_near_generation_limit(
    monkeypatch: pytest.MonkeyPatch,
):
    """Reserve MiMo generation headroom when guarded output approaches its limit."""
    audio = AudioSegment.silent(duration=4000)
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        chunk_overlap_seconds=0.0,
    )
    recognizer_call = Mock(
        side_effect=[
            SimpleNamespace(text="compressed", generation_tokens=244),
            SimpleNamespace(text="one", generation_tokens=1),
            SimpleNamespace(text="two", generation_tokens=1),
        ]
    )
    transcriber.ctc_aligner = Mock(
        model_name="ctc/test-model",
        model_revision=None,
        side_effect=[
            [_get_timed_segment("one", end=2.0)],
            [_get_timed_segment("two", end=2.0)],
        ],
    )
    monkeypatch.setattr(MlxAudioRecognizer, "__call__", recognizer_call)

    segments = transcriber._transcribe_audio_window_with_retry(
        audio, guard_token_limit=True
    )

    assert recognizer_call.call_count == 3
    assert transcriber.ctc_aligner.call_count == 2
    assert [segment.text for segment in segments] == ["one", "two"]


def test_transcribe_splits_audio_after_incomplete_ctc_alignment(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test incomplete CTC paths are retried over smaller audio windows."""
    audio = AudioSegment.silent(duration=4000)
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        chunk_overlap_seconds=0.0,
    )
    recognizer_call = Mock(
        side_effect=[
            SimpleNamespace(text="whole", generation_tokens=0),
            SimpleNamespace(text="one", generation_tokens=0),
            SimpleNamespace(text="two", generation_tokens=0),
        ]
    )
    transcriber.ctc_aligner = Mock(
        model_name="ctc/test-model",
        model_revision=None,
        side_effect=[
            TranscriptionAlignmentIncompleteError(
                "CTC alignment did not reach all tokens."
            ),
            [_get_timed_segment("one", end=2.0)],
            [_get_timed_segment("two", end=2.0)],
        ],
    )
    monkeypatch.setattr(MlxAudioRecognizer, "__call__", recognizer_call)

    segments = transcriber.transcribe(audio)

    assert recognizer_call.call_count == 3
    assert transcriber.ctc_aligner.call_count == 3
    assert [segment.text for segment in segments] == ["one", "two"]
    assert [segment.start for segment in segments] == pytest.approx([0.0, 2.0])
    assert [segment.end for segment in segments] == pytest.approx([2.0, 4.0])


def test_transcribe_does_not_split_audio_after_other_ctc_errors(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test non-length CTC failures propagate without recursive retries."""
    audio = AudioSegment.silent(duration=4000)
    transcriber = MlxAudioTranscriber(
        MIMO_MODEL, demucs_mode=DemucsMode.OFF, vad_mode=VadMode.OFF
    )
    recognizer_call = Mock(
        return_value=SimpleNamespace(text="whole", generation_tokens=0)
    )
    transcriber.ctc_aligner = Mock(
        model_name="ctc/test-model",
        model_revision=None,
        side_effect=TranscriptionAlignmentError("CTC backend unavailable."),
    )
    monkeypatch.setattr(MlxAudioRecognizer, "__call__", recognizer_call)

    with pytest.raises(TranscriptionAlignmentError, match="backend unavailable"):
        transcriber.transcribe(audio)

    recognizer_call.assert_called_once()
    transcriber.ctc_aligner.assert_called_once()


def test_transcribe_chunks_audio_skips_empty_windows(monkeypatch: pytest.MonkeyPatch):
    """Test an empty chunk does not discard speech from other chunks."""
    audio = AudioSegment.silent(duration=4500)
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        chunk_duration_seconds=2.0,
        chunk_overlap_seconds=0.5,
    )
    patched_transcribe = Mock(
        side_effect=[
            [_get_timed_segment("one", start=0.1, end=0.9)],
            TranscriptionEmptyError("MLX-Audio returned empty transcript."),
            [_get_timed_segment("three", start=0.6, end=1.0)],
        ]
    )
    monkeypatch.setattr(transcriber, "_transcribe_audio_window", patched_transcribe)

    segments = transcriber.transcribe(audio)

    assert patched_transcribe.call_count == 3
    assert [segment.text for segment in segments] == ["one", "three"]
    assert [segment.id for segment in segments] == [0, 1]
    assert [segment.start for segment in segments] == pytest.approx([0.1, 4.1])


def test_transcribe_chunks_audio_rejects_all_empty_windows(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test chunked transcription remains empty when every chunk is empty."""
    audio = AudioSegment.silent(duration=4500)
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        chunk_duration_seconds=2.0,
    )
    monkeypatch.setattr(
        transcriber,
        "_transcribe_audio_window",
        Mock(
            side_effect=TranscriptionEmptyError("MLX-Audio returned empty transcript.")
        ),
    )

    with pytest.raises(TranscriptionEmptyError, match="across audio chunks"):
        transcriber.transcribe(audio)


def test_transcribe_vad_uses_shared_detector_and_restores_original_timestamps(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Use shared VAD intervals, restore timings, and attach score summaries."""
    audio = AudioSegment.silent(duration=6000)
    trace = VoiceActivityTrace(
        np.full(60, 0.8, dtype=np.float32), start_ms=50, step_ms=100, duration_ms=6000
    )
    vad_detector = Mock(
        cache_identity={"implementation": "ten"},
        trace_cache_identity={"implementation": "ten"},
        threshold=0.5,
    )
    vad_detector.get_speech_intervals.return_value = [(1000, 2000), (4000, 5500)]
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.ON,
        cache_root_path=tmp_path,
        vad_detector=vad_detector,
    )
    get_trace = Mock(return_value=trace)
    monkeypatch.setattr(transcriber, "_get_voice_activity_trace", get_trace)
    patched_transcribe = Mock(
        return_value=[
            _get_timed_segment("one", start=0.1, end=0.9),
            _get_timed_segment("two", start=1.2, end=2.2),
        ]
    )
    monkeypatch.setattr(transcriber, "_transcribe_unfiltered_audio", patched_transcribe)

    segments = transcriber.transcribe(audio)

    get_trace.assert_called_once_with(audio)
    vad_detector.get_speech_intervals.assert_called_once_with(trace)
    speech_audio = patched_transcribe.call_args.args[0]
    assert len(speech_audio) == 2500
    assert [segment.text for segment in segments] == ["one", "two"]
    assert [segment.id for segment in segments] == [0, 1]
    assert [segment.start for segment in segments] == pytest.approx([1.1, 4.2])
    assert [segment.end for segment in segments] == pytest.approx([1.9, 5.2])
    assert segments[1].words is not None
    assert segments[1].words[0].start == pytest.approx(4.2)
    assert segments[1].words[0].end == pytest.approx(5.2)
    assert segments[1].words[0].voice_activity_score == pytest.approx(0.8)
    assert segments[1].words[0].voice_activity_peak == pytest.approx(0.8)
    assert segments[1].words[0].voice_activity_coverage == pytest.approx(1.0)


def test_transcribe_vad_rejects_audio_without_detected_speech(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Test VAD does not invoke MLX-Audio when no speech is detected."""
    trace = Mock()
    vad_detector = Mock(
        cache_identity={"implementation": "ten"},
        trace_cache_identity={"implementation": "ten"},
        threshold=0.5,
    )
    vad_detector.get_speech_intervals.return_value = []
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.ON,
        cache_root_path=tmp_path,
        vad_detector=vad_detector,
    )
    monkeypatch.setattr(
        transcriber, "_get_voice_activity_trace", Mock(return_value=trace)
    )
    patched_transcribe = Mock()
    monkeypatch.setattr(transcriber, "_transcribe_unfiltered_audio", patched_transcribe)

    with pytest.raises(TranscriptionEmptyError, match="VAD found no speech"):
        transcriber.transcribe(AudioSegment.silent(duration=1000))

    patched_transcribe.assert_not_called()


def test_transcribe_vad_auto_retries_unfiltered_audio(monkeypatch: pytest.MonkeyPatch):
    """Test automatic VAD retries unfiltered audio after VAD failure."""
    expected_segments = [_get_timed_segment("retry")]
    trace = Mock()
    vad_detector = Mock(
        cache_identity={"implementation": "ten"},
        trace_cache_identity={"implementation": "ten"},
        threshold=0.5,
    )
    vad_detector.get_speech_intervals.return_value = []
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.AUTO,
        vad_detector=vad_detector,
    )
    monkeypatch.setattr(
        transcriber, "_get_voice_activity_trace", Mock(return_value=trace)
    )
    patched_transcribe = Mock(return_value=expected_segments)
    monkeypatch.setattr(transcriber, "_transcribe_unfiltered_audio", patched_transcribe)
    audio = AudioSegment.silent(duration=1000)

    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    patched_transcribe.assert_called_once_with(audio, False)


def test_init_accepts_shared_vad_detector():
    """Configure MLX-Audio with the same reusable detector as other backends."""
    detector = VoiceActivityDetector(VadImplementation.PYANNOTE)
    transcriber = MlxAudioTranscriber(MIMO_MODEL, vad_detector=detector)

    assert transcriber.vad_detector is detector


def test_transcribe_aligns_text_and_writes_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Test transcription text is aligned, returned, and cached."""
    audio = AudioSegment.silent(duration=1000)
    expected_segments = [_get_timed_segment("你好")]
    transcriber = MlxAudioTranscriber(
        model=MIMO_MODEL,
        cache_root_path=tmp_path,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
    )
    monkeypatch.setattr(
        MlxAudioRecognizer,
        "__call__",
        lambda _recognizer, _audio_path: SimpleNamespace(
            text="你好", generation_tokens=0
        ),
    )
    transcriber.ctc_aligner = Mock(
        model_name="ctc/test-model", model_revision=None, return_value=expected_segments
    )

    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    transcriber.ctc_aligner.assert_called_once_with(audio, "你好")
    cache_path = _get_cache_path(transcriber, audio)
    cache_payload = json.loads(cache_path.read_text(encoding="utf-8"))
    assert cache_payload["cache_version"] == 2
    assert cache_payload["cache_identity"]["backend"] == "mlx-audio"
    assert cache_payload["cache_identity"]["model_type"] == "mimo"
    assert cache_payload["cache_identity"]["model_name"] == MIMO_MODEL.name
    assert cache_payload["segments"][0]["text"] == "你好"


def test_transcribe_rejects_low_information_vocalizations(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test isolated vocalizations do not become accepted transcription output.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    transcriber = MlxAudioTranscriber(
        MIMO_MODEL, demucs_mode=DemucsMode.OFF, vad_mode=VadMode.OFF
    )
    monkeypatch.setattr(
        MlxAudioRecognizer,
        "__call__",
        Mock(return_value=SimpleNamespace(text="啊！啊！", generation_tokens=0)),
    )
    transcriber.ctc_aligner = Mock(model_name="ctc/test-model", model_revision=None)

    with pytest.raises(TranscriptionEmptyError, match="low-information"):
        transcriber.transcribe(AudioSegment.silent(duration=1000))

    transcriber.ctc_aligner.assert_not_called()


def test_transcribe_wraps_mlx_audio_inference_errors(monkeypatch: pytest.MonkeyPatch):
    """Test MLX-Audio import/runtime errors are exposed as inference errors."""
    audio = AudioSegment.silent(duration=1000)
    transcriber = MlxAudioTranscriber(
        MIMO_MODEL, demucs_mode=DemucsMode.OFF, vad_mode=VadMode.OFF
    )
    monkeypatch.setattr(
        MlxAudioRecognizer,
        "__call__",
        Mock(side_effect=ImportError("missing mlx_audio")),
    )

    with pytest.raises(
        TranscriptionRecognitionError, match="Unable to run MLX-Audio inference"
    ):
        transcriber.transcribe(audio)


def _get_mlx_audio_transcriber(
    *, model: MlxAudioModelSpec, cache_root_path: Path | None = None
) -> MlxAudioTranscriber:
    """Get an MLX-Audio transcriber with preprocessing disabled.

    Arguments:
        cache_root_path: root directory beneath which to cache
        model: MLX-Audio model
    Returns:
        initialized transcriber
    """
    return MlxAudioTranscriber(
        model=model,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.OFF,
        cache_root_path=cache_root_path,
    )


def _get_cache_audio() -> AudioSegment:
    """Get a small audio segment suitable for MLX-Audio cache tests.

    Returns:
        audio segment with concrete format cache_identity
    """
    return AudioSegment(
        data=b"\0\1" * 100, sample_width=2, frame_rate=16000, channels=1
    )


def _get_timed_segment(
    text: str, *, start: float = 0.0, end: float = 1.0
) -> TranscribedSegment:
    """Get a segment with word timing data.

    Arguments:
        text: segment text
        start: start time in seconds
        end: end time in seconds
    Returns:
        segment with one timed word
    """
    return TranscribedSegment(
        id=0,
        seek=0,
        start=start,
        end=end,
        text=text,
        words=[TranscribedWord(text=text, start=start, end=end, confidence=0.9)],
    )
