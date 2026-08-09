#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLX-Audio speech-to-text backend."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Protocol, cast

from scinoephile.common.validation import val_input_file_or_dir_path
from scinoephile.core.dependencies.transcription import import_mlx_audio_stt_load
from scinoephile.core.language import Language

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

    _models_by_key: ClassVar[dict[tuple[str, str], _LoadedMlxAudioModel]] = {}
    """Loaded models shared by resolved reference and MLX-Audio model type."""

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

        self._loaded_model_instance: _LoadedMlxAudioModel | None = None
        """Loaded MLX-Audio model."""

    def transcribe(
        self, audio_path: Path, max_tokens: int | None = None
    ) -> MlxAudioInferenceResult:
        """Transcribe one audio file using MLX-Audio.

        Arguments:
            audio_path: audio file to transcribe
            max_tokens: optional override for the model's generation limit
        Returns:
            normalized inference result
        Raises:
            ImportError: if MLX-Audio is unavailable
            ValueError: if the limit is invalid or the model returns malformed output
        """
        generate_kwargs: dict[str, object] = {}
        if self.mlx_audio_language is not None:
            generate_kwargs["language"] = self.mlx_audio_language
        max_tokens = self.model.get_max_tokens(max_tokens)
        if max_tokens is not None:
            max_tokens_argument = self.model.max_tokens_argument
            assert max_tokens_argument is not None
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

    @property
    def _loaded_model(self) -> _LoadedMlxAudioModel:
        """Get the cached MLX-Audio model, loading it if needed.

        Returns:
            loaded MLX-Audio model
        """
        if self._loaded_model_instance is not None:
            return self._loaded_model_instance

        model_key = (str(self._model_reference), self.model.model_type)

        # Reuse the process-wide model cache across inference instances
        cached_model = self._models_by_key.get(model_key)
        if cached_model is None:
            load = import_mlx_audio_stt_load()
            cached_model = cast(
                _LoadedMlxAudioModel,
                load(self._model_reference, model_type=self.model.model_type),
            )
            self._models_by_key[model_key] = cached_model
        self._loaded_model_instance = cached_model
        return self._loaded_model_instance
