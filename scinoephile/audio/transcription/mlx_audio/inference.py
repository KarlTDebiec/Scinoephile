#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Direct speech-to-text inference through MLX-Audio."""

from __future__ import annotations

import wave
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from scinoephile.common.validation import val_input_file_or_dir_path

__all__ = [
    "MlxAudioInferenceResult",
    "transcribe_with_mlx_audio",
]

_MLX_MODEL_BY_REFERENCE: dict[str, Any] = {}
"""Loaded MLX-Audio models keyed by model reference."""


@dataclass(frozen=True)
class MlxAudioInferenceResult:
    """Result of direct MLX-Audio inference."""

    text: str
    """Transcript text."""

    duration_seconds: float
    """Source audio duration in seconds."""

    generation_tokens: int | None = None
    """Number of generated text tokens, when reported by the model."""


def transcribe_with_mlx_audio(
    audio_path: Path,
    model_name: str,
    language: str,
    *,
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
    model = _get_or_load_mlx_audio_model(model_name)
    generate_kwargs: dict[str, object] = {"language": language}
    if max_tokens is not None:
        generate_kwargs["max_tokens"] = max_tokens
    result = model.generate(str(audio_path), **generate_kwargs)

    if isinstance(result, Mapping):
        result_mapping = cast(Mapping[str, object], result)
        text = result_mapping.get("text")
        generation_tokens = result_mapping.get("generation_tokens")
    else:
        text = getattr(result, "text", None)
        generation_tokens = getattr(result, "generation_tokens", None)
    if not isinstance(text, str):
        raise ValueError("MLX-Audio inference result is missing transcript text.")
    if generation_tokens is not None and (
        not isinstance(generation_tokens, int)
        or isinstance(generation_tokens, bool)
        or generation_tokens < 0
    ):
        raise ValueError(
            "MLX-Audio inference result has an invalid generation token count."
        )

    with wave.open(str(audio_path), "rb") as file:
        duration_seconds = file.getnframes() / file.getframerate()
    return MlxAudioInferenceResult(
        text=text,
        duration_seconds=duration_seconds,
        generation_tokens=generation_tokens,
    )


def _get_or_load_mlx_audio_model(model_name: str) -> Any:
    """Get a cached MLX-Audio model, loading it when necessary.

    Arguments:
        model_name: model name or local path
    Returns:
        loaded MLX-Audio model
    """
    model_reference: str | Path = model_name
    if model_name.startswith(("/", ".", "~")):
        model_reference = val_input_file_or_dir_path(model_name)
    cache_key = str(model_reference)
    if cache_key not in _MLX_MODEL_BY_REFERENCE:
        load = _import_mlx_audio_stt_load()
        _MLX_MODEL_BY_REFERENCE[cache_key] = load(model_reference)
    return _MLX_MODEL_BY_REFERENCE[cache_key]


def _import_mlx_audio_stt_load() -> Any:
    """Import the MLX-Audio STT model loader on demand.

    Returns:
        MLX-Audio STT load function
    Raises:
        ImportError: if MLX-Audio is unavailable
    """
    try:
        from mlx_audio.stt import load  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "MLX-Audio inference requires optional transcription dependencies. "
            "Install scinoephile with the 'transcription' extra."
        ) from exc
    return load
