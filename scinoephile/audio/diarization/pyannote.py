#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Local speaker diarization using pyannote Community-1."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from functools import cached_property
from importlib.metadata import PackageNotFoundError, version
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, cast

import numpy as np

from scinoephile.audio.waveform import to_mono_int16
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.dependencies.transcription import (
    import_pyannote_audio,
    import_torch,
)
from scinoephile.core.exceptions import DependencyError
from scinoephile.core.ml import get_huggingface_snapshot_dir_path, get_torch_device

from .cache import SpeakerDiarizationCache
from .exceptions import (
    SpeakerDiarizationAuthorizationError,
    SpeakerDiarizationInferenceError,
)
from .models import SpeakerDiarizationResult, SpeakerTurn

__all__ = ["PyannoteDiarizer"]

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)

_DEFAULT_MODEL_ID = "pyannote/speaker-diarization-community-1"
"""Default speaker diarization pipeline."""
_DEFAULT_MODEL_REVISION = "3533c8cf8e369892e6b79ff1bf80f7b0286a54ee"
"""Pinned Hugging Face revision of the default pipeline and its model assets."""
_WAVEFORM_CHANNELS = 1
"""Channels supplied to pyannote inference."""
_WAVEFORM_FRAME_RATE = 16_000
"""Sample rate supplied to pyannote inference."""
_WAVEFORM_SAMPLE_WIDTH = 2
"""PCM sample width supplied to pyannote inference."""


class PyannoteDiarizer:
    """Run and cache local source-wide speaker diarization."""

    def __init__(
        self,
        cache_root_path: Path | None,
        *,
        model_id: str = _DEFAULT_MODEL_ID,
        model_revision: str | None = None,
        device: str | None = None,
        num_speakers: int | None = None,
        min_speakers: int | None = None,
        max_speakers: int | None = None,
        overwrite_cache: bool = False,
    ):
        """Initialize.

        Hugging Face credentials are resolved by the Hub from its normal local
        configuration or environment variables and are never stored by Scinoephile.

        Arguments:
            cache_root_path: root directory beneath which to cache
            model_id: Hugging Face pipeline identifier
            model_revision: exact Hugging Face model revision; None selects the
                pinned Community-1 revision or a custom repository's default
            device: Torch device, or None to select the available accelerator
            num_speakers: exact source-wide speaker count, when known
            min_speakers: minimum source-wide speaker count, when known
            max_speakers: maximum source-wide speaker count, when known
            overwrite_cache: whether to replace a matching cache entry
        Raises:
            ValueError: if speaker-count constraints are invalid
        """
        if num_speakers is not None and num_speakers < 1:
            raise ValueError("Speaker count must be positive.")
        if min_speakers is not None and min_speakers < 1:
            raise ValueError("Minimum speaker count must be positive.")
        if max_speakers is not None and max_speakers < 1:
            raise ValueError("Maximum speaker count must be positive.")
        if num_speakers is not None and (
            min_speakers is not None or max_speakers is not None
        ):
            raise ValueError(
                "Exact speaker count cannot be combined with minimum or maximum count."
            )
        if (
            min_speakers is not None
            and max_speakers is not None
            and min_speakers > max_speakers
        ):
            raise ValueError("Minimum speaker count cannot exceed maximum count.")

        self.model_id = model_id
        """Hugging Face pipeline identifier."""
        if model_revision is None and model_id == _DEFAULT_MODEL_ID:
            model_revision = _DEFAULT_MODEL_REVISION
        self.model_revision = model_revision
        """Exact Hugging Face pipeline and model-asset revision, or None."""
        self._device = device
        """Explicit Torch device, or None to select one lazily."""
        self.num_speakers = num_speakers
        """Exact source-wide speaker count, when known."""
        self.min_speakers = min_speakers
        """Minimum source-wide speaker count, when known."""
        self.max_speakers = max_speakers
        """Maximum source-wide speaker count, when known."""
        self._cache = SpeakerDiarizationCache(cache_root_path, overwrite_cache)
        """Source-wide diarization cache."""
        self._pipeline: object | None = None
        """Lazily loaded pyannote pipeline."""

    @cached_property
    def device(self) -> str:
        """Get the Torch device used for local inference.

        Returns:
            configured or automatically selected Torch device
        Raises:
            DependencyError: if Torch is unavailable
        """
        if self._device is None:
            self._device = get_torch_device()
        return self._device

    def __call__(self, audio: AudioSegment) -> SpeakerDiarizationResult:
        """Diarize complete source audio.

        Arguments:
            audio: complete source audio
        Returns:
            regular and exclusive source-timeline speaker turns
        Raises:
            SpeakerDiarizationAuthorizationError: if model access is not authorized
            DependencyError: if optional dependencies are missing
            SpeakerDiarizationInferenceError: if loading or inference fails
        """
        cache_identity = self.cache_identity
        cached_result = self._cache.load(audio, cache_identity)
        if cached_result is not None:
            return cached_result

        logger.info(f"Running pyannote speaker diarization on {self.device}.")
        pipeline = self._get_pipeline()
        torch = import_torch()
        try:
            samples = to_mono_int16(audio, _WAVEFORM_FRAME_RATE)
            waveform = samples.reshape(1, -1).astype(np.float32)
            waveform /= float(1 << (8 * _WAVEFORM_SAMPLE_WIDTH - 1))
            audio_input = {
                "waveform": torch.from_numpy(waveform),
                "sample_rate": _WAVEFORM_FRAME_RATE,
            }
            kwargs = {
                name: value
                for name, value in (
                    ("num_speakers", self.num_speakers),
                    ("min_speakers", self.min_speakers),
                    ("max_speakers", self.max_speakers),
                )
                if value is not None
            }
            run_pipeline = cast(Callable[..., object], pipeline)
            output = run_pipeline(audio_input, **kwargs)
            result = SpeakerDiarizationResult(
                turns=self._convert_annotation(
                    getattr(output, "speaker_diarization", None), "regular"
                ),
                exclusive_turns=self._convert_annotation(
                    getattr(output, "exclusive_speaker_diarization", None), "exclusive"
                ),
            )
        except SpeakerDiarizationInferenceError:
            raise
        except Exception as exc:
            raise SpeakerDiarizationInferenceError(
                f"pyannote speaker diarization failed: {exc}"
            ) from exc

        self._cache.save(audio, cache_identity, result)
        return result

    @property
    def cache_identity(self) -> CacheIdentity:
        """Get the pipeline, runtime, and inference configuration identity.

        Returns:
            configuration identifying reusable diarization output
        Raises:
            DependencyError: if pyannote.audio or Torch is unavailable
        """
        try:
            pyannote_audio_version = version("pyannote.audio")
        except PackageNotFoundError as exc:
            raise DependencyError(
                "Speaker diarization requires pyannote.audio. Install Scinoephile "
                "with the 'transcription' extra."
            ) from exc
        return {
            "device": self.device,
            "max_speakers": self.max_speakers,
            "min_speakers": self.min_speakers,
            "model": self.model_id,
            "model_revision": self.model_revision,
            "num_speakers": self.num_speakers,
            "runtime": {
                "distribution": "pyannote.audio",
                "version": pyannote_audio_version,
            },
            "waveform_channels": _WAVEFORM_CHANNELS,
            "waveform_frame_rate": _WAVEFORM_FRAME_RATE,
            "waveform_sample_width": _WAVEFORM_SAMPLE_WIDTH,
        }

    def _get_pipeline(self) -> object:
        """Lazily load and place the configured pyannote pipeline.

        Returns:
            configured pyannote pipeline
        Raises:
            SpeakerDiarizationAuthorizationError: if model access is not authorized
            DependencyError: if optional dependencies are missing
            SpeakerDiarizationInferenceError: if pipeline loading fails
        """
        if self._pipeline is not None:
            return self._pipeline
        try:
            pyannote_audio = import_pyannote_audio()
            pipeline_cls = getattr(pyannote_audio, "Pipeline")
            from_pretrained = getattr(pipeline_cls, "from_pretrained")
            model_dir_path = get_huggingface_snapshot_dir_path(
                self.model_id, self.model_revision
            )
            pipeline = from_pretrained(model_dir_path)
            if pipeline is None:
                raise SpeakerDiarizationAuthorizationError(
                    f"Unable to load gated pyannote model {self.model_id!r}. Accept "
                    "its Hugging Face conditions and configure a Hugging Face token."
                )
            torch = import_torch()
            pipeline.to(torch.device(self.device))
        except (DependencyError, SpeakerDiarizationAuthorizationError):
            raise
        except Exception as exc:
            exception_name = type(exc).__name__
            message = str(exc).casefold()
            if exception_name in {
                "GatedRepoError",
                "RepositoryNotFoundError",
                "UnauthorizedError",
            } or any(token in message for token in ("401", "403", "gated repo")):
                raise SpeakerDiarizationAuthorizationError(
                    f"Hugging Face has not authorized pyannote model "
                    f"{self.model_id!r}. Accept its conditions and configure a token."
                ) from exc
            raise SpeakerDiarizationInferenceError(
                f"Unable to load pyannote speaker diarization: {exc}"
            ) from exc
        self._pipeline = pipeline
        return pipeline

    @staticmethod
    def _convert_annotation(annotation: object, name: str) -> list[SpeakerTurn]:
        """Convert one pyannote Annotation into typed source-timeline turns.

        Arguments:
            annotation: pyannote annotation-like object
            name: timeline name used in errors
        Returns:
            sorted speaker turns
        Raises:
            SpeakerDiarizationInferenceError: if the annotation is malformed
        """
        itertracks = getattr(annotation, "itertracks", None)
        if not callable(itertracks):
            raise SpeakerDiarizationInferenceError(
                f"pyannote returned no usable {name} speaker diarization."
            )
        try:
            raw_turns = cast(
                Iterator[tuple[object, object, object]], itertracks(yield_label=True)
            )
            turns = [
                SpeakerTurn(
                    start=float(getattr(segment, "start")),
                    end=float(getattr(segment, "end")),
                    speaker=str(speaker),
                )
                for segment, _, speaker in raw_turns
            ]
        except (AttributeError, TypeError, ValueError) as exc:
            raise SpeakerDiarizationInferenceError(
                f"pyannote returned malformed {name} speaker diarization: {exc}"
            ) from exc
        return sorted(turns, key=lambda turn: (turn.start, turn.end, turn.speaker))
