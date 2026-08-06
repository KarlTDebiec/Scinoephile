#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the MLX-Audio speech-to-text backend."""

from __future__ import annotations

import builtins
import json
import wave
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from scinoephile.audio.transcription.exceptions import TranscriptionError
from scinoephile.audio.transcription.mlx_audio import backend
from scinoephile.audio.transcription.mlx_audio.backend import (
    FIRERED_ASR2_MODEL_NAME,
    GLM_ASR_MODEL_NAME,
    MIMO_MODEL_NAME,
    QWEN3_ASR_MODEL_NAME,
    SENSEVOICE_MODEL_NAME,
    MlxAudioBackend,
    MlxAudioInferenceResult,
)
from scinoephile.core import Language
from scinoephile.core.dependencies import transcription as transcription_dependencies


@pytest.mark.parametrize(
    ("model_name", "language", "mlx_audio_language"),
    [
        (MIMO_MODEL_NAME, Language.eng, "en"),
        (MIMO_MODEL_NAME, Language.yue_hans, "zh"),
        (MIMO_MODEL_NAME, Language.yue_hant, "zh"),
        (MIMO_MODEL_NAME, Language.zho_hans, "zh"),
        (MIMO_MODEL_NAME, Language.zho_hant, "zh"),
        (QWEN3_ASR_MODEL_NAME, Language.eng, "English"),
        (QWEN3_ASR_MODEL_NAME, Language.yue_hans, "Cantonese"),
        (QWEN3_ASR_MODEL_NAME, Language.yue_hant, "Cantonese"),
        (QWEN3_ASR_MODEL_NAME, Language.zho_hans, "Chinese"),
        (QWEN3_ASR_MODEL_NAME, Language.zho_hant, "Chinese"),
        (SENSEVOICE_MODEL_NAME, Language.eng, "en"),
        (SENSEVOICE_MODEL_NAME, Language.yue_hans, "yue"),
        (SENSEVOICE_MODEL_NAME, Language.yue_hant, "yue"),
        (SENSEVOICE_MODEL_NAME, Language.zho_hans, "zh"),
        (SENSEVOICE_MODEL_NAME, Language.zho_hant, "zh"),
        (FIRERED_ASR2_MODEL_NAME, Language.yue_hant, None),
        (GLM_ASR_MODEL_NAME, Language.yue_hant, None),
    ],
)
def test_init_derives_mlx_audio_languages(
    model_name: str, language: Language, mlx_audio_language: str
):
    """Test each model family derives its language identifier."""
    mlx_audio_backend = MlxAudioBackend(model_name=model_name, language=language)

    assert mlx_audio_backend.mlx_audio_language == mlx_audio_language


def test_init_matches_model_name_case_insensitively():
    """Test supported model profiles match model names case-insensitively."""
    mlx_audio_backend = MlxAudioBackend("custom/QWEN3-ASR-0.6B-8bit")

    assert mlx_audio_backend.model_family == "qwen3-asr"


@pytest.mark.parametrize(
    ("metadata", "expected_family"),
    [
        ({"architectures": ["MiMoV2ASRForCausalLM"]}, "mimo"),
        ({"model_type": "qwen3_asr"}, "qwen3-asr"),
        ({"model_type": "sensevoice"}, "sensevoice"),
        ({"model_type": "fireredasr2"}, "firered-asr2"),
        ({"model_type": "glm"}, "glm-asr"),
    ],
)
def test_init_reads_local_model_metadata(
    tmp_path: Path, metadata: dict[str, object], expected_family: str
):
    """Test arbitrary local directories are identified from model metadata."""
    model_path = tmp_path / "asr"
    model_path.mkdir()
    (model_path / "config.json").write_text(json.dumps(metadata), encoding="utf-8")

    mlx_audio_backend = MlxAudioBackend(str(model_path))

    assert mlx_audio_backend.model_family == expected_family


def test_init_rejects_untested_family():
    """Test unknown MLX-Audio model families fail clearly."""
    with pytest.raises(
        TranscriptionError,
        match=(
            "supported families: firered-asr2, glm-asr, mimo, qwen3-asr, sensevoice"
        ),
    ):
        MlxAudioBackend("mlx-community/Whisper-Large-v3-MLX")


def test_transcribe_reads_mapping_result(tmp_path: Path):
    """Test mapping output and generation arguments are normalized.

    Arguments:
        tmp_path: temporary directory path
    """
    audio_path = _write_wav(tmp_path / "audio.wav", duration_seconds=0.5)
    model = Mock()
    model.generate.return_value = {"text": "你好", "generation_tokens": 7}
    mlx_audio_backend = MlxAudioBackend()
    mlx_audio_backend._model = model

    result = mlx_audio_backend.transcribe(audio_path, 128)

    assert result == MlxAudioInferenceResult(text="你好", generation_tokens=7)
    model.generate.assert_called_once_with(
        str(audio_path), language="zh", max_tokens=128
    )


def test_transcribe_reads_object_result(tmp_path: Path):
    """Test attribute-based output and omitted token limits are normalized.

    Arguments:
        tmp_path: temporary directory path
    """
    audio_path = _write_wav(tmp_path / "audio.wav", duration_seconds=0.25)
    model = Mock()
    model.generate.return_value = SimpleNamespace(text="hello")
    mlx_audio_backend = MlxAudioBackend(language=Language.eng)
    mlx_audio_backend._model = model

    result = mlx_audio_backend.transcribe(audio_path)

    assert result.text == "hello"
    assert result.generation_tokens is None
    model.generate.assert_called_once_with(str(audio_path), language="en")


@pytest.mark.parametrize(
    ("model_name", "max_tokens", "expected_kwargs"),
    [
        (SENSEVOICE_MODEL_NAME, 128, {"language": "yue"}),
        (FIRERED_ASR2_MODEL_NAME, 128, {"max_len": 128}),
        (GLM_ASR_MODEL_NAME, 128, {"max_tokens": 128}),
    ],
)
def test_transcribe_adapts_model_specific_generation_arguments(
    tmp_path: Path, model_name: str, max_tokens: int, expected_kwargs: dict[str, object]
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


def test_transcribe_rejects_missing_text(tmp_path: Path):
    """Test output without transcript text is rejected.

    Arguments:
        tmp_path: temporary directory path
    """
    audio_path = _write_wav(tmp_path / "audio.wav")
    model = Mock()
    model.generate.return_value = {}
    mlx_audio_backend = MlxAudioBackend()
    mlx_audio_backend._model = model

    with pytest.raises(ValueError, match="missing transcript text"):
        mlx_audio_backend.transcribe(audio_path)


@pytest.mark.parametrize("generation_tokens", [True, -1, 1.5, "1"])
def test_transcribe_rejects_invalid_generation_tokens(
    tmp_path: Path, generation_tokens: object
):
    """Test malformed generation token counts are rejected.

    Arguments:
        tmp_path: temporary directory path
        generation_tokens: invalid token count
    """
    audio_path = _write_wav(tmp_path / "audio.wav")
    model = Mock()
    model.generate.return_value = {
        "text": "你好",
        "generation_tokens": generation_tokens,
    }
    mlx_audio_backend = MlxAudioBackend()
    mlx_audio_backend._model = model

    with pytest.raises(ValueError, match="invalid generation token count"):
        mlx_audio_backend.transcribe(audio_path)


def test_model_is_shared_by_reference(monkeypatch: pytest.MonkeyPatch):
    """Test a model is loaded once per resolved reference.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    models = [object() for _ in range(5)]
    load = Mock(side_effect=models)
    monkeypatch.setattr(MlxAudioBackend, "_models_by_reference", {})
    monkeypatch.setattr(backend, "import_mlx_audio_stt_load", Mock(return_value=load))

    first = MlxAudioBackend(MIMO_MODEL_NAME)
    second = MlxAudioBackend(MIMO_MODEL_NAME)
    third = MlxAudioBackend(QWEN3_ASR_MODEL_NAME)
    fourth = MlxAudioBackend(SENSEVOICE_MODEL_NAME)
    fifth = MlxAudioBackend(FIRERED_ASR2_MODEL_NAME)
    sixth = MlxAudioBackend(GLM_ASR_MODEL_NAME)

    assert first._loaded_model is models[0]
    assert second._loaded_model is models[0]
    assert third._loaded_model is models[1]
    assert fourth._loaded_model is models[2]
    assert fifth._loaded_model is models[3]
    assert sixth._loaded_model is models[4]
    assert load.call_count == 5
    assert load.call_args_list[0].args == (MIMO_MODEL_NAME,)
    assert load.call_args_list[0].kwargs == {"model_type": "mimo"}
    assert load.call_args_list[1].args == (QWEN3_ASR_MODEL_NAME,)
    assert load.call_args_list[1].kwargs == {"model_type": "qwen3_asr"}
    assert load.call_args_list[2].args == (SENSEVOICE_MODEL_NAME,)
    assert load.call_args_list[2].kwargs == {"model_type": "sensevoice"}
    assert load.call_args_list[3].args == (FIRERED_ASR2_MODEL_NAME,)
    assert load.call_args_list[3].kwargs == {"model_type": "fireredasr2"}
    assert load.call_args_list[4].args == (GLM_ASR_MODEL_NAME,)
    assert load.call_args_list[4].kwargs == {"model_type": "glm"}


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
    monkeypatch.setattr(MlxAudioBackend, "_models_by_reference", {})
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
