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
from scinoephile.audio.transcription.mlx_audio.backend import MlxAudioBackend
from scinoephile.audio.transcription.mlx_audio.model import (
    FIRERED_ASR2_MODEL,
    GLM_ASR_MODEL,
    MIMO_MODEL,
    QWEN3_ASR_MODEL,
    SENSEVOICE_MODEL,
    MlxAudioModel,
)
from scinoephile.audio.transcription.mlx_audio.tokenizer_model import (
    MIMO_AUDIO_TOKENIZER_MODEL,
    MlxAudioTokenizerModel,
)
from scinoephile.core import Language
from scinoephile.core.dependencies import transcription as transcription_dependencies


def test_mimo_uses_pinned_audio_tokenizer_model():
    """Test MiMo defines its required audio-tokenizer model."""
    assert MIMO_MODEL.audio_tokenizer is MIMO_AUDIO_TOKENIZER_MODEL
    assert MIMO_AUDIO_TOKENIZER_MODEL == MlxAudioTokenizerModel(
        name="mlx-community/MiMo-Audio-Tokenizer",
        revision="6d451ed9a73024b4d33b87afa69e0dfd40d8f306",
    )


def test_transcribe_returns_model_result(tmp_path: Path):
    """Test the MLX-Audio model result is returned directly.

    Arguments:
        tmp_path: temporary directory path
    """
    audio_path = _write_wav(tmp_path / "audio.wav")
    loaded_model = Mock()
    model_result = SimpleNamespace(text="你好", generation_tokens=7)
    loaded_model.generate.return_value = model_result
    mlx_audio_backend = MlxAudioBackend(MIMO_MODEL)
    mlx_audio_backend._loaded_model_instance = loaded_model

    result = mlx_audio_backend.transcribe(audio_path, 256)

    assert result is model_result
    loaded_model.generate.assert_called_once_with(
        str(audio_path), language="zh", max_tokens=256
    )


@pytest.mark.parametrize(
    ("model", "max_tokens", "expected_kwargs"),
    [
        (MIMO_MODEL, 128, {"language": "zh", "max_tokens": 128}),
        (QWEN3_ASR_MODEL, 128, {"language": "Cantonese", "max_tokens": 128}),
        (SENSEVOICE_MODEL, None, {"language": "yue"}),
        (FIRERED_ASR2_MODEL, 128, {"max_len": 128}),
        (GLM_ASR_MODEL, 128, {"max_tokens": 128}),
    ],
    ids=["mimo", "qwen3-asr", "sensevoice", "firered-asr2", "glm-asr"],
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
    loaded_model.generate.return_value = SimpleNamespace(
        text="你好", generation_tokens=0
    )
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


def test_transcribe_rejects_unsupported_language(tmp_path: Path):
    """Test the direct backend rejects unsupported languages.

    Arguments:
        tmp_path: temporary directory path
    """
    audio_path = _write_wav(tmp_path / "audio.wav")
    model = replace(MIMO_MODEL, languages={})
    mlx_audio_backend = MlxAudioBackend(model, Language.eng)

    with pytest.raises(ValueError, match="eng is not supported"):
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
def test_loaded_model_is_cached_by_backend(
    monkeypatch: pytest.MonkeyPatch, model: MlxAudioModel, model_type: str
):
    """Test each backend loads its runtime model once.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        model: MLX-Audio model
        model_type: expected MLX-Audio loader model type
    """
    load = Mock(return_value=object())
    get_snapshot_dir_path = Mock(return_value=Path("/cached/model"))
    mimo_asr = SimpleNamespace(get_model_path=Mock())
    monkeypatch.setattr(backend, "import_mlx_audio_stt_load", Mock(return_value=load))
    monkeypatch.setattr(
        backend, "import_mlx_audio_mimo_asr", Mock(return_value=mimo_asr)
    )
    monkeypatch.setattr(
        backend, "get_huggingface_snapshot_dir_path", get_snapshot_dir_path
    )

    mlx_audio_backend = MlxAudioBackend(model)

    assert mlx_audio_backend._loaded_model is load.return_value
    assert mlx_audio_backend._loaded_model is load.return_value
    expected_snapshot_calls = [call(model.name, model.revision)]
    if model.audio_tokenizer is not None:
        expected_snapshot_calls.append(
            call(model.audio_tokenizer.name, model.audio_tokenizer.revision)
        )
    assert get_snapshot_dir_path.call_args_list == expected_snapshot_calls
    load.assert_called_once_with(Path("/cached/model"), model_type=model_type)


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
    loaded_model = object()
    audio_tokenizer = MIMO_MODEL.audio_tokenizer
    assert audio_tokenizer is not None

    def load(local_model_path: Path, **kwargs: object) -> object:
        """Check the replacement resolver while simulating model loading."""
        assert local_model_path == model_path
        assert kwargs == {"model_type": "mimo"}
        assert mimo_asr.get_model_path(audio_tokenizer.name) == audio_tokenizer_path
        return loaded_model

    get_snapshot_dir_path = Mock(side_effect=(model_path, audio_tokenizer_path))
    monkeypatch.setattr(backend, "import_mlx_audio_stt_load", Mock(return_value=load))
    monkeypatch.setattr(
        backend, "import_mlx_audio_mimo_asr", Mock(return_value=mimo_asr)
    )
    monkeypatch.setattr(
        backend, "get_huggingface_snapshot_dir_path", get_snapshot_dir_path
    )

    assert MlxAudioBackend(MIMO_MODEL)._loaded_model is loaded_model
    assert get_snapshot_dir_path.call_args_list == [
        call(MIMO_MODEL.name, MIMO_MODEL.revision),
        call(audio_tokenizer.name, audio_tokenizer.revision),
    ]
    assert mimo_asr.get_model_path is remote_get_model_path
    remote_get_model_path.assert_not_called()


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
