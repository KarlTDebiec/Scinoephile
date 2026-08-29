#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of MlxAudioTranscriber."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
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
    TranscriptionPreprocessingSettings,
    TranscriptionRecognitionError,
    VadMode,
)
from scinoephile.audio.transcription.mlx_audio.model import (
    MlxAudioModel,
    MlxAudioResult,
)
from scinoephile.audio.transcription.mlx_audio.model_spec import (
    FIRERED_ASR2_MODEL,
    GLM_ASR_MODEL,
    MIMO_MODEL,
    QWEN3_ASR_MODEL,
    SENSEVOICE_MODEL,
    MlxAudioModelSpec,
)
from scinoephile.audio.transcription.mlx_audio.transcriber import MlxAudioTranscriber
from scinoephile.audio.vad import (
    VadImplementation,
    VoiceActivityDetector,
    VoiceActivityTrace,
)
from scinoephile.core import Language
from scinoephile.core.ml import ModelSpec

_CTC_MODEL = ModelSpec(name="ctc/test-model", revision="ctc-revision")
"""CTC model specification used by transcriber tests."""

_CTC_CACHE_CONFIG_IDENTITY = {
    "alignment_version": 1,
    "device": "cpu",
    "language": Language.yue_hant.code,
    "model_name": _CTC_MODEL.name,
    "model_revision": _CTC_MODEL.revision,
    "runtime": {},
    "script_conversion": None,
}
"""Serializable CTC cache configuration used by aligner mocks."""


def _get_cache_path(
    transcriber: MlxAudioTranscriber,
    audio: AudioSegment,
    use_demucs: bool = False,
    use_vad: bool = False,
) -> Path:
    """Get the cache path for one preprocessing configuration.

    Arguments:
        transcriber: MLX-Audio transcriber
        audio: audio whose cache path is requested
        use_demucs: whether Demucs preprocessing is enabled
        use_vad: whether VAD preprocessing is enabled
    Returns:
        cache path for the configuration
    """
    settings = TranscriptionPreprocessingSettings(use_demucs, use_vad)
    cache_path = transcriber._cache.get_path(
        audio, transcriber._get_cache_identity(audio, settings)
    )
    assert cache_path is not None
    return cache_path


def test_init_accepts_configured_components_and_defaults_preprocessing_to_off():
    """Test MLX-Audio retains configured components with preprocessing off."""
    model = MlxAudioModel(MIMO_MODEL, Language.yue_hant)
    ctc_aligner = CtcAligner(Language.yue_hant, _CTC_MODEL)
    transcriber = MlxAudioTranscriber(model, ctc_aligner, Language.yue_hant)

    assert transcriber.model is model
    assert transcriber.ctc_aligner is ctc_aligner
    assert transcriber.demucs_mode is DemucsMode.OFF
    assert transcriber.vad_mode is VadMode.OFF
    assert transcriber.demucs_separator is None
    assert transcriber.model.spec is MIMO_MODEL
    assert transcriber.language is Language.yue_hant
    assert not hasattr(model, "language")
    assert model.generate_kw == {"language": "zh", "max_tokens": 256}


def test_init_rejects_ctc_aligner_language_mismatch():
    """Test the transcriber and CTC aligner languages must match."""
    model = MlxAudioModel(MIMO_MODEL, Language.yue_hant)
    ctc_aligner = CtcAligner(Language.zho_hant)

    with pytest.raises(ValueError, match="languages must match"):
        MlxAudioTranscriber(model, ctc_aligner, Language.yue_hant)


def test_init_rejects_model_language_mismatch():
    """Test the executable model and transcriber languages must match."""
    model = MlxAudioModel(MIMO_MODEL, Language.eng)
    ctc_aligner = CtcAligner(Language.yue_hant, _CTC_MODEL)

    with pytest.raises(ValueError, match="model and transcriber languages must match"):
        MlxAudioTranscriber(model, ctc_aligner, Language.yue_hant)


def test_get_cache_path_separates_model_configuration(runtime_cache_root_path: Path):
    """Test MLX-Audio cache paths differ by model configuration.

    Arguments:
        runtime_cache_root_path: isolated default runtime cache root
    """
    audio = _get_cache_audio()
    first_transcriber = _get_mlx_audio_transcriber(
        model_spec=replace(
            MIMO_MODEL, name="custom/MiMo-V2.5-ASR-one", revision="revision-one"
        )
    )
    second_transcriber = _get_mlx_audio_transcriber(
        model_spec=replace(
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
    first_transcriber = _get_mlx_audio_transcriber(model_spec=MIMO_MODEL)
    second_transcriber = _get_mlx_audio_transcriber(model_spec=MIMO_MODEL)
    first_transcriber.ctc_aligner = CtcAligner(
        Language.yue_hant, ModelSpec(name="ctc/one", revision="revision-one"), "cpu"
    )
    second_transcriber.ctc_aligner = CtcAligner(
        Language.yue_hant, ModelSpec(name="ctc/two", revision="revision-two"), "cpu"
    )

    first_cache_path = _get_cache_path(first_transcriber, audio)
    second_cache_path = _get_cache_path(second_transcriber, audio)

    assert first_cache_path != second_cache_path
    settings = TranscriptionPreprocessingSettings(False, False)
    first_identity = first_transcriber._get_cache_identity(audio, settings)
    assert (
        first_identity["aligner"] == first_transcriber.ctc_aligner.cache_config_identity
    )


def test_get_cache_path_separates_model_revisions():
    """Test remote model revisions contribute to MLX-Audio cache identity."""
    audio = _get_cache_audio()
    first_transcriber = _get_mlx_audio_transcriber(
        model_spec=replace(MIMO_MODEL, revision="revision-one")
    )
    second_transcriber = _get_mlx_audio_transcriber(
        model_spec=replace(MIMO_MODEL, revision="revision-two")
    )

    assert _get_cache_path(first_transcriber, audio) != _get_cache_path(
        second_transcriber, audio
    )


def test_get_cache_path_separates_model_languages():
    """Test model-specific language values contribute to cache identity."""
    audio = _get_cache_audio()
    first_languages = {**MIMO_MODEL.languages, Language.yue_hant: "zh"}
    second_languages = {**MIMO_MODEL.languages, Language.yue_hant: "yue"}
    first_transcriber = _get_mlx_audio_transcriber(
        model_spec=replace(MIMO_MODEL, languages=first_languages)
    )
    second_transcriber = _get_mlx_audio_transcriber(
        model_spec=replace(MIMO_MODEL, languages=second_languages)
    )

    assert _get_cache_path(first_transcriber, audio) != _get_cache_path(
        second_transcriber, audio
    )


def test_get_cache_path_uses_installed_mlx_runtime(monkeypatch: pytest.MonkeyPatch):
    """Test the cache identity includes installed MLX-Audio provenance.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    runtime_identity = {
        "distribution": "mlx-audio",
        "version": "test-version",
        "source_revision": "test-revision",
    }
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mlx_audio.transcriber."
        "get_distribution_identity",
        lambda _distribution_name: runtime_identity,
    )
    transcriber = _get_mlx_audio_transcriber(model_spec=MIMO_MODEL)

    cache_identity = transcriber._get_cache_identity(
        _get_cache_audio(), TranscriptionPreprocessingSettings(False, False)
    )

    assert cache_identity["runtime"] == runtime_identity


def test_get_cache_path_separates_generation_options():
    """Test MLX-Audio cache paths differ by generation options."""
    audio = _get_cache_audio()
    first_transcriber = _get_mlx_audio_transcriber(model_spec=MIMO_MODEL)
    second_transcriber = _get_mlx_audio_transcriber(
        model_spec=replace(MIMO_MODEL, max_tokens=1024)
    )
    third_transcriber = _get_mlx_audio_transcriber(model_spec=MIMO_MODEL)
    fourth_transcriber = _get_mlx_audio_transcriber(model_spec=MIMO_MODEL)
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


def test_safe_audio_duration_changes_long_audio_cache_identity(tmp_path: Path):
    """Include automatic model-safe chunking only for overlong audio.

    Arguments:
        tmp_path: temporary cache directory path
    """
    short_audio = AudioSegment.silent(duration=55_000, frame_rate=1_000)
    long_audio = AudioSegment.silent(duration=55_001, frame_rate=1_000)
    transcriber = _get_mlx_audio_transcriber(
        model_spec=MIMO_MODEL, cache_root_path=tmp_path
    )

    settings = TranscriptionPreprocessingSettings(False, False)
    short_identity = transcriber._get_cache_identity(short_audio, settings)
    long_identity = transcriber._get_cache_identity(long_audio, settings)

    assert short_identity["chunk_duration_seconds"] is None
    assert short_identity["chunk_overlap_seconds"] is None
    assert short_identity["chunk_postprocessing_version"] is None
    assert long_identity["chunk_duration_seconds"] == 53.0
    assert long_identity["chunk_overlap_seconds"] == 1.0
    assert long_identity["chunk_postprocessing_version"] == "2"
    assert _get_cache_path(transcriber, short_audio) != _get_cache_path(
        transcriber, long_audio
    )


def test_model_without_safe_duration_uses_one_audio_window(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Leave unrestricted model cache identity and inference unchunked.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment.silent(duration=120_000, frame_rate=1_000)
    transcriber = _get_mlx_audio_transcriber(
        model_spec=QWEN3_ASR_MODEL, cache_root_path=tmp_path
    )
    expected_segments = [_get_timed_segment("qwen")]
    patched_transcribe = Mock(return_value=expected_segments)
    monkeypatch.setattr(transcriber, "_transcribe_window", patched_transcribe)

    cache_identity = transcriber._get_cache_identity(
        audio, TranscriptionPreprocessingSettings(False, False)
    )
    assert cache_identity["chunk_duration_seconds"] is None
    assert cache_identity["chunk_overlap_seconds"] is None
    assert cache_identity["chunk_postprocessing_version"] is None
    assert transcriber.transcribe(audio) == expected_segments
    patched_transcribe.assert_called_once_with(audio)


def test_get_cache_path_separates_audio_formats():
    """Test MLX-Audio cache paths include audio format identity."""
    raw_data = b"\0\1" * 100
    audio_segments = [
        AudioSegment(data=raw_data, sample_width=2, frame_rate=16000, channels=1),
        AudioSegment(data=raw_data, sample_width=2, frame_rate=8000, channels=1),
        AudioSegment(data=raw_data, sample_width=2, frame_rate=16000, channels=2),
        AudioSegment(data=raw_data, sample_width=1, frame_rate=16000, channels=1),
    ]
    transcriber = _get_mlx_audio_transcriber(model_spec=MIMO_MODEL)

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
        _get_mlx_audio_transcriber(chunk_duration_seconds=0.0004)


def test_get_cached_transcription_reads_mlx_audio_payload(tmp_path: Path):
    """Test MLX-Audio cache reads segment payloads from identity-bearing files.

    Arguments:
        tmp_path: temporary cache directory path
    """
    transcriber = _get_mlx_audio_transcriber(
        model_spec=MIMO_MODEL, cache_root_path=tmp_path
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
    """Test malformed cached output is replaced by a fresh transcription.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = _get_cache_audio()
    expected_segments = [_get_timed_segment("你好")]
    transcriber = _get_mlx_audio_transcriber(
        model_spec=MIMO_MODEL, cache_root_path=tmp_path
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
    transcriber = _get_mlx_audio_transcriber(
        model_spec=MIMO_MODEL, cache_root_path=tmp_path
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
    """Test MLX-Audio transcription uses direct typed inference.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    captured: dict[str, object] = {}
    audio = AudioSegment.silent(duration=1000)
    expected_segments = [_get_timed_segment("你好")]
    transcriber = _get_mlx_audio_transcriber()
    transcriber.ctc_aligner = Mock(
        cache_config_identity=_CTC_CACHE_CONFIG_IDENTITY,
        model=SimpleNamespace(spec=_CTC_MODEL),
        return_value=expected_segments,
    )

    def fake_model_call(_model: MlxAudioModel, audio_path: Path) -> MlxAudioResult:
        """Capture direct MLX-Audio arguments and return transcript text.

        Arguments:
            _model: ignored MLX-Audio model
            audio_path: audio file path passed to the model
        Returns:
            mocked MLX-Audio result
        """
        captured["audio_path"] = audio_path
        return SimpleNamespace(text="你好", generation_tokens=0)

    monkeypatch.setattr(MlxAudioModel, "__call__", fake_model_call)
    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    assert isinstance(captured["audio_path"], Path)


def test_transcribe_chunks_audio_assigns_and_clips_words(
    monkeypatch: pytest.MonkeyPatch,
):
    """Assign overlap words by midpoint and clip timings to chunk cores.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    audio = AudioSegment.silent(duration=4500)
    transcriber = _get_mlx_audio_transcriber(
        chunk_duration_seconds=2.0, chunk_overlap_seconds=0.5
    )
    model_call = Mock(
        side_effect=[
            SimpleNamespace(text="one", generation_tokens=0),
            SimpleNamespace(text="two", generation_tokens=0),
            SimpleNamespace(text="three", generation_tokens=0),
        ]
    )
    transcriber.ctc_aligner = Mock(
        cache_config_identity=_CTC_CACHE_CONFIG_IDENTITY,
        model=SimpleNamespace(spec=_CTC_MODEL),
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
    monkeypatch.setattr(MlxAudioModel, "__call__", model_call)
    segments = transcriber.transcribe(audio)

    assert model_call.call_count == 3
    assert transcriber.ctc_aligner.call_count == 3
    assert [segment.text for segment in segments] == ["one", "two", "three"]
    assert [segment.id for segment in segments] == [0, 1, 2]
    assert [segment.start for segment in segments] == pytest.approx([0.1, 2.0, 4.1])
    assert [segment.end for segment in segments] == pytest.approx([0.9, 4.0, 4.5])
    assert segments[1].words is not None
    assert segments[1].words[0].start == pytest.approx(2.0)
    assert segments[1].words[0].end == pytest.approx(4.0)


def test_long_mimo_audio_is_automatically_chunked(monkeypatch: pytest.MonkeyPatch):
    """Keep complete overlapping MiMo inference windows within its safe limit.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    audio = AudioSegment.silent(duration=108_000, frame_rate=1_000)
    transcriber = _get_mlx_audio_transcriber()
    model_call = Mock(
        side_effect=[
            SimpleNamespace(text="one duplicate", generation_tokens=3),
            SimpleNamespace(text="duplicate two", generation_tokens=3),
            SimpleNamespace(text="two three", generation_tokens=3),
        ]
    )
    transcriber.ctc_aligner = Mock(
        cache_config_identity=_CTC_CACHE_CONFIG_IDENTITY,
        model=SimpleNamespace(spec=_CTC_MODEL),
        side_effect=[
            [_get_timed_segment("one", start=0.1, end=52.9)],
            [_get_timed_segment("two", start=1.1, end=53.9)],
            [_get_timed_segment("three", start=1.1, end=2.9)],
        ],
    )
    monkeypatch.setattr(MlxAudioModel, "__call__", model_call)

    segments = transcriber.transcribe(audio)

    assert model_call.call_count == 3
    assert [len(call.args[0]) for call in transcriber.ctc_aligner.call_args_list] == [
        54_000,
        55_000,
        3_000,
    ]
    assert [segment.text for segment in segments] == ["one", "two", "three"]
    assert [segment.start for segment in segments] == pytest.approx([0.1, 53.1, 106.1])
    assert [segment.end for segment in segments] == pytest.approx([52.9, 105.9, 107.9])


def test_safe_duration_honors_shorter_explicit_chunks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Keep explicitly configured chunks shorter than the MiMo safe window.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment.silent(duration=61_000, frame_rate=1_000)
    transcriber = _get_mlx_audio_transcriber(
        cache_root_path=tmp_path, chunk_duration_seconds=20.0, chunk_overlap_seconds=0.0
    )
    patched_transcribe = Mock(
        side_effect=[
            [_get_timed_segment("one", end=20.0)],
            [_get_timed_segment("two", end=20.0)],
            [_get_timed_segment("three", end=20.0)],
            [_get_timed_segment("four", end=1.0)],
        ]
    )
    monkeypatch.setattr(transcriber, "_transcribe_window", patched_transcribe)

    segments = transcriber.transcribe(audio)

    assert [len(call.args[0]) for call in patched_transcribe.call_args_list] == [
        20_000,
        20_000,
        20_000,
        1_000,
    ]
    assert [segment.text for segment in segments] == ["one", "two", "three", "four"]


def test_transcribe_splits_audio_after_generation_token_exhaustion(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test truncated MLX-Audio output is retried over smaller windows.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    audio = AudioSegment.silent(duration=4000)
    transcriber = _get_mlx_audio_transcriber(chunk_overlap_seconds=0.0)
    model_call = Mock(
        side_effect=[
            SimpleNamespace(text="truncated", generation_tokens=256),
            SimpleNamespace(text="one", generation_tokens=1),
            SimpleNamespace(text="two", generation_tokens=1),
        ]
    )
    transcriber.ctc_aligner = Mock(
        cache_config_identity=_CTC_CACHE_CONFIG_IDENTITY,
        model=SimpleNamespace(spec=_CTC_MODEL),
        side_effect=[
            [_get_timed_segment("one", end=2.0)],
            [_get_timed_segment("two", end=2.0)],
        ],
    )
    monkeypatch.setattr(MlxAudioModel, "__call__", model_call)
    segments = transcriber.transcribe(audio)

    assert model_call.call_count == 3
    assert transcriber.ctc_aligner.call_count == 2
    assert [segment.text for segment in segments] == ["one", "two"]
    assert [segment.start for segment in segments] == pytest.approx([0.0, 2.0])
    assert [segment.end for segment in segments] == pytest.approx([2.0, 4.0])


def test_audio_near_generation_limit_is_not_split(monkeypatch: pytest.MonkeyPatch):
    """Accept complete output that remains below the model token limit.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    audio = AudioSegment.silent(duration=4000)
    transcriber = _get_mlx_audio_transcriber(chunk_overlap_seconds=0.0)
    model_call = Mock(
        return_value=SimpleNamespace(text="compressed", generation_tokens=244)
    )
    transcriber.ctc_aligner = Mock(
        cache_config_identity=_CTC_CACHE_CONFIG_IDENTITY,
        model=SimpleNamespace(spec=_CTC_MODEL),
        return_value=[_get_timed_segment("compressed", end=4.0)],
    )
    monkeypatch.setattr(MlxAudioModel, "__call__", model_call)

    segments = transcriber.transcribe(audio)

    model_call.assert_called_once()
    transcriber.ctc_aligner.assert_called_once()
    assert [segment.text for segment in segments] == ["compressed"]


def test_transcribe_splits_audio_after_incomplete_ctc_alignment(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test incomplete CTC paths are retried over smaller audio windows.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    audio = AudioSegment.silent(duration=4000)
    transcriber = _get_mlx_audio_transcriber(chunk_overlap_seconds=0.0)
    model_call = Mock(
        side_effect=[
            SimpleNamespace(text="whole", generation_tokens=0),
            SimpleNamespace(text="one", generation_tokens=0),
            SimpleNamespace(text="two", generation_tokens=0),
        ]
    )
    transcriber.ctc_aligner = Mock(
        cache_config_identity=_CTC_CACHE_CONFIG_IDENTITY,
        model=SimpleNamespace(spec=_CTC_MODEL),
        side_effect=[
            TranscriptionAlignmentIncompleteError(
                "CTC alignment did not reach all tokens."
            ),
            [_get_timed_segment("one", end=2.0)],
            [_get_timed_segment("two", end=2.0)],
        ],
    )
    monkeypatch.setattr(MlxAudioModel, "__call__", model_call)

    segments = transcriber.transcribe(audio)

    assert model_call.call_count == 3
    assert transcriber.ctc_aligner.call_count == 3
    assert [segment.text for segment in segments] == ["one", "two"]
    assert [segment.start for segment in segments] == pytest.approx([0.0, 2.0])
    assert [segment.end for segment in segments] == pytest.approx([2.0, 4.0])


def test_transcribe_does_not_split_audio_after_other_ctc_errors(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test non-length CTC failures propagate without recursive retries.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    audio = AudioSegment.silent(duration=4000)
    transcriber = _get_mlx_audio_transcriber()
    model_call = Mock(return_value=SimpleNamespace(text="whole", generation_tokens=0))
    transcriber.ctc_aligner = Mock(
        cache_config_identity=_CTC_CACHE_CONFIG_IDENTITY,
        model=SimpleNamespace(spec=_CTC_MODEL),
        side_effect=TranscriptionAlignmentError("CTC backend unavailable."),
    )
    monkeypatch.setattr(MlxAudioModel, "__call__", model_call)

    with pytest.raises(TranscriptionAlignmentError, match="backend unavailable"):
        transcriber.transcribe(audio)

    model_call.assert_called_once()
    transcriber.ctc_aligner.assert_called_once()


def test_transcribe_chunks_audio_skips_empty_windows(monkeypatch: pytest.MonkeyPatch):
    """Test an empty chunk does not discard speech from other chunks.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    audio = AudioSegment.silent(duration=4500)
    transcriber = _get_mlx_audio_transcriber(
        chunk_duration_seconds=2.0, chunk_overlap_seconds=0.5
    )
    patched_transcribe = Mock(
        side_effect=[
            [_get_timed_segment("one", start=0.1, end=0.9)],
            TranscriptionEmptyError("MLX-Audio returned empty transcript."),
            [_get_timed_segment("three", start=0.6, end=1.0)],
        ]
    )
    monkeypatch.setattr(transcriber, "_transcribe_window", patched_transcribe)

    segments = transcriber.transcribe(audio)

    assert patched_transcribe.call_count == 3
    assert [segment.text for segment in segments] == ["one", "three"]
    assert [segment.id for segment in segments] == [0, 1]
    assert [segment.start for segment in segments] == pytest.approx([0.1, 4.1])


def test_transcribe_chunks_audio_rejects_all_empty_windows(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test chunked transcription remains empty when every chunk is empty.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    audio = AudioSegment.silent(duration=4500)
    transcriber = _get_mlx_audio_transcriber(chunk_duration_seconds=2.0)
    monkeypatch.setattr(
        transcriber,
        "_transcribe_window",
        Mock(
            side_effect=TranscriptionEmptyError("MLX-Audio returned empty transcript.")
        ),
    )

    with pytest.raises(TranscriptionEmptyError, match="across audio chunks"):
        transcriber.transcribe(audio)


def test_transcribe_vad_uses_shared_detector_and_restores_original_timestamps(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Use shared VAD intervals, restore timings, and attach score summaries.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
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
    transcriber = _get_mlx_audio_transcriber(
        vad_mode=VadMode.ON, cache_root_path=tmp_path, vad_detector=vad_detector
    )
    get_trace = Mock(return_value=trace)
    monkeypatch.setattr(transcriber, "_get_voice_activity_trace", get_trace)
    patched_transcribe = Mock(
        return_value=[
            _get_timed_segment("one", start=0.1, end=0.9),
            _get_timed_segment("two", start=1.2, end=2.2),
        ]
    )
    monkeypatch.setattr(transcriber, "_transcribe_window", patched_transcribe)

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
    """Test VAD does not invoke MLX-Audio when no speech is detected.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    trace = Mock()
    vad_detector = Mock(
        cache_identity={"implementation": "ten"},
        trace_cache_identity={"implementation": "ten"},
        threshold=0.5,
    )
    vad_detector.get_speech_intervals.return_value = []
    transcriber = _get_mlx_audio_transcriber(
        vad_mode=VadMode.ON, cache_root_path=tmp_path, vad_detector=vad_detector
    )
    monkeypatch.setattr(
        transcriber, "_get_voice_activity_trace", Mock(return_value=trace)
    )
    patched_transcribe = Mock()
    monkeypatch.setattr(transcriber, "_transcribe_window", patched_transcribe)

    with pytest.raises(TranscriptionEmptyError, match="VAD found no speech"):
        transcriber.transcribe(AudioSegment.silent(duration=1000))

    patched_transcribe.assert_not_called()


def test_transcribe_vad_auto_retries_unfiltered_audio(monkeypatch: pytest.MonkeyPatch):
    """Test automatic VAD retries unfiltered audio after VAD failure.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    expected_segments = [_get_timed_segment("retry")]
    trace = Mock()
    vad_detector = Mock(
        cache_identity={"implementation": "ten"},
        trace_cache_identity={"implementation": "ten"},
        threshold=0.5,
    )
    vad_detector.get_speech_intervals.return_value = []
    transcriber = _get_mlx_audio_transcriber(
        vad_mode=VadMode.AUTO, vad_detector=vad_detector
    )
    monkeypatch.setattr(
        transcriber, "_get_voice_activity_trace", Mock(return_value=trace)
    )
    patched_transcribe = Mock(return_value=expected_segments)
    monkeypatch.setattr(transcriber, "_transcribe_window", patched_transcribe)
    audio = AudioSegment.silent(duration=1000)

    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    patched_transcribe.assert_called_once_with(audio)


def test_init_accepts_shared_vad_detector():
    """Configure MLX-Audio with the same reusable detector as other backends."""
    detector = VoiceActivityDetector(VadImplementation.PYANNOTE)
    transcriber = _get_mlx_audio_transcriber(vad_detector=detector)

    assert transcriber.vad_detector is detector


def test_transcribe_aligns_text_and_writes_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Test transcription text is aligned, returned, and cached.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = AudioSegment.silent(duration=1000)
    expected_segments = [_get_timed_segment("你好")]
    transcriber = _get_mlx_audio_transcriber(
        model_spec=MIMO_MODEL, cache_root_path=tmp_path
    )
    monkeypatch.setattr(
        MlxAudioModel,
        "__call__",
        lambda _model, _audio_path: SimpleNamespace(text="你好", generation_tokens=0),
    )
    transcriber.ctc_aligner = Mock(
        cache_config_identity=_CTC_CACHE_CONFIG_IDENTITY,
        model=SimpleNamespace(spec=_CTC_MODEL),
        return_value=expected_segments,
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
    transcriber = _get_mlx_audio_transcriber()
    monkeypatch.setattr(
        MlxAudioModel,
        "__call__",
        Mock(return_value=SimpleNamespace(text="啊！啊！", generation_tokens=0)),
    )
    transcriber.ctc_aligner = Mock(
        cache_config_identity=_CTC_CACHE_CONFIG_IDENTITY,
        model=SimpleNamespace(spec=_CTC_MODEL),
    )

    with pytest.raises(TranscriptionEmptyError, match="low-information"):
        transcriber.transcribe(AudioSegment.silent(duration=1000))

    transcriber.ctc_aligner.assert_not_called()


def test_transcribe_wraps_mlx_audio_inference_errors(monkeypatch: pytest.MonkeyPatch):
    """Test MLX-Audio import/runtime errors are exposed as inference errors.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    audio = AudioSegment.silent(duration=1000)
    transcriber = _get_mlx_audio_transcriber()
    monkeypatch.setattr(
        MlxAudioModel, "__call__", Mock(side_effect=ImportError("missing mlx_audio"))
    )

    with pytest.raises(
        TranscriptionRecognitionError, match="Unable to run MLX-Audio inference"
    ):
        transcriber.transcribe(audio)


def _get_mlx_audio_transcriber(
    *,
    model_spec: MlxAudioModelSpec = MIMO_MODEL,
    cache_root_path: Path | None = None,
    chunk_duration_seconds: float | None = None,
    chunk_overlap_seconds: float = 1.0,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    vad_mode: VadMode = VadMode.OFF,
    vad_detector: VoiceActivityDetector | None = None,
) -> MlxAudioTranscriber:
    """Get an MLX-Audio transcriber with preprocessing disabled.

    Arguments:
        model_spec: MLX-Audio model specification
        cache_root_path: root directory beneath which to cache
        chunk_duration_seconds: optional chunk duration for inference
        chunk_overlap_seconds: context overlap applied to each chunk
        demucs_mode: Demucs preprocessing mode
        vad_mode: voice activity detection mode
        vad_detector: optional shared voice activity detector
    Returns:
        initialized transcriber
    """
    return MlxAudioTranscriber(
        model=MlxAudioModel(model_spec, Language.yue_hant),
        ctc_aligner=CtcAligner(
            Language.yue_hant, _CTC_MODEL, device="cpu", cache_root_path=cache_root_path
        ),
        language=Language.yue_hant,
        chunk_duration_seconds=chunk_duration_seconds,
        chunk_overlap_seconds=chunk_overlap_seconds,
        demucs_mode=demucs_mode,
        vad_mode=vad_mode,
        cache_root_path=cache_root_path,
        vad_detector=vad_detector,
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
