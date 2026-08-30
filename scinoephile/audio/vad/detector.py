#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audio voice activity detector configuration and orchestration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scinoephile.core.cache.identity import CacheIdentity

from .provider import VadImplementation, VadProvider
from .pyannote import PyannoteVadProvider
from .silero import SileroVadProvider
from .ten import TenVadProvider
from .trace import VoiceActivityTrace

__all__ = ["VoiceActivityDetector"]

if TYPE_CHECKING:
    from pydub import AudioSegment

_POSTPROCESSING_VERSION = 2
"""Version of Scinoephile's probability-to-interval postprocessing."""

_TRACE_IDENTITY_VERSION = 2
"""Version of Scinoephile's frame-level score trace identity."""


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
        if min_speech_duration_seconds < 0:
            raise ValueError("VAD minimum speech duration must be non-negative.")
        if min_silence_duration_seconds < 0:
            raise ValueError("VAD minimum silence duration must be non-negative.")
        if padding_seconds < 0:
            raise ValueError("VAD padding must be non-negative.")
        if sample_rate <= 0:
            raise ValueError("VAD sample rate must be positive.")
        self.threshold = threshold
        """Minimum model score treated as speech."""

        self.min_speech_duration_seconds = min_speech_duration_seconds
        """Minimum retained speech duration."""

        self.min_silence_duration_seconds = min_silence_duration_seconds
        """Minimum silence separating speech intervals."""

        self.padding_seconds = padding_seconds
        """Context retained around speech intervals."""

        self._provider: VadProvider
        """Provider-specific inference adapter."""

        if implementation is VadImplementation.PYANNOTE:
            self._provider = PyannoteVadProvider(sample_rate)
        elif implementation is VadImplementation.SILERO:
            self._provider = SileroVadProvider(sample_rate)
        elif implementation is VadImplementation.TEN:
            self._provider = TenVadProvider(frame_size, sample_rate)
        else:
            raise ValueError(f"Unsupported VAD implementation: {implementation!r}.")

    def __call__(self, audio: AudioSegment) -> list[tuple[int, int]]:
        """Detect speech intervals.

        Arguments:
            audio: source audio
        Returns:
            speech start and end offsets in milliseconds
        """
        return self.get_speech_intervals(self.get_trace(audio))

    @property
    def cache_identity(self) -> CacheIdentity:
        """Get the configuration identifying reusable VAD output.

        Returns:
            VAD implementation, model, runtime, and postprocessing configuration
        """
        return {
            **self.trace_cache_identity,
            "min_silence_duration_seconds": self.min_silence_duration_seconds,
            "min_speech_duration_seconds": self.min_speech_duration_seconds,
            "padding_seconds": self.padding_seconds,
            "postprocessing_version": _POSTPROCESSING_VERSION,
            "threshold": self.threshold,
        }

    @property
    def implementation(self) -> VadImplementation:
        """Voice activity detection implementation."""
        return self._provider.implementation

    @property
    def trace_cache_identity(self) -> CacheIdentity:
        """Get the configuration identifying reusable frame-level model scores.

        Returns:
            VAD implementation, model, runtime, and inference geometry
        """
        return {
            **self._provider.cache_identity,
            "implementation": self.implementation.value,
            "sample_rate": self._provider.sample_rate,
            "trace_identity_version": _TRACE_IDENTITY_VERSION,
        }

    def get_speech_intervals(self, trace: VoiceActivityTrace) -> list[tuple[int, int]]:
        """Derive configured binary speech intervals from a model-score trace.

        Arguments:
            trace: frame-level voice activity model scores
        Returns:
            speech start and end offsets in milliseconds
        """
        return self._provider.get_speech_intervals(
            trace,
            threshold=self.threshold,
            min_speech_duration_seconds=self.min_speech_duration_seconds,
            min_silence_duration_seconds=self.min_silence_duration_seconds,
            padding_seconds=self.padding_seconds,
        )

    def get_trace(self, audio: AudioSegment) -> VoiceActivityTrace:
        """Infer frame-level voice activity scores.

        Arguments:
            audio: source audio
        Returns:
            model scores aligned to the original audio timeline
        """
        return self._provider.get_trace(audio)
