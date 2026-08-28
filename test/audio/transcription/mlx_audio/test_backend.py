#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the MLX-Audio speech-to-text backend."""

from __future__ import annotations

import builtins
import wave
from collections.abc import Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from scinoephile.audio.transcription.mlx_audio import backend
from scinoephile.audio.transcription.mlx_audio.backend import (
    MlxAudioBackend,
    MlxAudioInferenceResult,
)
from scinoephile.audio.transcription.mlx_audio.model import (
    FIRERED_ASR2_MODEL,
    GLM_ASR_MODEL,
    MIMO_MODEL,
    QWEN3_ASR_MODEL,
    SENSEVOICE_MODEL,
    MlxAudioModel,
)
from scinoephile.core import DependencyError, Language
from scinoephile.core.dependencies.transcription import import_mlx_audio_stt_load


@pytest.mark.parametrize(
    ("model", "expected_languages"),
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
    model: MlxAudioModel, expected_languages: Mapping[Language, str | None]
):
    """Test each model family derives its language identifier."""
    languages = {
        language: MlxAudioBackend(model=model, language=language).mlx_audio_language
        for language in Language
    }

    assert languages == expected_languages


@pytest.mark.parametrize(
    (
        "model",
        "model_result",
        "language",
        "max_tokens",
        "expected_result",
        "expected_kwargs",
    ),
    [
        (
            MIMO_MODEL,
            {"text": "你好", "generation_tokens": 7},
            Language.yue_hant,
            256,
            MlxAudioInferenceResult(text="你好", generation_tokens=7),
            {"language": "zh", "max_tokens": 256},
        ),
        (
            FIRERED_ASR2_MODEL,
            SimpleNamespace(text="hello"),
            Language.eng,
            None,
            MlxAudioInferenceResult(text="hello"),
            {},
        ),
    ],
    ids=["mapping", "attributes"],
)
def test_transcribe_normalizes_results(
    tmp_path: Path,
    model: MlxAudioModel,
    model_result: object,
    language: Language,
    max_tokens: int | None,
    expected_result: MlxAudioInferenceResult,
    expected_kwargs: dict[str, object],
):
    """Test mapping- and attribute-based results are normalized.

    Arguments:
        tmp_path: temporary directory path
        model: MLX-Audio model
        model_result: result returned by the MLX-Audio model
        language: language to transcribe
        max_tokens: optional generation limit
        expected_result: normalized inference result
        expected_kwargs: expected model generation arguments
    """
    audio_path = _write_wav(tmp_path / "audio.wav")
    loaded_model = Mock()
    loaded_model.generate.return_value = model_result
    mlx_audio_backend = MlxAudioBackend(model, language)
    mlx_audio_backend._loaded_model_instance = loaded_model

    result = mlx_audio_backend.transcribe(audio_path, max_tokens)

    assert result == expected_result
    loaded_model.generate.assert_called_once_with(str(audio_path), **expected_kwargs)


@pytest.mark.parametrize(
    ("model", "max_tokens", "expected_kwargs"),
    [
        (MIMO_MODEL, 128, {"language": "zh", "max_tokens": 128}),
        (SENSEVOICE_MODEL, None, {"language": "yue"}),
        (FIRERED_ASR2_MODEL, 128, {"max_len": 128}),
        (GLM_ASR_MODEL, 128, {"max_tokens": 128}),
    ],
    ids=["mimo", "sensevoice", "firered-asr2", "glm-asr"],
)
def test_transcribe_adapts_model_specific_generation_arguments(
    tmp_path: Path,
    model: MlxAudioModel,
    max_tokens: int | None,
    expected_kwargs: dict[str, object],
):
    """Test new model families receive only generation arguments they support.

    Arguments:
        tmp_path: temporary directory path
        model: MLX-Audio model
        max_tokens: normalized generation limit
        expected_kwargs: model-specific generation arguments
    """
    audio_path = _write_wav(tmp_path / "audio.wav", duration_seconds=0.25)
    loaded_model = Mock()
    loaded_model.generate.return_value = SimpleNamespace(text="你好")
    mlx_audio_backend = MlxAudioBackend(model=model)
    mlx_audio_backend._loaded_model_instance = loaded_model

    result = mlx_audio_backend.transcribe(audio_path, max_tokens)

    assert result.text == "你好"
    loaded_model.generate.assert_called_once_with(str(audio_path), **expected_kwargs)


def test_transcribe_rejects_unsupported_generation_limit(tmp_path: Path):
    """Test the direct backend rejects unsupported generation limits."""
    audio_path = _write_wav(tmp_path / "audio.wav")
    mlx_audio_backend = MlxAudioBackend(SENSEVOICE_MODEL)

    with pytest.raises(ValueError, match="sensevoice does not support"):
        mlx_audio_backend.transcribe(audio_path, 128)


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
    loaded_model = Mock()
    loaded_model.generate.return_value = model_result
    mlx_audio_backend = MlxAudioBackend()
    mlx_audio_backend._loaded_model_instance = loaded_model

    with pytest.raises(ValueError, match=expected_message):
        mlx_audio_backend.transcribe(audio_path)


@pytest.mark.parametrize(
    ("model", "model_type"),
    [
        (MIMO_MODEL, "mimo"),
        (QWEN3_ASR_MODEL, "qwen3_asr"),
        (SENSEVOICE_MODEL, "sensevoice"),
        (FIRERED_ASR2_MODEL, "fireredasr2"),
        (GLM_ASR_MODEL, "glm"),
    ],
    ids=["mimo", "qwen3-asr", "sensevoice", "firered-asr2", "glm-asr"],
)
def test_loaded_model_is_shared_by_model_key(
    monkeypatch: pytest.MonkeyPatch, model: MlxAudioModel, model_type: str
):
    """Test each model definition loads its runtime model once per cache key.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        model: MLX-Audio model
        model_type: expected MLX-Audio loader model type
    """
    load = Mock(return_value=object())
    get_snapshot_dir_path = Mock(return_value=Path("/cached/model"))
    monkeypatch.setattr(MlxAudioBackend, "_models_by_key", {})
    monkeypatch.setattr(backend, "import_mlx_audio_stt_load", Mock(return_value=load))
    monkeypatch.setattr(
        backend, "get_huggingface_snapshot_dir_path", get_snapshot_dir_path
    )

    first = MlxAudioBackend(model)
    second = MlxAudioBackend(model)

    assert first._loaded_model is load.return_value
    assert second._loaded_model is load.return_value
    get_snapshot_dir_path.assert_called_once_with(
        model.model_name, model.model_revision
    )
    load.assert_called_once_with(Path("/cached/model"), model_type=model_type)


def test_model_cache_key_includes_model_type(monkeypatch: pytest.MonkeyPatch):
    """Test loader types distinguish models with the same reference.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    models = [object(), object()]
    load = Mock(side_effect=models)
    get_snapshot_dir_path = Mock(return_value=Path("/cached/model"))
    monkeypatch.setattr(MlxAudioBackend, "_models_by_key", {})
    monkeypatch.setattr(backend, "import_mlx_audio_stt_load", Mock(return_value=load))
    monkeypatch.setattr(
        backend, "get_huggingface_snapshot_dir_path", get_snapshot_dir_path
    )
    alternate_model = replace(MIMO_MODEL, model_type="qwen3_asr")

    first = MlxAudioBackend(MIMO_MODEL)
    second = MlxAudioBackend(alternate_model)

    assert first._loaded_model is models[0]
    assert second._loaded_model is models[1]
    assert load.call_args_list == [
        call(Path("/cached/model"), model_type="mimo"),
        call(Path("/cached/model"), model_type="qwen3_asr"),
    ]


def test_model_validates_local_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Test local model paths are resolved before loading.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary directory path
    """
    model_path = tmp_path / "model"
    model_path.mkdir()
    load = Mock(return_value=object())
    monkeypatch.setattr(MlxAudioBackend, "_models_by_key", {})
    monkeypatch.setattr(backend, "import_mlx_audio_stt_load", Mock(return_value=load))

    model = replace(MIMO_MODEL, model_name=str(model_path))
    mlx_audio_backend = MlxAudioBackend(model)

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

    with pytest.raises(DependencyError, match="'transcription' extra"):
        import_mlx_audio_stt_load()


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
