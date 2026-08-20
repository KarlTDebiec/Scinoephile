#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Direct MLX-Audio speech recognition."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from functools import cached_property
from pathlib import Path
from threading import Lock
from typing import ClassVar, Protocol, cast

from scinoephile.core.dependencies.transcription import (
    import_mlx_audio_mimo_asr,
    import_mlx_audio_stt_load,
)
from scinoephile.core.language import Language
from scinoephile.core.ml import get_huggingface_snapshot_dir_path

from .model import MlxAudioModelSpec

__all__ = ["MlxAudioInferenceResult", "MlxAudioRecognizer"]


class MlxAudioInferenceResult(Protocol):
    """Structural type returned by MLX-Audio inference."""

    text: str
    """Transcript text."""

    generation_tokens: int
    """Number of generated text tokens."""


class MlxAudioRecognizer:
    """Runs direct speech-to-text inference through one MLX-Audio model."""

    _model_load_lock: ClassVar[Lock] = Lock()
    """Lock protecting model loading and resolver replacement."""

    def __init__(
        self, model: MlxAudioModelSpec, language: Language = Language.yue_hant
    ):
        """Initialize.

        Arguments:
            model: MLX-Audio model specification
            language: language to transcribe
        Raises:
            ValueError: if the model does not support the language
        """
        self.model = model
        """Selected MLX-Audio model specification."""

        if language not in self.model.languages:
            raise ValueError(
                f"{language} is not supported by MLX-Audio "
                f"{self.model.model_type} transcription"
            )
        self.language = language
        """Language to transcribe."""

        self._generate_instance: Callable[..., MlxAudioInferenceResult] | None = None
        """Loaded MLX-Audio model's bound generation method."""

    def transcribe(self, audio_path: Path) -> MlxAudioInferenceResult:
        """Transcribe one audio file using MLX-Audio.

        Arguments:
            audio_path: audio file to transcribe
        Returns:
            MLX-Audio inference result
        Raises:
            ImportError: if MLX-Audio is unavailable
        """
        return self._generate(str(audio_path), **self._generate_kwargs)

    @property
    def _generate(self) -> Callable[..., MlxAudioInferenceResult]:
        """Get the loaded MLX-Audio model's bound generation method.

        Returns:
            bound MLX-Audio generation method
        """
        generate = self._generate_instance
        if generate is not None:
            return generate

        with self._model_load_lock:
            generate = self._generate_instance
            if generate is None:
                load = import_mlx_audio_stt_load()
                load_kwargs: dict[str, object] = {"model_type": self.model.model_type}
                model_dir_path = get_huggingface_snapshot_dir_path(
                    self.model.name, self.model.revision
                )
                audio_tokenizer_dir_path = None
                tokenizer = self.model.tokenizer
                if tokenizer is not None:
                    audio_tokenizer_dir_path = get_huggingface_snapshot_dir_path(
                        tokenizer.name, tokenizer.revision
                    )
                with self._use_local_audio_tokenizer(audio_tokenizer_dir_path):
                    loaded_model = load(model_dir_path, **load_kwargs)
                generate = cast(
                    Callable[..., MlxAudioInferenceResult],
                    getattr(loaded_model, "generate"),
                )
                self._generate_instance = generate
        return generate

    @cached_property
    def _generate_kwargs(self) -> dict[str, object]:
        """Get model-specific keyword arguments for MLX-Audio generation.

        Returns:
            keyword arguments for the selected model's generate method
        """
        generate_kwargs: dict[str, object] = {}

        model_language = self.model.languages.get(self.language)
        if model_language is not None:
            generate_kwargs["language"] = model_language

        max_tokens = self.model.max_tokens
        if max_tokens is not None:
            max_tokens_arg = cast(str, self.model.max_tokens_arg)
            generate_kwargs[max_tokens_arg] = max_tokens

        return generate_kwargs

    @contextmanager
    def _use_local_audio_tokenizer(
        self, audio_tokenizer_dir_path: Path | None
    ) -> Iterator[None]:
        """Make MLX-Audio use a pre-resolved auxiliary tokenizer directory.

        Arguments:
            audio_tokenizer_dir_path: pinned local tokenizer directory, if required
        """
        if audio_tokenizer_dir_path is None:
            yield
            return

        tokenizer = self.model.tokenizer
        if tokenizer is None:
            raise RuntimeError("MLX-Audio tokenizer specification is missing.")

        # Keep MLX-Audio from resolving the manifest's mutable tokenizer remotely
        mimo_asr = import_mlx_audio_mimo_asr()
        get_model_path = cast(Callable[..., Path], mimo_asr.get_model_path)

        def get_local_model_path(
            path_or_hf_repo: str, *args: object, **kwargs: object
        ) -> Path:
            """Resolve the configured tokenizer locally and delegate other models."""
            if path_or_hf_repo == tokenizer.name:
                return audio_tokenizer_dir_path
            return get_model_path(path_or_hf_repo, *args, **kwargs)

        setattr(mimo_asr, "get_model_path", get_local_model_path)
        try:
            yield
        finally:
            setattr(mimo_asr, "get_model_path", get_model_path)
