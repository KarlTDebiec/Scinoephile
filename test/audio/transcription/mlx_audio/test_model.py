#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of executable MLX-Audio speech-to-text models."""

from __future__ import annotations

import builtins
import wave
from collections.abc import Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from scinoephile.audio.transcription.mlx_audio import model as mlx_audio_model
from scinoephile.audio.transcription.mlx_audio import tokenization
from scinoephile.audio.transcription.mlx_audio.model import MlxAudioModel
from scinoephile.audio.transcription.mlx_audio.model_spec import (
    FIRERED_ASR2_MODEL,
    GLM_ASR_MODEL,
    MIMO_MODEL,
    QWEN3_ASR_MODEL,
    SENSEVOICE_MODEL,
    MlxAudioModelSpec,
)
from scinoephile.audio.transcription.mlx_audio.tokenization import MIMO_AUDIO_TOKENIZER
from scinoephile.core import DependencyError, Language
from scinoephile.core.dependencies.transcription import import_mlx_audio_stt_load
from scinoephile.core.ml import ModelSpec


@pytest.fixture(autouse=True)
def use_apple_silicon_platform(monkeypatch: pytest.MonkeyPatch):
    """Run model tests as though on the supported platform."""
    monkeypatch.setattr(mlx_audio_model.platform, "system", Mock(return_value="Darwin"))
    monkeypatch.setattr(mlx_audio_model.platform, "machine", Mock(return_value="arm64"))


def test_mimo_uses_pinned_audio_tokenizer():
    """Test MiMo defines its required audio-tokenizer specification."""
    assert MIMO_MODEL.tokenizer is MIMO_AUDIO_TOKENIZER
    assert MIMO_AUDIO_TOKENIZER == ModelSpec(
        name="mlx-community/MiMo-Audio-Tokenizer",
        revision="6d451ed9a73024b4d33b87afa69e0dfd40d8f306",
    )


def test_model_returns_result_directly(tmp_path: Path):
    """Test the MLX-Audio model result is returned directly.

    Arguments:
        tmp_path: temporary directory path
    """
    audio_path = _write_wav(tmp_path / "audio.wav")
    runtime_model = Mock()
    model_result = SimpleNamespace(text="你好", generation_tokens=7)
    runtime_model.generate.return_value = model_result
    model = MlxAudioModel(MIMO_MODEL, Language.yue_hant)
    model.__dict__["model"] = runtime_model

    result = model(audio_path)

    assert result is model_result
    runtime_model.generate.assert_called_once_with(
        str(audio_path), language="zh", max_tokens=256
    )


@pytest.mark.parametrize(
    ("model", "expected_kwargs"),
    [
        (MIMO_MODEL, {"language": "zh", "max_tokens": 256}),
        (QWEN3_ASR_MODEL, {"language": "Cantonese", "max_tokens": 8192}),
        (SENSEVOICE_MODEL, {"language": "yue"}),
        (FIRERED_ASR2_MODEL, {}),
        (GLM_ASR_MODEL, {"max_tokens": 128}),
    ],
    ids=["mimo", "qwen3-asr", "sensevoice", "firered-asr2", "glm-asr"],
)
def test_model_adapts_model_specific_generation_arguments(
    tmp_path: Path, model: MlxAudioModelSpec, expected_kwargs: dict[str, object]
):
    """Test new model families receive only generation arguments they support.

    Arguments:
        tmp_path: temporary directory path
        model: MLX-Audio model
        expected_kwargs: model-specific generation arguments
    """
    audio_path = _write_wav(tmp_path / "audio.wav", duration_seconds=0.25)
    runtime_model = Mock()
    runtime_model.generate.return_value = SimpleNamespace(
        text="你好", generation_tokens=0
    )
    mlx_audio_model_instance = MlxAudioModel(spec=model, language=Language.yue_hant)
    mlx_audio_model_instance.__dict__["model"] = runtime_model

    result = mlx_audio_model_instance(audio_path)

    assert result.text == "你好"
    runtime_model.generate.assert_called_once_with(str(audio_path), **expected_kwargs)


@pytest.mark.parametrize(
    ("model", "max_tokens", "expected_message"),
    [
        (MIMO_MODEL, 0, "MLX-Audio max tokens must be positive"),
        (SENSEVOICE_MODEL, 128, "sensevoice does not support"),
    ],
    ids=["non-positive", "unsupported"],
)
def test_model_rejects_invalid_generation_limit(
    model: MlxAudioModelSpec, max_tokens: int, expected_message: str
):
    """Test model definitions reject invalid generation limits.

    Arguments:
        model: base MLX-Audio model
        max_tokens: invalid generation limit
        expected_message: expected validation error text
    """
    with pytest.raises(ValueError, match=expected_message):
        replace(model, max_tokens=max_tokens)


def test_model_rejects_invalid_safe_audio_duration():
    """Test model definitions require a positive safe audio duration."""
    with pytest.raises(ValueError, match="max safe audio duration must be positive"):
        replace(MIMO_MODEL, max_safe_audio_duration_seconds=0)


def test_init_rejects_unsupported_language():
    """Test the model rejects unsupported languages."""
    model = replace(MIMO_MODEL, languages={})

    with pytest.raises(ValueError, match="eng is not supported"):
        MlxAudioModel(model, Language.eng)


@pytest.mark.parametrize(
    ("system", "machine"),
    [("Linux", "arm64"), ("Darwin", "x86_64"), ("Windows", "ARM64")],
)
def test_model_rejects_unsupported_platform(
    monkeypatch: pytest.MonkeyPatch, system: str, machine: str
):
    """Test model loading rejects unsupported platforms.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        system: operating system name
        machine: machine architecture
    """
    monkeypatch.setattr(mlx_audio_model.platform, "system", Mock(return_value=system))
    monkeypatch.setattr(mlx_audio_model.platform, "machine", Mock(return_value=machine))
    model = MlxAudioModel(MIMO_MODEL, Language.yue_hant)

    with pytest.raises(RuntimeError, match="requires macOS on Apple Silicon"):
        _ = model.model


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
def test_model_is_cached(
    monkeypatch: pytest.MonkeyPatch, model: MlxAudioModelSpec, model_type: str
):
    """Test each model loads its runtime implementation once.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        model: MLX-Audio model
        model_type: expected MLX-Audio loader model type
    """
    runtime_model = Mock()
    load = Mock(return_value=runtime_model)
    get_snapshot_dir_path = Mock(return_value=Path("/cached/model"))
    mimo_asr = SimpleNamespace(get_model_path=Mock())
    monkeypatch.setattr(
        mlx_audio_model, "import_mlx_audio_stt_load", Mock(return_value=load)
    )
    monkeypatch.setattr(
        tokenization, "import_mlx_audio_mimo_asr", Mock(return_value=mimo_asr)
    )
    monkeypatch.setattr(
        mlx_audio_model, "get_huggingface_snapshot_dir_path", get_snapshot_dir_path
    )

    mlx_audio_model_instance = MlxAudioModel(model, Language.yue_hant)

    mlx_audio_model_instance(Path("audio.wav"))
    mlx_audio_model_instance(Path("audio.wav"))
    expected_snapshot_calls = [call(model.name, model.revision)]
    if model.tokenizer is not None:
        expected_snapshot_calls.append(
            call(model.tokenizer.name, model.tokenizer.revision)
        )
    assert get_snapshot_dir_path.call_args_list == expected_snapshot_calls
    load.assert_called_once_with(Path("/cached/model"), model_type=model_type)
    assert runtime_model.generate.call_count == 2


def test_mimo_audio_tokenizer_uses_pinned_local_snapshot(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test MiMo loading bypasses MLX-Audio's mutable remote tokenizer lookup.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    model_path = Path("/cached/mimo")
    audio_tokenizer_path = Path("/cached/mimo-audio-tokenizer")
    remote_get_model_path = Mock()
    mimo_asr = SimpleNamespace(get_model_path=remote_get_model_path)
    runtime_model = Mock()
    tokenizer = MIMO_MODEL.tokenizer
    assert tokenizer is not None

    def load(local_model_path: Path, **kwargs: object) -> object:
        """Check the replacement resolver while simulating model loading.

        Arguments:
            local_model_path: resolved local model path
            **kwargs: model loading arguments
        Returns:
            simulated runtime model
        """
        assert local_model_path == model_path
        assert kwargs == {"model_type": "mimo"}
        assert mimo_asr.get_model_path(tokenizer.name) == audio_tokenizer_path
        return runtime_model

    get_snapshot_dir_path = Mock(side_effect=(model_path, audio_tokenizer_path))
    monkeypatch.setattr(
        mlx_audio_model, "import_mlx_audio_stt_load", Mock(return_value=load)
    )
    monkeypatch.setattr(
        tokenization, "import_mlx_audio_mimo_asr", Mock(return_value=mimo_asr)
    )
    monkeypatch.setattr(
        mlx_audio_model, "get_huggingface_snapshot_dir_path", get_snapshot_dir_path
    )

    model = MlxAudioModel(MIMO_MODEL, Language.yue_hant)
    model(Path("audio.wav"))
    assert get_snapshot_dir_path.call_args_list == [
        call(MIMO_MODEL.name, MIMO_MODEL.revision),
        call(tokenizer.name, tokenizer.revision),
    ]
    assert mimo_asr.get_model_path is remote_get_model_path
    remote_get_model_path.assert_not_called()
    runtime_model.generate.assert_called_once()


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
        """Reject MLX-Audio while delegating all other imports.

        Arguments:
            name: module name
            globals: optional global namespace
            locals: optional local namespace
            fromlist: optional imported names
            level: relative import level
        Returns:
            imported module
        """
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
