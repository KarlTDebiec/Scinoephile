#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of direct MLX-Audio speech recognition."""

from __future__ import annotations

import builtins
import wave
from collections.abc import Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from scinoephile.audio.transcription.mlx_audio import helpers, recognizer
from scinoephile.audio.transcription.mlx_audio.model import (
    FIRERED_ASR2_MODEL,
    GLM_ASR_MODEL,
    MIMO_MODEL,
    QWEN3_ASR_MODEL,
    SENSEVOICE_MODEL,
    MlxAudioModelSpec,
)
from scinoephile.audio.transcription.mlx_audio.recognizer import MlxAudioRecognizer
from scinoephile.audio.transcription.mlx_audio.tokenizer import (
    MIMO_AUDIO_TOKENIZER,
    MlxAudioTokenizerSpec,
)
from scinoephile.core import Language
from scinoephile.core.dependencies import transcription as transcription_dependencies


def test_mimo_uses_pinned_audio_tokenizer():
    """Test MiMo defines its required audio-tokenizer specification."""
    assert MIMO_MODEL.tokenizer is MIMO_AUDIO_TOKENIZER
    assert MIMO_AUDIO_TOKENIZER == MlxAudioTokenizerSpec(
        name="mlx-community/MiMo-Audio-Tokenizer",
        revision="6d451ed9a73024b4d33b87afa69e0dfd40d8f306",
    )


def test_recognize_returns_model_result(tmp_path: Path):
    """Test the MLX-Audio model result is returned directly.

    Arguments:
        tmp_path: temporary directory path
    """
    audio_path = _write_wav(tmp_path / "audio.wav")
    loaded_model = Mock()
    model_result = SimpleNamespace(text="你好", generation_tokens=7)
    loaded_model.generate.return_value = model_result
    mlx_audio_recognizer = MlxAudioRecognizer(MIMO_MODEL)
    mlx_audio_recognizer.__dict__["model"] = loaded_model

    result = mlx_audio_recognizer.recognize(audio_path)

    assert result is model_result
    loaded_model.generate.assert_called_once_with(
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
def test_recognize_adapts_model_specific_generation_arguments(
    tmp_path: Path, model: MlxAudioModelSpec, expected_kwargs: dict[str, object]
):
    """Test new model families receive only generation arguments they support.

    Arguments:
        tmp_path: temporary directory path
        model: MLX-Audio model
        expected_kwargs: model-specific generation arguments
    """
    audio_path = _write_wav(tmp_path / "audio.wav", duration_seconds=0.25)
    loaded_model = Mock()
    loaded_model.generate.return_value = SimpleNamespace(
        text="你好", generation_tokens=0
    )
    mlx_audio_recognizer = MlxAudioRecognizer(model_spec=model)
    mlx_audio_recognizer.__dict__["model"] = loaded_model

    result = mlx_audio_recognizer.recognize(audio_path)

    assert result.text == "你好"
    loaded_model.generate.assert_called_once_with(str(audio_path), **expected_kwargs)


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


def test_init_rejects_unsupported_language():
    """Test the recognizer rejects unsupported languages."""
    model = replace(MIMO_MODEL, languages={})

    with pytest.raises(ValueError, match="eng is not supported"):
        MlxAudioRecognizer(model, Language.eng)


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
def test_model_is_cached_by_recognizer(
    monkeypatch: pytest.MonkeyPatch, model: MlxAudioModelSpec, model_type: str
):
    """Test each recognizer loads its runtime model once.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        model: MLX-Audio model
        model_type: expected MLX-Audio loader model type
    """
    loaded_model = Mock()
    load = Mock(return_value=loaded_model)
    get_snapshot_dir_path = Mock(return_value=Path("/cached/model"))
    mimo_asr = SimpleNamespace(get_model_path=Mock())
    monkeypatch.setattr(
        recognizer, "import_mlx_audio_stt_load", Mock(return_value=load)
    )
    monkeypatch.setattr(
        helpers, "import_mlx_audio_mimo_asr", Mock(return_value=mimo_asr)
    )
    monkeypatch.setattr(
        recognizer, "get_huggingface_snapshot_dir_path", get_snapshot_dir_path
    )

    mlx_audio_recognizer = MlxAudioRecognizer(model)

    mlx_audio_recognizer.recognize(Path("audio.wav"))
    mlx_audio_recognizer.recognize(Path("audio.wav"))
    expected_snapshot_calls = [call(model.name, model.revision)]
    if model.tokenizer is not None:
        expected_snapshot_calls.append(
            call(model.tokenizer.name, model.tokenizer.revision)
        )
    assert get_snapshot_dir_path.call_args_list == expected_snapshot_calls
    load.assert_called_once_with(Path("/cached/model"), model_type=model_type)
    assert loaded_model.generate.call_count == 2


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
    loaded_model = Mock()
    tokenizer = MIMO_MODEL.tokenizer
    assert tokenizer is not None

    def load(local_model_path: Path, **kwargs: object) -> object:
        """Check the replacement resolver while simulating model loading."""
        assert local_model_path == model_path
        assert kwargs == {"model_type": "mimo"}
        assert mimo_asr.get_model_path(tokenizer.name) == audio_tokenizer_path
        return loaded_model

    get_snapshot_dir_path = Mock(side_effect=(model_path, audio_tokenizer_path))
    monkeypatch.setattr(
        recognizer, "import_mlx_audio_stt_load", Mock(return_value=load)
    )
    monkeypatch.setattr(
        helpers, "import_mlx_audio_mimo_asr", Mock(return_value=mimo_asr)
    )
    monkeypatch.setattr(
        recognizer, "get_huggingface_snapshot_dir_path", get_snapshot_dir_path
    )

    mlx_audio_recognizer = MlxAudioRecognizer(MIMO_MODEL)
    mlx_audio_recognizer.recognize(Path("audio.wav"))
    assert get_snapshot_dir_path.call_args_list == [
        call(MIMO_MODEL.name, MIMO_MODEL.revision),
        call(tokenizer.name, tokenizer.revision),
    ]
    assert mimo_asr.get_model_path is remote_get_model_path
    remote_get_model_path.assert_not_called()
    loaded_model.generate.assert_called_once()


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
