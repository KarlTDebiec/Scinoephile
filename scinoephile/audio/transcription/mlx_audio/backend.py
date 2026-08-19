#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLX-Audio speech-to-text backend."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import ClassVar, Protocol, cast

from scinoephile.common.validation import val_input_file_or_dir_path
from scinoephile.core.dependencies.transcription import (
    import_mlx_audio_mimo_asr,
    import_mlx_audio_stt_load,
)
from scinoephile.core.language import Language
from scinoephile.core.ml import get_huggingface_snapshot_dir_path

from .model import MIMO_MODEL, MlxAudioModel

__all__ = ["MlxAudioBackend", "MlxAudioInferenceResult"]


@dataclass(frozen=True, slots=True)
class MlxAudioInferenceResult:
    """Result of direct MLX-Audio inference."""

    text: str
    """Transcript text."""

    generation_tokens: int | None = None
    """Number of generated text tokens, when reported by the model."""


class _LoadedMlxAudioModel(Protocol):
    """Structural type for loaded MLX-Audio models used by the backend."""

    def generate(self, audio: str, **kwargs: object) -> object:
        """Generate a transcript for one audio file."""


class MlxAudioBackend:
    """Runs direct speech-to-text inference through one MLX-Audio model."""

    _models_by_key: ClassVar[
        dict[tuple[str, str | None, str, str | None, str | None], _LoadedMlxAudioModel]
    ] = {}
    """Loaded models shared by complete model identity."""
    _model_load_lock: ClassVar[Lock] = Lock()
    """Lock protecting process-wide model loading and resolver replacement."""

    def __init__(
        self, model: MlxAudioModel = MIMO_MODEL, language: Language = Language.yue_hant
    ):
        """Initialize.

        Arguments:
            model: MLX-Audio model
            language: language to transcribe
        Raises:
            ValueError: if the model family does not support the language
        """
        self.model = model
        """Selected MLX-Audio model."""

        # Convert the Scinoephile language to the selected model's value
        try:
            self.language = language
            self.mlx_audio_language = self.model.languages[language]
        except KeyError as exc:
            raise ValueError(
                f"{language} is not supported by MLX-Audio "
                f"{self.model.family_name} transcription"
            ) from exc

        # Resolve local paths while preserving remote Hugging Face references
        selected_model_name = self.model.model_name
        model_reference: str | Path = selected_model_name
        model_path = Path(selected_model_name).expanduser()
        if model_path.exists() or selected_model_name.startswith(("/", ".", "~")):
            model_reference = val_input_file_or_dir_path(selected_model_name)
        self._model_reference = model_reference
        """Resolved local model path or remote Hugging Face reference."""

        self.model_revision = (
            self.model.model_revision if isinstance(model_reference, str) else None
        )
        """Immutable remote model revision, or None for local models."""

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
            normalized inference result
        Raises:
            ImportError: if MLX-Audio is unavailable
            ValueError: if the limit is invalid or the model returns malformed output
        """
        generate_kwargs: dict[str, object] = {}
        if self.mlx_audio_language is not None:
            generate_kwargs["language"] = self.mlx_audio_language
        if max_tokens is not None:
            max_tokens_argument = self.model.max_tokens_argument
            if max_tokens_argument is None:
                raise ValueError(
                    f"MLX-Audio {self.model.family_name} does not support a "
                    "generation token limit."
                )
            generate_kwargs[max_tokens_argument] = max_tokens
        result = self._loaded_model.generate(str(audio_path), **generate_kwargs)

        # Normalize mapping- and attribute-based results
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

        return MlxAudioInferenceResult(text=text, generation_tokens=generation_tokens)

    def _get_model_reference(self) -> Path:
        """Resolve the configured model to a local directory.

        Returns:
            local model directory path
        """
        if isinstance(self._model_reference, Path):
            return self._model_reference
        return get_huggingface_snapshot_dir_path(
            self._model_reference, self.model_revision
        )

    def _get_audio_tokenizer_reference(self) -> Path | None:
        """Resolve a remote model's auxiliary audio tokenizer locally.

        Returns:
            pinned local audio-tokenizer directory, when configured
        """
        if (
            not isinstance(self._model_reference, str)
            or self.model.audio_tokenizer_model_name is None
        ):
            return None
        return get_huggingface_snapshot_dir_path(
            self.model.audio_tokenizer_model_name,
            self.model.audio_tokenizer_model_revision,
        )

    @contextmanager
    def _use_local_audio_tokenizer(
        self, audio_tokenizer_reference: Path | None
    ) -> Iterator[None]:
        """Make MLX-Audio use a pre-resolved auxiliary tokenizer directory.

        Arguments:
            audio_tokenizer_reference: pinned local tokenizer directory, if required
        """
        if audio_tokenizer_reference is None:
            yield
            return

        # MLX-Audio's MiMo hook otherwise resolves the manifest's mutable tokenizer
        # repository through Hugging Face even when the required files are cached.
        mimo_asr = import_mlx_audio_mimo_asr()
        get_model_path = cast(Callable[..., Path], mimo_asr.get_model_path)

        def get_local_model_path(
            path_or_hf_repo: str, *args: object, **kwargs: object
        ) -> Path:
            """Resolve the configured tokenizer locally and delegate other models."""
            if path_or_hf_repo == self.model.audio_tokenizer_model_name:
                return audio_tokenizer_reference
            return get_model_path(path_or_hf_repo, *args, **kwargs)

        setattr(mimo_asr, "get_model_path", get_local_model_path)
        try:
            yield
        finally:
            setattr(mimo_asr, "get_model_path", get_model_path)

    @property
    def _loaded_model(self) -> _LoadedMlxAudioModel:
        """Get the cached MLX-Audio model, loading it if needed.

        Returns:
            loaded MLX-Audio model
        """
        if self._loaded_model_instance is not None:
            return self._loaded_model_instance

        model_key = (
            str(self._model_reference),
            self.model_revision,
            self.model.model_type,
            self.model.audio_tokenizer_model_name,
            self.model.audio_tokenizer_model_revision,
        )

        # Reuse the process-wide model cache across inference instances
        with self._model_load_lock:
            cached_model = self._models_by_key.get(model_key)
            if cached_model is None:
                load = import_mlx_audio_stt_load()
                load_kwargs: dict[str, object] = {"model_type": self.model.model_type}
                model_reference = self._get_model_reference()
                audio_tokenizer_reference = self._get_audio_tokenizer_reference()
                with self._use_local_audio_tokenizer(audio_tokenizer_reference):
                    cached_model = cast(
                        _LoadedMlxAudioModel, load(model_reference, **load_kwargs)
                    )
                self._models_by_key[model_key] = cached_model
        self._loaded_model_instance = cached_model
        return self._loaded_model_instance
