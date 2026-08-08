#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the MLX-Audio speech-to-text backend."""

from __future__ import annotations

import builtins
import json
import wave
from collections.abc import Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from scinoephile.audio.transcription.exceptions import TranscriptionError
from scinoephile.audio.transcription.mlx_audio import backend
from scinoephile.audio.transcription.mlx_audio.backend import (
    FIRERED_ASR2_MODEL,
    GLM_ASR_MODEL,
    MIMO_MODEL,
    QWEN3_ASR_MODEL,
    SENSEVOICE_MODEL,
    MlxAudioBackend,
    MlxAudioInferenceResult,
    MlxAudioModelProfile,
)
from scinoephile.core import Language
from scinoephile.core.dependencies import transcription as transcription_dependencies


@pytest.mark.parametrize(
    ("model_profile", "expected_languages"),
    [
        pytest.param(
            MIMO_MODEL,
            {
                Language.eng: "en",
                Language.yue_hans: "zh",
                Language.yue_hant: "zh",
                Language.zho_hans: "zh",
                Language.zho_hant: "zh",
            },
            id="mimo",
        ),
        pytest.param(
            QWEN3_ASR_MODEL,
            {
                Language.eng: "English",
                Language.yue_hans: "Cantonese",
                Language.yue_hant: "Cantonese",
                Language.zho_hans: "Chinese",
                Language.zho_hant: "Chinese",
            },
            id="qwen3-asr",
        ),
        pytest.param(
            SENSEVOICE_MODEL,
            {
                Language.eng: "en",
                Language.yue_hans: "yue",
                Language.yue_hant: "yue",
                Language.zho_hans: "zh",
                Language.zho_hant: "zh",
            },
            id="sensevoice",
        ),
        pytest.param(FIRERED_ASR2_MODEL, dict.fromkeys(Language), id="firered-asr2"),
        pytest.param(GLM_ASR_MODEL, dict.fromkeys(Language), id="glm-asr"),
    ],
)
def test_init_derives_mlx_audio_languages(
    model_profile: MlxAudioModelProfile,
    expected_languages: Mapping[Language, str | None],
):
    """Test each model family derives its language identifier."""
    languages = {
        language: MlxAudioBackend(
            model_name=model_profile, language=language
        ).mlx_audio_language
        for language in Language
    }

    assert languages == expected_languages


def test_init_matches_model_name_case_insensitively():
    """Test supported model profiles match model names case-insensitively."""
    mlx_audio_backend = MlxAudioBackend("custom/QWEN3-ASR-0.6B-8bit")

    assert mlx_audio_backend.model_profile.family_name == "qwen3-asr"


@pytest.mark.parametrize(
    ("metadata", "expected_family"),
    [
        ({"architectures": ["MiMoV2ASRForCausalLM"]}, "mimo"),
        ({"model_type": "qwen3_asr"}, "qwen3-asr"),
        ({"model_type": "sensevoice"}, "sensevoice"),
        ({"model_type": "fireredasr2"}, "firered-asr2"),
        ({"model_type": "glm"}, "glm-asr"),
    ],
    ids=["mimo", "qwen3-asr", "sensevoice", "firered-asr2", "glm-asr"],
)
def test_init_reads_local_model_metadata(
    tmp_path: Path, metadata: dict[str, object], expected_family: str
):
    """Test arbitrary local directories are identified from model metadata."""
    model_path = tmp_path / "asr"
    model_path.mkdir()
    (model_path / "config.json").write_text(json.dumps(metadata), encoding="utf-8")

    mlx_audio_backend = MlxAudioBackend(str(model_path))

    assert mlx_audio_backend.model_profile.family_name == expected_family


def test_init_prefers_exact_metadata_over_parent_path_marker(tmp_path: Path):
    """Test exact metadata wins over unrelated markers in parent paths.

    Arguments:
        tmp_path: temporary directory path
    """
    model_path = tmp_path / "firered-asr2-evaluation" / "asr"
    model_path.mkdir(parents=True)
    (model_path / "config.json").write_text(
        json.dumps({"model_type": "sensevoice"}), encoding="utf-8"
    )

    mlx_audio_backend = MlxAudioBackend(str(model_path))

    assert mlx_audio_backend.model_profile.family_name == "sensevoice"


def test_init_rejects_untested_family():
    """Test unknown MLX-Audio model families fail clearly."""
    with pytest.raises(
        TranscriptionError,
        match=(
            "supported families: firered-asr2, glm-asr, mimo, qwen3-asr, sensevoice"
        ),
    ):
        MlxAudioBackend("mlx-community/Whisper-Large-v3-MLX")


@pytest.mark.parametrize(
    ("model_result", "language", "max_tokens", "expected_result", "expected_kwargs"),
    [
        (
            {"text": "你好", "generation_tokens": 7},
            Language.yue_hant,
            128,
            MlxAudioInferenceResult(text="你好", generation_tokens=7),
            {"language": "zh", "max_tokens": 128},
        ),
        (
            SimpleNamespace(text="hello"),
            Language.eng,
            None,
            MlxAudioInferenceResult(text="hello"),
            {"language": "en"},
        ),
    ],
    ids=["mapping", "attributes"],
)
def test_transcribe_normalizes_results(
    tmp_path: Path,
    model_result: object,
    language: Language,
    max_tokens: int | None,
    expected_result: MlxAudioInferenceResult,
    expected_kwargs: dict[str, object],
):
    """Test mapping- and attribute-based results are normalized.

    Arguments:
        tmp_path: temporary directory path
        model_result: result returned by the MLX-Audio model
        language: language to transcribe
        max_tokens: optional generation limit
        expected_result: normalized inference result
        expected_kwargs: expected model generation arguments
    """
    audio_path = _write_wav(tmp_path / "audio.wav")
    model = Mock()
    model.generate.return_value = model_result
    mlx_audio_backend = MlxAudioBackend(language=language)
    mlx_audio_backend._model = model

    result = mlx_audio_backend.transcribe(audio_path, max_tokens)

    assert result == expected_result
    model.generate.assert_called_once_with(str(audio_path), **expected_kwargs)


@pytest.mark.parametrize(
    ("model_name", "max_tokens", "expected_kwargs"),
    [
        (SENSEVOICE_MODEL, None, {"language": "yue"}),
        (FIRERED_ASR2_MODEL, 128, {"max_len": 128}),
        (GLM_ASR_MODEL, 128, {"max_tokens": 128}),
    ],
    ids=["sensevoice", "firered-asr2", "glm-asr"],
)
def test_transcribe_adapts_model_specific_generation_arguments(
    tmp_path: Path,
    model_name: MlxAudioModelProfile,
    max_tokens: int | None,
    expected_kwargs: dict[str, object],
):
    """Test new model families receive only generation arguments they support.

    Arguments:
        tmp_path: temporary directory path
        model_name: MLX-Audio model name
        max_tokens: normalized generation limit
        expected_kwargs: model-specific generation arguments
    """
    audio_path = _write_wav(tmp_path / "audio.wav", duration_seconds=0.25)
    model = Mock()
    model.generate.return_value = SimpleNamespace(text="你好")
    mlx_audio_backend = MlxAudioBackend(model_name=model_name)
    mlx_audio_backend._model = model

    result = mlx_audio_backend.transcribe(audio_path, max_tokens)

    assert result.text == "你好"
    model.generate.assert_called_once_with(str(audio_path), **expected_kwargs)


@pytest.mark.parametrize(
    ("model_profile", "max_tokens", "expected_message"),
    [
        (MIMO_MODEL, 0, "max tokens must be positive"),
        (SENSEVOICE_MODEL, 128, "sensevoice does not support"),
    ],
    ids=["non-positive", "unsupported"],
)
def test_transcribe_rejects_invalid_generation_limit(
    tmp_path: Path,
    model_profile: MlxAudioModelProfile,
    max_tokens: int,
    expected_message: str,
):
    """Test the direct backend rejects invalid generation limits.

    Arguments:
        tmp_path: temporary directory path
        model_profile: MLX-Audio model profile
        max_tokens: invalid generation limit
        expected_message: expected validation error text
    """
    audio_path = _write_wav(tmp_path / "audio.wav")
    mlx_audio_backend = MlxAudioBackend(model_profile)

    with pytest.raises(ValueError, match=expected_message):
        mlx_audio_backend.transcribe(audio_path, max_tokens)


@pytest.mark.parametrize(
    ("model_result", "expected_message"),
    [
        ({}, "missing transcript text"),
        ({"text": "你好", "generation_tokens": True}, "invalid generation token"),
        ({"text": "你好", "generation_tokens": -1}, "invalid generation token"),
        ({"text": "你好", "generation_tokens": 1.5}, "invalid generation token"),
        ({"text": "你好", "generation_tokens": "1"}, "invalid generation token"),
    ],
    ids=[
        "missing-text",
        "tokens-bool",
        "tokens-negative",
        "tokens-float",
        "tokens-str",
    ],
)
def test_transcribe_rejects_malformed_result(
    tmp_path: Path, model_result: object, expected_message: str
):
    """Test malformed MLX-Audio results are rejected.

    Arguments:
        tmp_path: temporary directory path
        model_result: malformed result returned by the MLX-Audio model
        expected_message: expected validation error text
    """
    audio_path = _write_wav(tmp_path / "audio.wav")
    model = Mock()
    model.generate.return_value = model_result
    mlx_audio_backend = MlxAudioBackend()
    mlx_audio_backend._model = model

    with pytest.raises(ValueError, match=expected_message):
        mlx_audio_backend.transcribe(audio_path)


@pytest.mark.parametrize(
    ("model_profile", "mlx_audio_model_type"),
    [
        (MIMO_MODEL, "mimo"),
        (QWEN3_ASR_MODEL, "qwen3_asr"),
        (SENSEVOICE_MODEL, "sensevoice"),
        (FIRERED_ASR2_MODEL, "fireredasr2"),
        (GLM_ASR_MODEL, "glm"),
    ],
    ids=["mimo", "qwen3-asr", "sensevoice", "firered-asr2", "glm-asr"],
)
def test_model_is_shared_by_profile_key(
    monkeypatch: pytest.MonkeyPatch,
    model_profile: MlxAudioModelProfile,
    mlx_audio_model_type: str,
):
    """Test each profile loads its model type once per cache key.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        model_profile: MLX-Audio model profile
        mlx_audio_model_type: expected MLX-Audio loader model type
    """
    load = Mock(return_value=object())
    monkeypatch.setattr(MlxAudioBackend, "_models_by_key", {})
    monkeypatch.setattr(backend, "import_mlx_audio_stt_load", Mock(return_value=load))

    first = MlxAudioBackend(model_profile)
    second = MlxAudioBackend(model_profile)

    assert first._loaded_model is load.return_value
    assert second._loaded_model is load.return_value
    load.assert_called_once_with(
        model_profile.model_name, model_type=mlx_audio_model_type
    )


def test_model_cache_key_includes_mlx_audio_model_type(monkeypatch: pytest.MonkeyPatch):
    """Test loader types distinguish models with the same reference.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    models = [object(), object()]
    load = Mock(side_effect=models)
    monkeypatch.setattr(MlxAudioBackend, "_models_by_key", {})
    monkeypatch.setattr(backend, "import_mlx_audio_stt_load", Mock(return_value=load))
    alternate_profile = replace(MIMO_MODEL, mlx_audio_model_type="qwen3_asr")

    first = MlxAudioBackend(MIMO_MODEL)
    second = MlxAudioBackend(alternate_profile)

    assert first._loaded_model is models[0]
    assert second._loaded_model is models[1]
    assert load.call_args_list == [
        call(MIMO_MODEL.model_name, model_type="mimo"),
        call(MIMO_MODEL.model_name, model_type="qwen3_asr"),
    ]


def test_model_validates_local_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Test local model paths are resolved before loading.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary directory path
    """
    model_path = tmp_path / "model"
    model_path.mkdir()
    (model_path / "config.json").write_text(
        json.dumps({"architectures": ["MiMoV2ASRForCausalLM"]}), encoding="utf-8"
    )
    load = Mock(return_value=object())
    monkeypatch.setattr(MlxAudioBackend, "_models_by_key", {})
    monkeypatch.setattr(backend, "import_mlx_audio_stt_load", Mock(return_value=load))

    mlx_audio_backend = MlxAudioBackend(str(model_path))

    assert mlx_audio_backend._loaded_model is load.return_value
    load.assert_called_once_with(model_path.resolve(), model_type="mimo")


def test_mlx_audio_import_error_is_actionable(monkeypatch: pytest.MonkeyPatch):
    """Test missing MLX-Audio reports the optional extra.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    original_import = builtins.__import__

    def import_without_mlx_audio(
        name: str,
        globals: Mapping[str, object] | None = None,
        locals: Mapping[str, object] | None = None,
        fromlist: Sequence[str] | None = (),
        level: int = 0,
    ) -> object:
        """Reject MLX-Audio while delegating all other imports."""
        if name == "mlx_audio.stt":
            raise ImportError("blocked optional dependency")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_without_mlx_audio)

    with pytest.raises(ImportError, match="'transcription' extra"):
        transcription_dependencies.import_mlx_audio_stt_load()


def _write_wav(path: Path, *, duration_seconds: float = 0.1) -> Path:
    """Write a silent mono WAV file.

    Arguments:
        path: output WAV path
        duration_seconds: output duration in seconds
    Returns:
        output WAV path
    """
    frame_rate = 16000
    with wave.open(str(path), "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(frame_rate)
        file.writeframes(b"\0\0" * round(frame_rate * duration_seconds))
    return path
