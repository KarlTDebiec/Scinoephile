#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Direct MLX-Audio speech recognition."""

from __future__ import annotations

import platform
from functools import cached_property
from pathlib import Path
from typing import Any, Protocol, cast

from scinoephile.core.dependencies.transcription import import_mlx_audio_stt_load
from scinoephile.core.language import Language
from scinoephile.core.ml import get_huggingface_snapshot_dir_path

from .helpers import use_local_tokenizer
from .model_spec import MlxAudioModelSpec

__all__ = ["MlxAudioRecognizer", "MlxAudioResult"]


class MlxAudioResult(Protocol):
    """Structural result returned by MLX-Audio recognition."""

    text: str
    """Transcript text."""

    generation_tokens: int
    """Number of generated text tokens."""


class MlxAudioRecognizer:
    """Runs direct speech-to-text inference through one MLX-Audio model."""

    def __init__(
        self, model_spec: MlxAudioModelSpec, language: Language = Language.yue_hant
    ):
        """Initialize.

        Arguments:
            model_spec: MLX-Audio model specification
            language: language to transcribe
        Raises:
            ValueError: if the model does not support the language
        """
        self.model_spec = model_spec
        """Selected MLX-Audio model specification."""

        if language not in self.model_spec.languages:
            raise ValueError(
                f"{language} is not supported by MLX-Audio "
                f"{self.model_spec.model_type} transcription"
            )
        self.language = language
        """Language to transcribe."""

    def __call__(self, audio_path: Path) -> MlxAudioResult:
        """Recognize speech in one audio file using MLX-Audio.

        Arguments:
            audio_path: audio file to transcribe
        Returns:
            MLX-Audio recognition result
        Raises:
            ImportError: if MLX-Audio is unavailable
        """
        return self.model.generate(str(audio_path), **self.generate_kw)

    @cached_property
    def generate_kw(self) -> dict[str, object]:
        """Get model-specific keyword arguments for MLX-Audio generation.

        Returns:
            keyword arguments for the selected model's generate method
        """
        generate_kw: dict[str, object] = {}

        model_language = self.model_spec.languages.get(self.language)
        if model_language is not None:
            generate_kw["language"] = model_language

        max_tokens = self.model_spec.max_tokens
        if max_tokens is not None:
            max_tokens_arg = cast(str, self.model_spec.max_tokens_arg)
            generate_kw[max_tokens_arg] = max_tokens

        return generate_kw

    @cached_property
    def model(self) -> Any:
        """Load and get the configured MLX-Audio model.

        Returns:
            loaded MLX-Audio model
        Raises:
            RuntimeError: if MLX-Audio is unsupported on the current platform
        """
        system = platform.system()
        machine = platform.machine()
        if system != "Darwin" or machine != "arm64":
            raise RuntimeError(
                "MLX-Audio support requires macOS on Apple Silicon "
                f"(detected platform.system()={system!r}, "
                f"platform.machine()={machine!r}). CUDA support is not included."
            )

        load = import_mlx_audio_stt_load()
        model_dir_path = get_huggingface_snapshot_dir_path(
            self.model_spec.name, self.model_spec.revision
        )
        tokenizer = self.model_spec.tokenizer
        if tokenizer is None:
            return load(model_dir_path, model_type=self.model_spec.model_type)

        tokenizer_dir_path = get_huggingface_snapshot_dir_path(
            tokenizer.name, tokenizer.revision
        )
        with use_local_tokenizer(tokenizer, tokenizer_dir_path):
            return load(model_dir_path, model_type=self.model_spec.model_type)
