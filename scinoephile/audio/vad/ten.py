#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""TEN adapter for shared voice activity detection."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from scinoephile.audio.waveform import to_mono_int16
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.cache.runtime import get_distribution_identity
from scinoephile.core.dependencies.transcription import import_ten_vad

from .exceptions import VoiceActivityError
from .provider import VadImplementation, VadProvider
from .trace import VoiceActivityTrace

__all__ = ["TenVadProvider"]

if TYPE_CHECKING:
    from pydub import AudioSegment


class TenVadProvider(VadProvider):
    """Infer frame-level voice activity scores through TEN VAD."""

    implementation = VadImplementation.TEN
    """Voice activity detection implementation."""

    def __init__(self, frame_size: int, sample_rate: int):
        """Initialize.

        Arguments:
            frame_size: TEN inference frame size in samples
            sample_rate: input sample rate expected by TEN VAD
        Raises:
            ValueError: if the inference geometry is unsupported
        """
        if sample_rate != 16000:
            raise ValueError("TEN VAD requires a sample rate of 16000 Hz.")
        if frame_size not in {160, 256}:
            raise ValueError("TEN VAD frame size must be 160 or 256 samples.")
        self.frame_size = frame_size
        """TEN inference frame size in samples."""

        self.sample_rate = sample_rate
        """Input sample rate expected by TEN VAD."""

    @property
    def cache_identity(self) -> CacheIdentity:
        """Get the TEN model, runtime, and inference geometry identity."""
        return {
            "frame_size": self.frame_size,
            "model": "ten-vad-native",
            "runtime": get_distribution_identity("ten-vad"),
        }

    def get_trace(self, audio: AudioSegment) -> VoiceActivityTrace:
        """Infer frame-level scores from the official TEN VAD runtime.

        Arguments:
            audio: source audio
        Returns:
            model scores aligned to the source timeline
        Raises:
            DependencyError: if optional dependencies are unavailable
            VoiceActivityError: if initialization or inference fails
        """
        samples = to_mono_int16(audio, self.sample_rate)
        step_ms = self.frame_size / self.sample_rate * 1000
        if not len(samples):
            return VoiceActivityTrace(
                np.empty(0, dtype=np.float32),
                start_ms=step_ms / 2,
                step_ms=step_ms,
                duration_ms=0,
            )

        ten_vad = import_ten_vad()
        try:
            detector = ten_vad.TenVad(hop_size=self.frame_size, threshold=0.5)
        except (
            AssertionError,
            ImportError,
            NotImplementedError,
            OSError,
            RuntimeError,
        ) as exc:
            raise VoiceActivityError(f"Unable to initialize TEN VAD: {exc}") from exc

        probabilities: list[float] = []
        try:
            for frame_start_idx in range(0, len(samples), self.frame_size):
                frame = samples[frame_start_idx : frame_start_idx + self.frame_size]
                if len(frame) < self.frame_size:
                    frame = np.pad(frame, (0, self.frame_size - len(frame)))
                probability, _ = detector.process(frame)
                if not isinstance(probability, int | float):
                    raise ValueError("TEN VAD returned a non-numeric probability.")
                probability = float(probability)
                if not 0 <= probability <= 1:
                    raise ValueError(
                        f"TEN VAD returned probability outside [0, 1]: {probability}"
                    )
                probabilities.append(probability)
        except (AssertionError, OSError, RuntimeError, ValueError) as exc:
            raise VoiceActivityError(f"Unable to run TEN VAD: {exc}") from exc

        return VoiceActivityTrace(
            np.asarray(probabilities, dtype=np.float32),
            start_ms=step_ms / 2,
            step_ms=step_ms,
            duration_ms=len(audio),
        )
