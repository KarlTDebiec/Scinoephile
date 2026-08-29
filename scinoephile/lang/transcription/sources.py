#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Registry and factory for multi-source audio transcription."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from scinoephile.analysis.transcription.artifact import AlignmentSource
from scinoephile.audio.transcription import (
    CtcAligner,
    DemucsMode,
    MlxAudioModel,
    MlxAudioTranscriber,
    Transcriber,
    VadMode,
    WhisperModel,
    WhisperTranscriber,
)
from scinoephile.audio.transcription.mlx_audio.model_spec import (
    FIRERED_ASR2_MODEL,
    GLM_ASR_MODEL,
    MIMO_MODEL,
    QWEN3_ASR_MODEL,
    SENSEVOICE_MODEL,
    MlxAudioModelSpec,
)
from scinoephile.audio.transcription.whisper.model_spec import (
    WHISPER_LARGE_V3_CANTONESE_MODEL,
    WhisperModelSpec,
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
    spec: WhisperModelSpec | MlxAudioModelSpec
    """Speech-to-text model specification."""

    def __post_init__(self):
        """Normalize and validate the source name."""
        name = self.name.strip()
        if not name:
            raise ValueError("Transcription source name must be nonblank.")
        object.__setattr__(self, "name", name)


_YUE_SOURCE_SPECS = (
    TranscriptionSourceSpec(name="whisper", spec=WHISPER_LARGE_V3_CANTONESE_MODEL),
    TranscriptionSourceSpec(name="mimo", spec=MIMO_MODEL),
    TranscriptionSourceSpec(name="qwen", spec=QWEN3_ASR_MODEL),
    TranscriptionSourceSpec(name="sensevoice", spec=SENSEVOICE_MODEL),
    TranscriptionSourceSpec(name="firered", spec=FIRERED_ASR2_MODEL),
    TranscriptionSourceSpec(name="glm", spec=GLM_ASR_MODEL),
)
"""Default equal-status Cantonese ASR sources."""

_DEFAULT_SOURCE_SPECS: Mapping[Language, tuple[TranscriptionSourceSpec, ...]] = (
    MappingProxyType(
        {Language.yue_hans: _YUE_SOURCE_SPECS, Language.yue_hant: _YUE_SOURCE_SPECS}
    )
)
"""Default source registries keyed by transcription language."""


def get_transcription_sources(
    language: Language,
    *,
    source_specs: Sequence[TranscriptionSourceSpec] | None = None,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
) -> tuple[dict[str, Transcriber], tuple[AlignmentSource, ...]]:
    """Construct configured ASR sources and portable source descriptors.

    All sources receive the complete VAD-planned audio block without internal
    VAD segmentation.

    Arguments:
        language: transcription and output language
        source_specs: optional source registry override
        demucs_mode: source-level vocal-separation mode
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching generated cache files
    Returns:
        named source transcribers and matching portable descriptors
    Raises:
        ScinoephileError: if the language or a model type is unsupported
        ValueError: if fewer than two unique sources are configured
    """
    if source_specs is None:
        try:
            source_specs = _DEFAULT_SOURCE_SPECS[language]
        except KeyError as exc:
            raise ScinoephileError(
                f"Multi-source transcription does not support {language.code}."
            ) from exc
    if len(source_specs) < 2:
        raise ValueError("Multi-source transcription requires at least two sources.")
    if len({source.name for source in source_specs}) != len(source_specs):
        raise ValueError("Transcription source names must be unique.")

    transcribers: dict[str, Transcriber] = {}
    descriptors = []
    for source in source_specs:
        model_name = source.spec.name
        if language not in source.spec.languages:
            raise ScinoephileError(
                f"Transcription source {source.name!r} model "
                f"{model_name!r} does not support {language.code}."
            )
        if isinstance(source.spec, WhisperModelSpec):
            transcriber = WhisperTranscriber(
                model=WhisperModel(source.spec, language),
                language=language,
                demucs_mode=demucs_mode,
                vad_mode=VadMode.OFF,
                cache_root_path=cache_root_path,
                overwrite_cache=overwrite_cache,
                recover_decoding=True,
            )
            backend_name = WhisperTranscriber.backend_name
        elif isinstance(source.spec, MlxAudioModelSpec):
            transcriber = MlxAudioTranscriber(
                model=MlxAudioModel(source.spec, language),
                ctc_aligner=CtcAligner(
                    language,
                    cache_root_path=cache_root_path,
                    overwrite_cache=overwrite_cache,
                ),
                language=language,
                chunk_duration_seconds=_MLX_AUDIO_CHUNK_DURATION_SECONDS,
                demucs_mode=demucs_mode,
                vad_mode=VadMode.OFF,
                cache_root_path=cache_root_path,
                overwrite_cache=overwrite_cache,
            )
            backend_name = MlxAudioTranscriber.backend_name
        else:
            raise ScinoephileError(
                f"Unsupported transcription source model {type(source.spec).__name__}."
            )
        transcribers[source.name] = transcriber
        descriptors.append(
            AlignmentSource(name=source.name, backend=backend_name, model=model_name)
        )
    return transcribers, tuple(descriptors)
