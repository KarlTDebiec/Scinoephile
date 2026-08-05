#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Local speaker diarization using pyannote speaker-diarization-3.0."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from importlib.metadata import PackageNotFoundError, version
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, cast

import numpy as np

from scinoephile.core.dependencies.transcription import (
    import_huggingface_hub,
    import_pyannote_audio,
    import_torch,
    import_yaml,
)

from .cache import SpeakerDiarizationCache
from .exceptions import (
    SpeakerDiarizationAuthorizationError,
    SpeakerDiarizationDependencyError,
    SpeakerDiarizationInferenceError,
)
from .models import SpeakerDiarizationResult, SpeakerTurn

__all__ = ["PyannoteDiarizer"]

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)

_DEFAULT_MODEL_ID = "pyannote/speaker-diarization-3.0"
"""Default speaker diarization pipeline selected for Scinoephile's data."""
_DEFAULT_MODEL_REVISION = "61bc5e801239695154ba03562a72e1d6254ed4e4"
"""Pinned Hugging Face revision of the default pipeline and model assets."""
_EMBEDDING_MODEL_ID = "hbredin/wespeaker-voxceleb-resnet34-LM"
"""Speaker embedding model referenced by the pinned 3.0 pipeline."""
_EMBEDDING_MODEL_REVISION = "0ae88dcaf48cacdf741275d6d1a8101f45eee220"
"""Pinned Hugging Face revision of the speaker embedding model."""
_PIPELINE_CLASS_NAME = "pyannote.audio.pipelines.SpeakerDiarization"
"""Pipeline implementation recorded in cache metadata."""
_PLDA_MODEL_ID = "pyannote/speaker-diarization-community-1"
"""Repository providing PLDA assets required by pyannote.audio 4."""
_PLDA_MODEL_REVISION = "3533c8cf8e369892e6b79ff1bf80f7b0286a54ee"
"""Pinned Hugging Face revision of the PLDA assets."""
_SEGMENTATION_MODEL_ID = "pyannote/segmentation-3.0"
"""Speaker segmentation model referenced by the pinned 3.0 pipeline."""
_SEGMENTATION_MODEL_REVISION = "e66f3d3b9eb0873085418a7b813d3b369bf160bb"
"""Pinned Hugging Face revision of the speaker segmentation model."""
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
        model_revision: str = _DEFAULT_MODEL_REVISION,
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
            model_revision: exact Hugging Face model revision
            device: Torch device, or None to use CPU
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
        if (
            min_speakers is not None
            and max_speakers is not None
            and min_speakers > max_speakers
        ):
            raise ValueError("Minimum speaker count cannot exceed maximum count.")

        self.model_id = model_id
        """Hugging Face pipeline identifier."""
        self.model_revision = model_revision
        """Exact Hugging Face pipeline and model-asset revision."""
        self.device = device or "cpu"
        """Torch device used for local inference."""
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

    def __call__(self, audio: AudioSegment) -> SpeakerDiarizationResult:
        """Diarize complete source audio.

        Arguments:
            audio: complete source audio
        Returns:
            regular and exclusive source-timeline speaker turns
        Raises:
            SpeakerDiarizationAuthorizationError: if model access is not authorized
            SpeakerDiarizationDependencyError: if optional dependencies are missing
            SpeakerDiarizationInferenceError: if loading or inference fails
        """
        metadata = self._get_cache_metadata()
        cached_result = self._cache.load(audio, metadata)
        if cached_result is not None:
            return cached_result

        pipeline = self._get_pipeline()
        try:
            torch = import_torch()
            inference_audio = (
                audio.set_channels(_WAVEFORM_CHANNELS)
                .set_frame_rate(_WAVEFORM_FRAME_RATE)
                .set_sample_width(_WAVEFORM_SAMPLE_WIDTH)
            )
            samples = np.asarray(inference_audio.get_array_of_samples())
            waveform = samples.reshape(-1, _WAVEFORM_CHANNELS).T.astype(np.float32)
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

        self._cache.save(audio, metadata, result)
        return result

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
        except (TypeError, ValueError) as exc:
            raise SpeakerDiarizationInferenceError(
                f"pyannote returned malformed {name} speaker diarization: {exc}"
            ) from exc
        return sorted(turns, key=lambda turn: (turn.start, turn.end, turn.speaker))

    def _get_cache_metadata(self) -> Mapping[str, object]:
        """Get exact pipeline identity and result-affecting parameters."""
        try:
            pyannote_audio_version = version("pyannote.audio")
        except PackageNotFoundError as exc:
            raise SpeakerDiarizationDependencyError(
                "Speaker diarization requires pyannote.audio. Install Scinoephile "
                "with the 'transcription' extra."
            ) from exc
        metadata = {
            "device": self.device,
            "max_speakers": self.max_speakers,
            "min_speakers": self.min_speakers,
            "model_id": self.model_id,
            "model_revision": self.model_revision,
            "num_speakers": self.num_speakers,
            "pipeline_class": _PIPELINE_CLASS_NAME,
            "pyannote_audio_version": pyannote_audio_version,
            "waveform_channels": _WAVEFORM_CHANNELS,
            "waveform_frame_rate": _WAVEFORM_FRAME_RATE,
            "waveform_sample_width": _WAVEFORM_SAMPLE_WIDTH,
        }
        if self.model_id == _DEFAULT_MODEL_ID:
            metadata.update(
                {
                    "embedding_model_id": _EMBEDDING_MODEL_ID,
                    "embedding_model_revision": _EMBEDDING_MODEL_REVISION,
                    "plda_model_id": _PLDA_MODEL_ID,
                    "plda_model_revision": _PLDA_MODEL_REVISION,
                    "segmentation_model_id": _SEGMENTATION_MODEL_ID,
                    "segmentation_model_revision": _SEGMENTATION_MODEL_REVISION,
                }
            )
        return metadata

    def _get_pipeline(self) -> object:
        """Lazily load and place the configured pyannote pipeline."""
        if self._pipeline is not None:
            return self._pipeline
        try:
            pyannote_audio = import_pyannote_audio()
            pipeline_cls = getattr(pyannote_audio, "Pipeline")
            from_pretrained = getattr(pipeline_cls, "from_pretrained")
            if self.model_id == _DEFAULT_MODEL_ID:
                pipeline = from_pretrained(self._load_pinned_pipeline_config())
            else:
                pipeline = from_pretrained(self.model_id, revision=self.model_revision)
            if pipeline is None:
                raise SpeakerDiarizationAuthorizationError(
                    "Unable to load the gated pyannote diarization assets. Accept "
                    "the Hugging Face conditions for speaker-diarization-3.0, "
                    "segmentation-3.0, and speaker-diarization-community-1, then "
                    "configure a Hugging Face token."
                )
            torch = import_torch()
            pipeline.to(torch.device(self.device))
        except ImportError as exc:
            raise SpeakerDiarizationDependencyError(
                "Speaker diarization requires pyannote.audio. Install Scinoephile "
                "with the 'transcription' extra."
            ) from exc
        except SpeakerDiarizationAuthorizationError:
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
                    "Hugging Face has not authorized all required pyannote assets. "
                    "Accept the conditions for speaker-diarization-3.0, "
                    "segmentation-3.0, and speaker-diarization-community-1, then "
                    "configure a Hugging Face token."
                ) from exc
            raise SpeakerDiarizationInferenceError(
                f"Unable to load pyannote speaker diarization: {exc}"
            ) from exc
        self._pipeline = pipeline
        return pipeline

    def _load_pinned_pipeline_config(self) -> dict[str, object]:
        """Load the exact pipeline config and pin all transitive model assets.

        Returns:
            mutable pyannote pipeline configuration
        Raises:
            ValueError: if the downloaded pipeline configuration is malformed
        """
        huggingface_hub = import_huggingface_hub()
        hf_hub_download = cast(
            Callable[..., str], getattr(huggingface_hub, "hf_hub_download")
        )
        config_path = Path(
            hf_hub_download(self.model_id, "config.yaml", revision=self.model_revision)
        )
        yaml = import_yaml()
        safe_load = cast(Callable[[object], object], getattr(yaml, "safe_load"))
        with config_path.open(encoding="utf-8") as file_handle:
            config = safe_load(file_handle)
        if not isinstance(config, dict):
            raise ValueError("pyannote returned a malformed pipeline configuration.")
        typed_config = cast(dict[str, object], config)
        pipeline_config = typed_config.get("pipeline")
        if not isinstance(pipeline_config, dict):
            raise ValueError("pyannote returned a malformed pipeline configuration.")
        typed_pipeline_config = cast(dict[str, object], pipeline_config)
        pipeline_params = typed_pipeline_config.get("params")
        if not isinstance(pipeline_params, dict):
            raise ValueError("pyannote returned a malformed pipeline configuration.")
        typed_pipeline_params = cast(dict[str, object], pipeline_params)

        embedding_path = hf_hub_download(
            _EMBEDDING_MODEL_ID,
            "speaker-embedding.onnx",
            revision=_EMBEDDING_MODEL_REVISION,
        )
        typed_pipeline_params["embedding"] = embedding_path
        typed_pipeline_params["plda"] = {
            "checkpoint": _PLDA_MODEL_ID,
            "revision": _PLDA_MODEL_REVISION,
            "subfolder": "plda",
        }
        typed_pipeline_params["segmentation"] = {
            "checkpoint": _SEGMENTATION_MODEL_ID,
            "revision": _SEGMENTATION_MODEL_REVISION,
        }
        return typed_config
