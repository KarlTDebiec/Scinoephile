#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Executable MLX-Audio speech-to-text model."""

from __future__ import annotations

import platform
from collections.abc import Callable
from functools import cached_property
from pathlib import Path
from typing import cast

from scinoephile.core.dependencies.transcription import import_mlx_audio_stt_load
from scinoephile.core.language import Language
from scinoephile.core.ml import get_huggingface_snapshot_dir_path

from .model_spec import MlxAudioModelSpec
from .tokenization import use_local_tokenizer
from .types import MlxAudioResult, MlxAudioRuntimeModel

__all__ = ["MlxAudioModel", "MlxAudioResult"]


class MlxAudioModel:
    """Configured executable MLX-Audio speech-to-text model."""

    def __init__(self, spec: MlxAudioModelSpec, language: Language):
        """Initialize.

        Arguments:
            spec: MLX-Audio model specification
            language: language to transcribe
        Raises:
            ValueError: if the model does not support the language
        """
        self.spec = spec
        """Selected MLX-Audio model specification."""

        if language not in self.spec.languages:
            raise ValueError(
                f"{language} is not supported by MLX-Audio "
                f"{self.spec.model_type} transcription"
            )

        self.generate_kw: dict[str, object] = {}
        """Model-specific keyword arguments for MLX-Audio generation."""
        model_language = self.spec.languages[language]
        if model_language is not None:
            self.generate_kw["language"] = model_language

        max_tokens = self.spec.max_tokens
        if max_tokens is not None:
            max_tokens_arg = cast(str, self.spec.max_tokens_arg)
            self.generate_kw[max_tokens_arg] = max_tokens

    def __call__(self, audio_path: Path) -> MlxAudioResult:
        """Recognize speech in one audio file using MLX-Audio.

        Arguments:
            audio_path: audio file to transcribe
        Returns:
            MLX-Audio recognition result
        Raises:
            DependencyError: if MLX-Audio is unavailable
        """
        return self.model.generate(str(audio_path), **self.generate_kw)

    @cached_property
    def model(self) -> MlxAudioRuntimeModel:
        """Load and get the configured MLX-Audio model.

        Returns:
            loaded MLX-Audio model
        Raises:
            DependencyError: if MLX-Audio is unavailable
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

        load = cast(Callable[..., MlxAudioRuntimeModel], import_mlx_audio_stt_load())
        model_dir_path = get_huggingface_snapshot_dir_path(
            self.spec.name, self.spec.revision
        )
        tokenizer = self.spec.tokenizer
        if tokenizer is None:
            return load(model_dir_path, model_type=self.spec.model_type)

        tokenizer_dir_path = get_huggingface_snapshot_dir_path(
            tokenizer.name, tokenizer.revision
        )
        with use_local_tokenizer(tokenizer, tokenizer_dir_path):
            return load(model_dir_path, model_type=self.spec.model_type)
