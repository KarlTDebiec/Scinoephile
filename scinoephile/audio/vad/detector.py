#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audio voice activity detector configuration and orchestration."""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from functools import partial
from typing import TYPE_CHECKING

from .identity import get_distribution_identity
from .intervals import get_threshold_speech_intervals
from .provider import VadProvider
from .pyannote import (
    PYANNOTE_VAD_MODEL_ID,
    PYANNOTE_VAD_MODEL_REVISION,
    PyannoteVadProvider,
)
from .silero import SileroVadProvider
from .ten import TenVadProvider
from .trace import VoiceActivityTrace

__all__ = ["VadImplementation", "VoiceActivityDetector"]

if TYPE_CHECKING:
    from pydub import AudioSegment

_POSTPROCESSING_VERSION = "2"
"""Version of Scinoephile's probability-to-interval postprocessing."""

_TRACE_IDENTITY_VERSION = "1"
"""Version of Scinoephile's frame-level score trace identity."""


class VadImplementation(StrEnum):
    """Voice activity detection implementations."""

    PYANNOTE = "pyannote"
    """Use pyannote's speaker-segmentation model as a speech detector."""
    SILERO = "silero"
    """Use the official Silero VAD runtime."""
    TEN = "ten"
    """Use the official TEN VAD runtime."""


class VoiceActivityDetector:
    """Detect speech intervals using a selected VAD implementation."""

    def __init__(
        self,
        implementation: VadImplementation = VadImplementation.SILERO,
        *,
        threshold: float = 0.5,
        frame_size: int = 256,
        min_speech_duration_seconds: float = 0.1,
        min_silence_duration_seconds: float = 1.0,
        padding_seconds: float = 0.5,
        sample_rate: int = 16000,
    ):
        """Initialize.

        Arguments:
            implementation: VAD implementation to use
            threshold: minimum model score treated as speech
            frame_size: TEN inference frame size in samples
            min_speech_duration_seconds: minimum retained speech duration
            min_silence_duration_seconds: minimum silence separating intervals
            padding_seconds: context retained around detected speech
            sample_rate: input sample rate expected by the VAD implementation
        Raises:
            ValueError: if numeric configuration is invalid
        """
        if not 0 <= threshold <= 1:
            raise ValueError("VAD threshold must be between zero and one.")
        if frame_size <= 0:
            raise ValueError("VAD frame size must be positive.")
        if min_speech_duration_seconds < 0:
            raise ValueError("VAD minimum speech duration must be non-negative.")
        if min_silence_duration_seconds < 0:
            raise ValueError("VAD minimum silence duration must be non-negative.")
        if padding_seconds < 0:
            raise ValueError("VAD padding must be non-negative.")
        if sample_rate <= 0:
            raise ValueError("VAD sample rate must be positive.")
        if implementation is VadImplementation.PYANNOTE and sample_rate != 16000:
            raise ValueError("pyannote VAD requires 16000 Hz audio.")
        if implementation is VadImplementation.TEN and sample_rate != 16000:
            raise ValueError("TEN VAD requires a sample rate of 16000 Hz.")
        if implementation is VadImplementation.TEN and frame_size not in {160, 256}:
            raise ValueError("TEN VAD frame size must be 160 or 256 samples.")

        self.implementation = implementation
        """VAD implementation."""

        self.threshold = threshold
        """Minimum model score treated as speech."""

        self.frame_size = frame_size
        """TEN inference frame size in samples."""

        self.min_speech_duration_seconds = min_speech_duration_seconds
        """Minimum retained speech duration."""

        self.min_silence_duration_seconds = min_silence_duration_seconds
        """Minimum silence separating speech intervals."""

        self.padding_seconds = padding_seconds
        """Context retained around speech intervals."""

        self.sample_rate = sample_rate
        """Sample rate expected by the VAD implementation."""

        self._provider: VadProvider
        """Provider-specific inference adapter."""

        self._derive_speech_intervals: Callable[
            [VoiceActivityTrace], list[tuple[int, int]]
        ] = partial(
            get_threshold_speech_intervals,
            threshold=self.threshold,
            min_speech_duration_seconds=self.min_speech_duration_seconds,
            min_silence_duration_seconds=self.min_silence_duration_seconds,
            padding_seconds=self.padding_seconds,
        )
        """Provider-appropriate trace postprocessor."""

        if implementation is VadImplementation.PYANNOTE:
            self._provider = PyannoteVadProvider(sample_rate)
        elif implementation is VadImplementation.SILERO:
            provider = SileroVadProvider(
                threshold,
                min_speech_duration_seconds,
                min_silence_duration_seconds,
                padding_seconds,
                sample_rate,
            )
            self._provider = provider
            self._derive_speech_intervals = provider.get_speech_intervals
        else:
            self._provider = TenVadProvider(frame_size, sample_rate)

    def __call__(self, audio: AudioSegment) -> list[tuple[int, int]]:
        """Detect speech intervals.

        Arguments:
            audio: source audio
        Returns:
            speech start and end offsets in milliseconds
        """
        return self.get_speech_intervals(self.get_trace(audio))

    @property
    def cache_identity(self) -> dict[str, object]:
        """Get the configuration identifying reusable VAD output.

        Returns:
            VAD implementation, model, runtime, and postprocessing configuration
        """
        if self.implementation is VadImplementation.SILERO:
            runtime_identity = get_distribution_identity("silero-vad")
            identity = self._get_common_cache_identity(runtime_identity)
            identity.update(
                {
                    "model": "silero-vad",
                    "model_format": "onnx",
                    "model_opset": 16,
                    "model_version": runtime_identity["version"],
                }
            )
            return identity

        if self.implementation is VadImplementation.PYANNOTE:
            runtime_identity = get_distribution_identity("pyannote.audio")
            identity = self._get_common_cache_identity(runtime_identity)
            identity.update(
                {
                    "model": PYANNOTE_VAD_MODEL_ID,
                    "model_revision": PYANNOTE_VAD_MODEL_REVISION,
                    "model_version": PYANNOTE_VAD_MODEL_REVISION,
                }
            )
            return identity

        runtime_identity = get_distribution_identity("ten-vad")
        identity = self._get_common_cache_identity(runtime_identity)
        identity.update(
            {
                "frame_size": self.frame_size,
                "model": "ten-vad-native",
                "model_version": runtime_identity["version"],
            }
        )
        return identity

    @property
    def trace_cache_identity(self) -> dict[str, object]:
        """Get the configuration identifying reusable frame-level model scores.

        Returns:
            VAD implementation, model, runtime, and inference geometry
        """
        identity = self.cache_identity
        for key in (
            "min_silence_duration_seconds",
            "min_speech_duration_seconds",
            "padding_seconds",
            "postprocessing_version",
            "threshold",
        ):
            identity.pop(key, None)
        identity["trace_identity_version"] = _TRACE_IDENTITY_VERSION
        return identity

    def get_speech_intervals(self, trace: VoiceActivityTrace) -> list[tuple[int, int]]:
        """Derive configured binary speech intervals from a model-score trace.

        Arguments:
            trace: frame-level voice activity model scores
        Returns:
            speech start and end offsets in milliseconds
        """
        return self._derive_speech_intervals(trace)

    def get_trace(self, audio: AudioSegment) -> VoiceActivityTrace:
        """Infer frame-level voice activity scores.

        Arguments:
            audio: source audio
        Returns:
            model scores aligned to the original audio timeline
        """
        return self._provider.get_trace(audio)

    def _get_common_cache_identity(
        self, runtime_identity: dict[str, str]
    ) -> dict[str, object]:
        """Get cache fields shared by all VAD implementations."""
        return {
            "implementation": self.implementation.value,
            "min_silence_duration_seconds": self.min_silence_duration_seconds,
            "min_speech_duration_seconds": self.min_speech_duration_seconds,
            "padding_seconds": self.padding_seconds,
            "postprocessing_version": _POSTPROCESSING_VERSION,
            "runtime": runtime_identity,
            "sample_rate": self.sample_rate,
            "threshold": self.threshold,
        }
