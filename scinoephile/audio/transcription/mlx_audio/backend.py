#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLX-Audio speech-to-text backend."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import ClassVar, Protocol, cast

from scinoephile.core.dependencies.transcription import (
    import_mlx_audio_mimo_asr,
    import_mlx_audio_stt_load,
)
from scinoephile.core.language import Language
from scinoephile.core.ml import get_huggingface_snapshot_dir_path

from .model import MlxAudioModel

__all__ = ["MlxAudioBackend", "MlxAudioInferenceResult"]


class MlxAudioInferenceResult(Protocol):
    """Structural type returned by MLX-Audio inference."""

    text: str
    """Transcript text."""

    generation_tokens: int
    """Number of generated text tokens."""


class _LoadedMlxAudioModel(Protocol):
    """Structural type for loaded MLX-Audio models used by the backend."""

    def generate(self, audio: str, **kwargs: object) -> MlxAudioInferenceResult:
        """Generate a transcript for one audio file."""


class MlxAudioBackend:
    """Runs direct speech-to-text inference through one MLX-Audio model."""

    _model_load_lock: ClassVar[Lock] = Lock()
    """Lock protecting model loading and resolver replacement."""

    def __init__(self, model: MlxAudioModel, language: Language = Language.yue_hant):
        """Initialize.

        Arguments:
            model: MLX-Audio model
            language: language to transcribe
        """
        self.model = model
        """Selected MLX-Audio model."""

        self.language = language
        """Language to transcribe."""

        self._loaded_model_instance: _LoadedMlxAudioModel | None = None
        """Loaded MLX-Audio model."""

    def transcribe(
        self, audio_path: Path, max_tokens: int | None = None
    ) -> MlxAudioInferenceResult:
        """Transcribe one audio file using MLX-Audio.

        Arguments:
            audio_path: audio file to transcribe
            max_tokens: generation limit, or None to use native model behavior
        Returns:
            MLX-Audio inference result
        Raises:
            ImportError: if MLX-Audio is unavailable
            ValueError: if the language or generation limit is invalid
        """
        generate_kwargs = self._get_generate_kwargs(max_tokens)
        return self._loaded_model.generate(str(audio_path), **generate_kwargs)

    @property
    def _loaded_model(self) -> _LoadedMlxAudioModel:
        """Get this backend's MLX-Audio model, loading it if needed.

        Returns:
            loaded MLX-Audio model
        """
        loaded_model = self._loaded_model_instance
        if loaded_model is not None:
            return loaded_model

        with self._model_load_lock:
            loaded_model = self._loaded_model_instance
            if loaded_model is None:
                load = import_mlx_audio_stt_load()
                load_kwargs: dict[str, object] = {"model_type": self.model.model_type}
                model_dir_path = get_huggingface_snapshot_dir_path(
                    self.model.name, self.model.revision
                )
                audio_tokenizer_dir_path = None
                audio_tokenizer = self.model.audio_tokenizer
                if audio_tokenizer is not None:
                    audio_tokenizer_dir_path = get_huggingface_snapshot_dir_path(
                        audio_tokenizer.name, audio_tokenizer.revision
                    )
                with self._use_local_audio_tokenizer(audio_tokenizer_dir_path):
                    loaded_model = cast(
                        _LoadedMlxAudioModel, load(model_dir_path, **load_kwargs)
                    )
                self._loaded_model_instance = loaded_model
        return loaded_model

    def _get_generate_kwargs(self, max_tokens: int | None) -> dict[str, object]:
        """Get model-specific keyword arguments for MLX-Audio generation.

        Arguments:
            max_tokens: generation limit, or None to use native model behavior
        Returns:
            keyword arguments for the selected model's generate method
        Raises:
            ValueError: if the selected model does not support the language or a
                generation limit
        """
        generate_kwargs: dict[str, object] = {}
        try:
            model_language = self.model.languages[self.language]
        except KeyError as exc:
            raise ValueError(
                f"{self.language} is not supported by MLX-Audio "
                f"{self.model.model_type} transcription"
            ) from exc
        if model_language is not None:
            generate_kwargs["language"] = model_language
        if max_tokens is not None:
            max_tokens_argument = self.model.max_tokens_argument
            if max_tokens_argument is None:
                raise ValueError(
                    f"MLX-Audio {self.model.model_type} does not support a "
                    "generation token limit."
                )
            generate_kwargs[max_tokens_argument] = max_tokens
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

        audio_tokenizer = self.model.audio_tokenizer
        if audio_tokenizer is None:
            raise RuntimeError("MLX-Audio tokenizer model is missing.")

        # Keep MLX-Audio from resolving the manifest's mutable tokenizer remotely
        mimo_asr = import_mlx_audio_mimo_asr()
        get_model_path = cast(Callable[..., Path], mimo_asr.get_model_path)

        def get_local_model_path(
            path_or_hf_repo: str, *args: object, **kwargs: object
        ) -> Path:
            """Resolve the configured tokenizer locally and delegate other models."""
            if path_or_hf_repo == audio_tokenizer.name:
                return audio_tokenizer_dir_path
            return get_model_path(path_or_hf_repo, *args, **kwargs)

        setattr(mimo_asr, "get_model_path", get_local_model_path)
        try:
            yield
        finally:
            setattr(mimo_asr, "get_model_path", get_model_path)
