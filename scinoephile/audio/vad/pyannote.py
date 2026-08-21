#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""pyannote adapter for shared voice activity detection."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, cast

import numpy as np

from scinoephile.audio.waveform import to_mono_int16
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.cache.runtime import get_distribution_identity
from scinoephile.core.dependencies import transcription
from scinoephile.core.ml import get_huggingface_snapshot_dir_path

from .exceptions import VoiceActivityError
from .provider import VadImplementation, VadProvider
from .trace import VoiceActivityTrace

__all__ = ["PyannoteVadProvider"]

if TYPE_CHECKING:
    from pydub import AudioSegment

_MODEL_ID = "pyannote/segmentation-3.0"
_MODEL_REVISION = "e66f3d3b9eb0873085418a7b813d3b369bf160bb"


class PyannoteVadProvider(VadProvider):
    """Infer frame-level voice activity scores through pyannote."""

    implementation = VadImplementation.PYANNOTE
    """Voice activity detection implementation."""

    def __init__(self, sample_rate: int):
        """Initialize.

        Arguments:
            sample_rate: input sample rate expected by pyannote
        Raises:
            ValueError: if the sample rate is unsupported
        """
        if sample_rate != 16000:
            raise ValueError("pyannote VAD requires 16000 Hz audio.")
        self.sample_rate = sample_rate
        """Input sample rate expected by pyannote."""

        self._pipeline: object | None = None
        """Lazily loaded pyannote voice activity detection pipeline."""

    @property
    def cache_identity(self) -> CacheIdentity:
        """Get the pyannote model and runtime identity."""
        return {
            "model": _MODEL_ID,
            "model_revision": _MODEL_REVISION,
            "runtime": get_distribution_identity("pyannote.audio"),
        }

    def get_trace(self, audio: AudioSegment) -> VoiceActivityTrace:
        """Infer frame-level pyannote segmentation scores.

        Arguments:
            audio: source audio
        Returns:
            model scores aligned to the source timeline
        """
        if not len(audio):
            return VoiceActivityTrace(
                np.empty(0, dtype=np.float32),
                start_ms=0.0,
                step_ms=16.875,
                duration_ms=0,
            )

        try:
            torch = transcription.import_torch()
            pipeline = self._load_pipeline(torch)
            samples = to_mono_int16(audio, self.sample_rate)
            samples = samples.astype(np.float32).reshape(1, -1)
            samples /= float(1 << 15)
            run_inference = cast(
                Callable[[Mapping[str, object]], object],
                getattr(pipeline, "_segmentation"),
            )
            segmentation = run_inference(
                {"sample_rate": self.sample_rate, "waveform": torch.from_numpy(samples)}
            )
            raw_scores = np.asarray(getattr(segmentation, "data"), dtype=np.float32)
            if raw_scores.ndim != 2 or raw_scores.shape[1] == 0:
                raise VoiceActivityError(
                    "pyannote VAD returned malformed segmentation scores."
                )
            speech_scores = np.max(raw_scores, axis=1)
            sliding_window = getattr(segmentation, "sliding_window")
            start_seconds = float(getattr(sliding_window, "start"))
            frame_duration_seconds = float(getattr(sliding_window, "duration"))
            step_seconds = float(getattr(sliding_window, "step"))
            return VoiceActivityTrace(
                speech_scores,
                start_ms=(start_seconds + frame_duration_seconds / 2) * 1000,
                step_ms=step_seconds * 1000,
                duration_ms=len(audio),
            )
        except VoiceActivityError:
            raise
        except Exception as exc:
            raise VoiceActivityError(f"Unable to run pyannote VAD: {exc}") from exc

    def _load_pipeline(self, torch: object) -> object:
        """Lazily load and configure pyannote voice activity detection.

        Arguments:
            torch: imported Torch module
        Returns:
            configured pyannote VAD pipeline
        """
        if self._pipeline is not None:
            return self._pipeline
        try:
            pyannote_audio = transcription.import_pyannote_audio()
            model_class = getattr(pyannote_audio, "Model")
            from_pretrained = cast(
                Callable[..., object], getattr(model_class, "from_pretrained")
            )
            model_dir_path = get_huggingface_snapshot_dir_path(
                _MODEL_ID, _MODEL_REVISION
            )
            model = from_pretrained(model_dir_path)
            if model is None:
                raise VoiceActivityError(
                    "Unable to load the gated pyannote segmentation model. Accept "
                    "its Hugging Face conditions and configure a Hugging Face token."
                )
            pipeline_class = (
                transcription.import_pyannote_audio_voice_activity_detection()
            )
            pipeline = pipeline_class(segmentation=model)
            device = cast(Callable[[str], object], getattr(torch, "device"))("cpu")
            cast(Callable[[object], object], getattr(pipeline, "to"))(device)
        except ImportError as exc:
            raise VoiceActivityError(
                "pyannote VAD requires the optional transcription dependencies."
            ) from exc
        except VoiceActivityError:
            raise
        except Exception as exc:
            exception_name = type(exc).__name__
            message = str(exc).casefold()
            if exception_name in {
                "GatedRepoError",
                "RepositoryNotFoundError",
                "UnauthorizedError",
            } or any(token in message for token in ("401", "403", "gated repo")):
                raise VoiceActivityError(
                    "Hugging Face has not authorized pyannote segmentation-3.0. "
                    "Accept the model conditions and configure a Hugging Face token."
                ) from exc
            raise VoiceActivityError(
                f"Unable to initialize pyannote VAD: {exc}"
            ) from exc
        self._pipeline = pipeline
        return pipeline
