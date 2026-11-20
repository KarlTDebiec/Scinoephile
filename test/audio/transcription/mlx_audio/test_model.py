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
from typing import Any
from unittest.mock import Mock, call

import pytest

import scinoephile.audio.transcription.mlx_audio.model as mlx_audio_model_module
from scinoephile.audio.transcription.mlx_audio import (
    FIRERED_ASR2_MODEL,
    GLM_ASR_MODEL,
    MIMO_AUDIO_TOKENIZER,
    MIMO_MODEL,
    QWEN3_ASR_MODEL,
    SENSEVOICE_MODEL,
    MlxAudioModel,
    MlxAudioModelSpec,
    tokenization,
)
from scinoephile.core import DependencyError, Language
from scinoephile.core.dependencies.transcription import import_mlx_audio_stt_load
from scinoephile.core.ml import ModelSpec


@pytest.fixture(autouse=True)
def use_apple_silicon_platform(monkeypatch: pytest.MonkeyPatch):
    """Run model tests as though on the supported platform.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    monkeypatch.setattr(
        mlx_audio_model_module.platform, "system", Mock(return_value="Darwin")
    )
    monkeypatch.setattr(
        mlx_audio_model_module.platform, "machine", Mock(return_value="arm64")
    )


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


def test_release_clears_loaded_weights_once(monkeypatch: pytest.MonkeyPatch):
    """Release resident weights without initializing an unused backend.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    mx = Mock()
    import_core = Mock(return_value=mx)
    monkeypatch.setattr(mlx_audio_model_module, "import_mlx_core", import_core)
    model = MlxAudioModel(QWEN3_ASR_MODEL, Language.yue_hant)
    model.release()
    import_core.assert_not_called()
    model.__dict__["model"] = Mock()

    model.release()
    model.release()

    assert "model" not in model.__dict__
    mx.synchronize.assert_called_once_with()
    mx.clear_cache.assert_called_once_with()


@pytest.mark.parametrize("fails", [False, True])
def test_inference_releases_weights_before_return(tmp_path: Path, fails: bool):
    """Release recognition weights before alignment, including failed inference.

    Arguments:
        tmp_path: temporary directory path
        fails: whether inference raises an exception
    """
    model = MlxAudioModel(
        QWEN3_ASR_MODEL, Language.yue_hant, release_after_inference=True
    )
    runtime = Mock()
    model.__dict__["model"] = runtime
    model.release = Mock()
    if fails:
        runtime.generate.side_effect = ValueError("inference failed")
        with pytest.raises(ValueError, match="inference failed"):
            model(tmp_path / "audio.wav")
    else:
        assert model(tmp_path / "audio.wav") is runtime.generate.return_value
    model.release.assert_called_once_with()


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
    monkeypatch.setattr(
        mlx_audio_model_module.platform, "system", Mock(return_value=system)
    )
    monkeypatch.setattr(
        mlx_audio_model_module.platform, "machine", Mock(return_value=machine)
    )
    model = MlxAudioModel(MIMO_MODEL, Language.yue_hant)

    with pytest.raises(DependencyError, match="requires macOS on Apple Silicon"):
        _ = model.model


@pytest.mark.parametrize("cuda_available", [True, False])
def test_windows_requires_available_cuda_backend(
    monkeypatch: pytest.MonkeyPatch, cuda_available: bool
):
    """Check CUDA availability before downloading a model on Windows.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        cuda_available: whether the native CUDA backend is available
    """
    monkeypatch.setattr(mlx_audio_model_module.platform, "system", lambda: "Windows")
    monkeypatch.setattr(mlx_audio_model_module.platform, "machine", lambda: "AMD64")
    mx = SimpleNamespace(
        cuda=SimpleNamespace(is_available=lambda: cuda_available),
        gpu=object(),
        set_default_device=Mock(),
    )
    monkeypatch.setattr(mlx_audio_model_module, "import_mlx_core", lambda: mx)
    load = Mock()
    snapshot = Mock(return_value=Path("/cached/model"))
    monkeypatch.setattr(
        mlx_audio_model_module, "import_mlx_audio_stt_load", lambda: load
    )
    monkeypatch.setattr(
        mlx_audio_model_module, "get_huggingface_snapshot_dir_path", snapshot
    )
    model = MlxAudioModel(QWEN3_ASR_MODEL, Language.yue_hant)

    if cuda_available:
        assert model.model is load.return_value
        mx.set_default_device.assert_called_once_with(mx.gpu)
        snapshot.assert_called_once_with(QWEN3_ASR_MODEL.name, QWEN3_ASR_MODEL.revision)
    else:
        with pytest.raises(DependencyError, match="MLX CUDA backend"):
            _ = model.model
        snapshot.assert_not_called()
        load.assert_not_called()


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
        mlx_audio_model_module, "import_mlx_audio_stt_load", Mock(return_value=load)
    )
    monkeypatch.setattr(
        tokenization, "import_mlx_audio_mimo_asr", Mock(return_value=mimo_asr)
    )
    monkeypatch.setattr(
        mlx_audio_model_module,
        "get_huggingface_snapshot_dir_path",
        get_snapshot_dir_path,
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
    other_model_path = Path("/cached/other")
    remote_get_model_path = Mock(return_value=other_model_path)
    mimo_asr = SimpleNamespace(get_model_path=remote_get_model_path)
    runtime_model = Mock()
    tokenizer = MIMO_MODEL.tokenizer
    assert tokenizer is not None

    def load(local_model_path: Path, **kwargs: Any) -> object:
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
        assert (
            mimo_asr.get_model_path("other/model", "revision", local_only=True)
            == other_model_path
        )
        return runtime_model

    get_snapshot_dir_path = Mock(side_effect=(model_path, audio_tokenizer_path))
    monkeypatch.setattr(
        mlx_audio_model_module, "import_mlx_audio_stt_load", Mock(return_value=load)
    )
    monkeypatch.setattr(
        tokenization, "import_mlx_audio_mimo_asr", Mock(return_value=mimo_asr)
    )
    monkeypatch.setattr(
        mlx_audio_model_module,
        "get_huggingface_snapshot_dir_path",
        get_snapshot_dir_path,
    )

    model = MlxAudioModel(MIMO_MODEL, Language.yue_hant)
    model(Path("audio.wav"))
    assert get_snapshot_dir_path.call_args_list == [
        call(MIMO_MODEL.name, MIMO_MODEL.revision),
        call(tokenizer.name, tokenizer.revision),
    ]
    assert mimo_asr.get_model_path is remote_get_model_path
    remote_get_model_path.assert_called_once_with(
        "other/model", "revision", local_only=True
    )
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
        Raises:
            ImportError: if the operation fails
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
