#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Direct speech-to-text inference through MLX-Audio."""

from __future__ import annotations

import wave
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, cast

__all__ = [
    "MlxAudioInferenceResult",
    "transcribe_with_mlx_audio",
]

_MLX_AUDIO_EXTRA_MESSAGE = (
    "MLX-Audio inference requires optional transcription dependencies. "
    "Install scinoephile with the 'transcription' extra."
)
_MLX_MODEL_BY_REFERENCE: dict[str, Any] = {}
"""Loaded MLX-Audio models keyed by model reference."""


@dataclass(frozen=True)
class MlxAudioInferenceResult:
    """Result of direct MLX-Audio inference."""

    text: str
    duration_seconds: float


def transcribe_with_mlx_audio(
    audio_path: Path,
    *,
    model_name: str,
    language: str,
    max_tokens: int | None = None,
) -> MlxAudioInferenceResult:
    """Transcribe one audio file using MLX-Audio.

    Arguments:
        audio_path: audio file to transcribe
        model_name: model name or local path
        language: model-specific language identifier
        max_tokens: optional maximum number of text tokens to generate
    Returns:
        transcript text and source audio duration
    Raises:
        ImportError: if MLX-Audio is unavailable
        ValueError: if the model returns malformed output
    """
    model = _get_mlx_model(model_name)
    generate_kwargs: dict[str, object] = {"language": language}
    if max_tokens is not None:
        generate_kwargs["max_tokens"] = max_tokens
    result = model.generate(str(audio_path), **generate_kwargs)

    if isinstance(result, Mapping):
        text = cast(Mapping[str, object], result).get("text")
    else:
        text = getattr(result, "text", None)
    if not isinstance(text, str):
        raise ValueError("MLX-Audio inference result is missing transcript text.")

    with wave.open(str(audio_path), "rb") as file:
        duration_seconds = file.getnframes() / file.getframerate()
    return MlxAudioInferenceResult(text=text, duration_seconds=duration_seconds)


def _get_mlx_load() -> Any:
    """Get the MLX-Audio STT model loader.

    Returns:
        MLX-Audio STT load function
    Raises:
        ImportError: if MLX-Audio is unavailable
    """
    try:
        mlx_stt = import_module("mlx_audio.stt")
    except ImportError as exc:
        raise ImportError(_MLX_AUDIO_EXTRA_MESSAGE) from exc
    return getattr(mlx_stt, "load")


def _get_mlx_model(model_name: str) -> Any:
    """Get a cached MLX-Audio model.

    Arguments:
        model_name: model name or local path
    Returns:
        loaded MLX-Audio model
    """
    model_path = Path(model_name).expanduser()
    model_reference: str | Path = model_name
    if model_path.is_absolute() or model_name.startswith("~"):
        model_reference = model_path
    cache_key = str(model_reference)
    if cache_key not in _MLX_MODEL_BY_REFERENCE:
        load = _get_mlx_load()
        _MLX_MODEL_BY_REFERENCE[cache_key] = load(model_reference)
    return _MLX_MODEL_BY_REFERENCE[cache_key]
