#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of direct MLX-Audio inference."""

from __future__ import annotations

import builtins
import json
import wave
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from scinoephile.audio.transcription.mlx_audio import inference
from scinoephile.audio.transcription.mlx_audio.inference import (
    MIMO_MODEL_NAME,
    QWEN3_ASR_MODEL_NAME,
    MlxAudioInference,
    MlxAudioInferenceResult,
)
from scinoephile.core import Language


def test_transcribe_reads_mapping_result(
    tmp_path: Path,
):
    """Test mapping output and generation arguments are normalized.

    Arguments:
        tmp_path: temporary directory path
    """
    audio_path = _write_wav(tmp_path / "audio.wav", duration_seconds=0.5)
    model = Mock()
    model.generate.return_value = {"text": "你好", "generation_tokens": 7}
    mlx_audio_inference = MlxAudioInference()
    mlx_audio_inference._model = model

    result = mlx_audio_inference.transcribe(
        audio_path,
        128,
    )

    assert result == MlxAudioInferenceResult(
        text="你好",
        generation_tokens=7,
    )
    model.generate.assert_called_once_with(
        str(audio_path),
        language="zh",
        max_tokens=128,
    )


def test_transcribe_reads_object_result(
    tmp_path: Path,
):
    """Test attribute-based output and omitted token limits are normalized.

    Arguments:
        tmp_path: temporary directory path
    """
    audio_path = _write_wav(tmp_path / "audio.wav", duration_seconds=0.25)
    model = Mock()
    model.generate.return_value = SimpleNamespace(text="hello")
    mlx_audio_inference = MlxAudioInference(language=Language.eng)
    mlx_audio_inference._model = model

    result = mlx_audio_inference.transcribe(audio_path)

    assert result.text == "hello"
    assert result.generation_tokens is None
    model.generate.assert_called_once_with(str(audio_path), language="en")


def test_transcribe_rejects_missing_text(
    tmp_path: Path,
):
    """Test output without transcript text is rejected.

    Arguments:
        tmp_path: temporary directory path
    """
    audio_path = _write_wav(tmp_path / "audio.wav")
    model = Mock()
    model.generate.return_value = {}
    mlx_audio_inference = MlxAudioInference()
    mlx_audio_inference._model = model

    with pytest.raises(ValueError, match="missing transcript text"):
        mlx_audio_inference.transcribe(audio_path)


@pytest.mark.parametrize("generation_tokens", [True, -1, 1.5, "1"])
def test_transcribe_rejects_invalid_generation_tokens(
    tmp_path: Path,
    generation_tokens: object,
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
    mlx_audio_inference = MlxAudioInference()
    mlx_audio_inference._model = model

    with pytest.raises(ValueError, match="invalid generation token count"):
        mlx_audio_inference.transcribe(audio_path)


def test_model_is_shared_by_reference(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test a model is loaded once per resolved reference.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    models = [object(), object()]
    load = Mock(side_effect=models)
    monkeypatch.setattr(MlxAudioInference, "_models_by_reference", {})
    monkeypatch.setattr(
        inference, "_import_mlx_audio_stt_load", Mock(return_value=load)
    )

    first = MlxAudioInference(MIMO_MODEL_NAME)
    second = MlxAudioInference(MIMO_MODEL_NAME)
    third = MlxAudioInference(QWEN3_ASR_MODEL_NAME)

    assert first._loaded_model is models[0]
    assert second._loaded_model is models[0]
    assert third._loaded_model is models[1]
    assert load.call_count == 2
    assert load.call_args_list[0].args == (MIMO_MODEL_NAME,)
    assert load.call_args_list[0].kwargs == {"model_type": "mimo"}
    assert load.call_args_list[1].args == (QWEN3_ASR_MODEL_NAME,)
    assert load.call_args_list[1].kwargs == {"model_type": "qwen3_asr"}


def test_model_validates_local_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test local model paths are resolved before loading.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary directory path
    """
    model_path = tmp_path / "model"
    model_path.mkdir()
    (model_path / "config.json").write_text(
        json.dumps({"architectures": ["MiMoV2ASRForCausalLM"]}),
        encoding="utf-8",
    )
    load = Mock(return_value=object())
    monkeypatch.setattr(MlxAudioInference, "_models_by_reference", {})
    monkeypatch.setattr(
        inference, "_import_mlx_audio_stt_load", Mock(return_value=load)
    )

    mlx_audio_inference = MlxAudioInference(str(model_path))

    assert mlx_audio_inference._loaded_model is load.return_value
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
        inference._import_mlx_audio_stt_load()


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
