#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Future-extensible ASR source registry for aligned transcription."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from scinoephile.analysis.transcription_alignment import TranscriptionAlignmentSource
from scinoephile.audio.transcription import (
    DemucsMode,
    MlxAudioTranscriber,
    Transcriber,
    VADMode,
    WhisperTranscriber,
)
from scinoephile.audio.transcription.mlx_audio.backend import (
    FIRERED_ASR2_MODEL_NAME,
    GLM_ASR_MODEL_NAME,
    MIMO_MODEL_NAME,
    QWEN3_ASR_MODEL_NAME,
    SENSEVOICE_MODEL_NAME,
)
from scinoephile.core import Language, ScinoephileError

__all__ = ["TranscriptionSourceSpec", "get_transcription_sources"]

_MLX_AUDIO_CHUNK_DURATION_SECONDS = 30.0
"""Core MLX-Audio chunk duration used for block transcription."""


@dataclass(frozen=True, slots=True, kw_only=True)
class TranscriptionSourceSpec:
    """Configuration for one equal-status ASR source."""

    name: str
    """Stable source name used in alignment rows and artifacts."""
    backend: str
    """Backend implementation identifier."""
    model: str
    """Backend-specific model identifier."""

    def __post_init__(self):
        """Validate source identity."""
        if not self.name.strip():
            raise ValueError("Transcription source name must be nonblank.")
        if not self.backend.strip():
            raise ValueError("Transcription source backend must be nonblank.")
        if not self.model.strip():
            raise ValueError("Transcription source model must be nonblank.")


_YUE_SOURCE_SPECS = (
    TranscriptionSourceSpec(
        name="whisper", backend="whisper", model="khleeloo/whisper-large-v3-cantonese"
    ),
    TranscriptionSourceSpec(name="mimo", backend="mlx-audio", model=MIMO_MODEL_NAME),
    TranscriptionSourceSpec(
        name="qwen", backend="mlx-audio", model=QWEN3_ASR_MODEL_NAME
    ),
    TranscriptionSourceSpec(
        name="sensevoice", backend="mlx-audio", model=SENSEVOICE_MODEL_NAME
    ),
    TranscriptionSourceSpec(
        name="firered", backend="mlx-audio", model=FIRERED_ASR2_MODEL_NAME
    ),
    TranscriptionSourceSpec(name="glm", backend="mlx-audio", model=GLM_ASR_MODEL_NAME),
)
"""Default equal-status Cantonese ASR source registry."""

_DEFAULT_SOURCE_SPECS: Mapping[Language, tuple[TranscriptionSourceSpec, ...]] = (
    MappingProxyType(
        {Language.yue_hans: _YUE_SOURCE_SPECS, Language.yue_hant: _YUE_SOURCE_SPECS}
    )
)
"""Default source registries keyed by transcription language."""


def get_transcription_sources(
    language: Language,
    *,
    source_specs: tuple[TranscriptionSourceSpec, ...] | None = None,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
) -> tuple[dict[str, Transcriber], tuple[TranscriptionAlignmentSource, ...]]:
    """Construct configured ASR sources and portable source descriptors.

    All sources receive the complete VAD-planned audio block without internal
    VAD segmentation. Add another source by registering a stable source spec and
    adding its backend construction branch here.

    Arguments:
        language: transcription and output language
        source_specs: optional source registry override
        demucs_mode: source-level vocal-separation mode
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching generated cache files
    Returns:
        named source transcribers and matching portable descriptors
    Raises:
        ScinoephileError: if the language or a backend is unsupported
        ValueError: if fewer than two unique sources are configured
    """
    if source_specs is None:
        try:
            source_specs = _DEFAULT_SOURCE_SPECS[language]
        except KeyError as exc:
            raise ScinoephileError(
                f"Aligned transcription does not support language {language.code}."
            ) from exc
    if len(source_specs) < 2:
        raise ValueError("Aligned transcription requires at least two ASR sources.")
    if len({source.name for source in source_specs}) != len(source_specs):
        raise ValueError("Transcription source names must be unique.")

    transcribers: dict[str, Transcriber] = {}
    descriptors = []
    for source in source_specs:
        if source.backend == "whisper":
            transcriber = WhisperTranscriber(
                model_name=source.model,
                language="yue",
                demucs_mode=demucs_mode,
                vad_mode=VADMode.OFF,
                cache_root_path=cache_root_path,
                overwrite_cache=overwrite_cache,
            )
        elif source.backend == "mlx-audio":
            transcriber = MlxAudioTranscriber(
                model_name=source.model,
                language=language,
                chunk_duration_seconds=_MLX_AUDIO_CHUNK_DURATION_SECONDS,
                token_limit_guard=source.model == MIMO_MODEL_NAME,
                demucs_mode=demucs_mode,
                vad_mode=VADMode.OFF,
                cache_root_path=cache_root_path,
                overwrite_cache=overwrite_cache,
            )
        else:
            raise ScinoephileError(
                f"Unsupported transcription source backend {source.backend!r}."
            )
        transcribers[source.name] = transcriber
        descriptors.append(
            TranscriptionAlignmentSource(
                name=source.name, backend=source.backend, model=source.model
            )
        )
    return transcribers, tuple(descriptors)
