#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLX-Audio speech-to-text backend."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType
from typing import ClassVar, Protocol, cast

from scinoephile.audio.transcription.exceptions import TranscriptionError
from scinoephile.common.validation import val_input_file_or_dir_path
from scinoephile.core.dependencies.transcription import import_mlx_audio_stt_load
from scinoephile.core.language import Language

__all__ = [
    "FIRERED_ASR2_MODEL",
    "GLM_ASR_MODEL",
    "MIMO_MODEL",
    "MlxAudioBackend",
    "MlxAudioInferenceResult",
    "MlxAudioModelProfile",
    "QWEN3_ASR_MODEL",
    "SENSEVOICE_MODEL",
]


@dataclass(frozen=True, slots=True)
class MlxAudioInferenceResult:
    """Result of direct MLX-Audio inference."""

    text: str
    """Transcript text."""

    generation_tokens: int | None = None
    """Number of generated text tokens, when reported by the model."""


@dataclass(frozen=True, slots=True)
class MlxAudioModelProfile:
    """Complete configuration for one MLX-Audio STT model."""

    model_name: str
    """Hugging Face model name or local model path."""
    family_name: str
    """Stable model-family name used in cache metadata."""
    mlx_audio_model_type: str
    """Model type passed to the MLX-Audio loader."""
    default_max_tokens: int | None
    """Default maximum generated tokens, or None for the model's native behavior."""
    generation_limit_parameter_name: str | None
    """MLX-Audio generation-limit parameter, or None when unsupported."""
    token_limit_guard_window_duration_seconds: float | None
    """Maximum guarded window duration, or None when no guard is required."""
    metadata_identifiers: tuple[str, ...]
    """Exact lower-case metadata values identifying the model family."""
    model_name_markers: tuple[str, ...]
    """Case-insensitive substrings identifying the model family."""
    languages: Mapping[Language, str | None]
    """Model-specific language values keyed by Scinoephile language."""

    def __post_init__(self):
        """Copy and freeze the model-specific language mapping."""
        object.__setattr__(self, "languages", MappingProxyType(dict(self.languages)))


FIRERED_ASR2_MODEL = MlxAudioModelProfile(
    model_name="mlx-community/FireRedASR2-AED-mlx",
    family_name="firered-asr2",
    mlx_audio_model_type="fireredasr2",
    default_max_tokens=None,
    generation_limit_parameter_name="max_len",
    token_limit_guard_window_duration_seconds=None,
    metadata_identifiers=("fireredasr2",),
    model_name_markers=("fireredasr2", "firered-asr2"),
    languages=dict.fromkeys(Language),
)
"""Default MLX FireRedASR2-AED model profile."""

GLM_ASR_MODEL = MlxAudioModelProfile(
    model_name="mlx-community/GLM-ASR-Nano-2512-8bit",
    family_name="glm-asr",
    mlx_audio_model_type="glm",
    default_max_tokens=128,
    generation_limit_parameter_name="max_tokens",
    token_limit_guard_window_duration_seconds=None,
    metadata_identifiers=("glm", "glmasr"),
    model_name_markers=("glm-asr", "glm_asr", "glmasr"),
    languages=dict.fromkeys(Language),
)
"""Default MLX GLM-ASR-Nano-2512 model profile."""

MIMO_MODEL = MlxAudioModelProfile(
    model_name="mlx-community/MiMo-V2.5-ASR-MLX",
    family_name="mimo",
    mlx_audio_model_type="mimo",
    default_max_tokens=256,
    generation_limit_parameter_name="max_tokens",
    token_limit_guard_window_duration_seconds=55.0,
    metadata_identifiers=("mimo", "mimov2asrforcausallm"),
    model_name_markers=("mimo-v2.5-asr", "mimov2asr"),
    languages={
        Language.eng: "en",
        Language.yue_hans: "zh",
        Language.yue_hant: "zh",
        Language.zho_hans: "zh",
        Language.zho_hant: "zh",
    },
)
"""Default MLX MiMo model profile."""

QWEN3_ASR_MODEL = MlxAudioModelProfile(
    model_name="mlx-community/Qwen3-ASR-0.6B-8bit",
    family_name="qwen3-asr",
    mlx_audio_model_type="qwen3_asr",
    default_max_tokens=8192,
    generation_limit_parameter_name="max_tokens",
    token_limit_guard_window_duration_seconds=None,
    metadata_identifiers=("qwen3_asr",),
    model_name_markers=("qwen3-asr", "qwen3_asr", "qwen3asr"),
    languages={
        Language.eng: "English",
        Language.yue_hans: "Cantonese",
        Language.yue_hant: "Cantonese",
        Language.zho_hans: "Chinese",
        Language.zho_hant: "Chinese",
    },
)
"""Default MLX Qwen3-ASR model profile."""

SENSEVOICE_MODEL = MlxAudioModelProfile(
    model_name="mlx-community/SenseVoiceSmall",
    family_name="sensevoice",
    mlx_audio_model_type="sensevoice",
    default_max_tokens=None,
    generation_limit_parameter_name=None,
    token_limit_guard_window_duration_seconds=None,
    metadata_identifiers=("sensevoice",),
    model_name_markers=("sensevoice",),
    languages={
        Language.eng: "en",
        Language.yue_hans: "yue",
        Language.yue_hant: "yue",
        Language.zho_hans: "zh",
        Language.zho_hant: "zh",
    },
)
"""Default MLX SenseVoiceSmall model profile."""

_MLX_AUDIO_MODELS = (
    FIRERED_ASR2_MODEL,
    GLM_ASR_MODEL,
    MIMO_MODEL,
    QWEN3_ASR_MODEL,
    SENSEVOICE_MODEL,
)
"""Supported MLX-Audio models."""


class _MlxAudioModel(Protocol):
    """Structural type for MLX-Audio models used by the backend."""

    def generate(self, audio: str, **kwargs: object) -> object:
        """Generate a transcript for one audio file."""


class MlxAudioBackend:
    """Runs direct speech-to-text inference through one MLX-Audio model."""

    _models_by_key: ClassVar[dict[tuple[str, str], _MlxAudioModel]] = {}
    """Loaded models shared by resolved reference and MLX-Audio model type."""

    def __init__(
        self,
        model_name: str | MlxAudioModelProfile = MIMO_MODEL,
        language: Language = Language.yue_hant,
    ):
        """Initialize.

        Arguments:
            model_name: model profile, supported model name, or local model path
            language: language to transcribe
        Raises:
            TranscriptionError: if the model family has not been integrated and tested
            ValueError: if the model family does not support the language
        """
        if isinstance(model_name, MlxAudioModelProfile):
            model_profile = model_name
        else:
            model_profile = _get_mlx_audio_model_profile(model_name)
            model_profile = replace(model_profile, model_name=model_name)
        self.model_profile = model_profile
        """Complete configuration for the selected MLX-Audio model."""

        # Convert the Scinoephile language to the selected model's value
        try:
            self.language = language
            self.mlx_audio_language = self.model_profile.languages[language]
        except KeyError as exc:
            raise ValueError(
                f"{language} is not supported by MLX-Audio "
                f"{self.model_profile.family_name} transcription"
            ) from exc

        # Resolve local paths while preserving remote Hugging Face references
        selected_model_name = self.model_profile.model_name
        model_reference: str | Path = selected_model_name
        model_path = Path(selected_model_name).expanduser()
        if model_path.exists() or selected_model_name.startswith(("/", ".", "~")):
            model_reference = val_input_file_or_dir_path(selected_model_name)
        self._model_reference = model_reference
        """Resolved local model path or remote Hugging Face reference."""

        self._model: _MlxAudioModel | None = None
        """Loaded MLX-Audio model."""

    def transcribe(
        self, audio_path: Path, max_tokens: int | None = None
    ) -> MlxAudioInferenceResult:
        """Transcribe one audio file using MLX-Audio.

        Arguments:
            audio_path: audio file to transcribe
            max_tokens: optional maximum number of text tokens to generate
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
            if max_tokens <= 0:
                raise ValueError("MLX-Audio max tokens must be positive.")
            generation_limit_parameter_name = (
                self.model_profile.generation_limit_parameter_name
            )
            if generation_limit_parameter_name is None:
                raise ValueError(
                    f"MLX-Audio {self.model_profile.family_name} does not support a "
                    "generation token limit."
                )
            generate_kwargs[generation_limit_parameter_name] = max_tokens
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
    def _loaded_model(self) -> _MlxAudioModel:
        """Get the cached MLX-Audio model, loading it if needed.

        Returns:
            loaded MLX-Audio model
        """
        if self._model is not None:
            return self._model

        model_key = (
            str(self._model_reference),
            self.model_profile.mlx_audio_model_type,
        )

        # Reuse the process-wide model cache across inference instances
        cached_model = self._models_by_key.get(model_key)
        if cached_model is None:
            load = import_mlx_audio_stt_load()
            cached_model = cast(
                _MlxAudioModel,
                load(
                    self._model_reference,
                    model_type=self.model_profile.mlx_audio_model_type,
                ),
            )
            self._models_by_key[model_key] = cached_model
        self._model = cached_model
        return self._model


def _get_mlx_audio_model_metadata_identifiers(model_name: str) -> tuple[str, ...]:
    """Get exact identity values from local MLX-Audio model metadata.

    Arguments:
        model_name: local model path
    Returns:
        lower-case model identity values
    """
    model_path = Path(model_name).expanduser()
    if not model_path.exists():
        return ()

    if model_path.is_dir():
        metadata_paths = (model_path / "config.json", model_path / "mlx_manifest.json")
    elif model_path.suffix.lower() == ".json":
        metadata_paths = (model_path,)
    else:
        metadata_paths = ()

    identifiers = []
    for metadata_path in metadata_paths:
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            continue
        if not isinstance(metadata, Mapping):
            continue
        for key in ("model_type", "model", "architectures", "source_model_dir"):
            value = metadata.get(key)
            if isinstance(value, str):
                identifiers.append(value.lower())
            elif isinstance(value, Sequence):
                identifiers.extend(
                    item.lower() for item in value if isinstance(item, str)
                )

    return tuple(identifiers)


def _get_mlx_audio_model_profile(model_name: str) -> MlxAudioModelProfile:
    """Get the supported model profile matching an MLX-Audio model name.

    Arguments:
        model_name: Hugging Face model identifier or local model path
    Returns:
        matching model profile
    Raises:
        TranscriptionError: if the model family has not been integrated
            and tested
    """
    metadata_identifiers = _get_mlx_audio_model_metadata_identifiers(model_name)
    for model in _MLX_AUDIO_MODELS:
        if any(
            identifier in model.metadata_identifiers
            for identifier in metadata_identifiers
        ):
            return model

    model_path = Path(model_name).expanduser()
    if model_path.exists():
        model_name_parts = [model_path.name.lower()]
    else:
        model_name_parts = [model_name.rpartition("/")[2].lower()]
    model_name_parts.extend(
        identifier.replace("\\", "/").rpartition("/")[2]
        for identifier in metadata_identifiers
    )
    model_name_identity = " ".join(model_name_parts)
    for model in _MLX_AUDIO_MODELS:
        if any(marker in model_name_identity for marker in model.model_name_markers):
            return model
    supported_families = ", ".join(model.family_name for model in _MLX_AUDIO_MODELS)
    raise TranscriptionError(
        f"Unsupported MLX-Audio model {model_name!r}; supported families: "
        f"{supported_families}."
    )
