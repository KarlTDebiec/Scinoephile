#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Silero adapter for shared voice activity detection."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager
from math import floor
from typing import TYPE_CHECKING, cast

import numpy as np

from scinoephile.audio.samples import get_mono_pcm16_samples
from scinoephile.core.dependencies import transcription

from .exceptions import VoiceActivityError
from .intervals import get_padded_intervals
from .provider import VadImplementation, VadProvider
from .trace import VoiceActivityTrace

__all__ = ["SileroVadProvider"]

if TYPE_CHECKING:
    from pydub import AudioSegment


class SileroVadProvider(VadProvider):
    """Infer and postprocess voice activity through Silero."""

    implementation = VadImplementation.SILERO
    """Voice activity detection implementation."""

    def __init__(self, sample_rate: int):
        """Initialize.

        Arguments:
            sample_rate: input sample rate expected by Silero
        Raises:
            ValueError: if the sample rate is unsupported
        """
        if sample_rate != 16000:
            raise ValueError("Silero VAD requires a sample rate of 16000 Hz.")
        self.sample_rate = sample_rate
        """Input sample rate expected by Silero."""

        self._model: object | None = None
        """Lazily loaded official Silero model."""

    @property
    def cache_identity(self) -> dict[str, object]:
        """Get the Silero model and runtime identity."""
        return {
            "model": "silero-vad",
            "model_format": "onnx",
            "model_opset": 16,
            "runtime": self._get_distribution_identity("silero-vad"),
        }

    def get_speech_intervals(
        self,
        trace: VoiceActivityTrace,
        *,
        threshold: float,
        min_speech_duration_seconds: float,
        min_silence_duration_seconds: float,
        padding_seconds: float,
    ) -> list[tuple[int, int]]:
        """Derive speech intervals using Silero's hysteresis postprocessing.

        Arguments:
            trace: frame-level Silero model scores
            threshold: minimum model score treated as speech
            min_speech_duration_seconds: minimum retained speech duration
            min_silence_duration_seconds: minimum silence separating intervals
            padding_seconds: context retained around detected speech
        Returns:
            speech start and end offsets in milliseconds
        """
        if not len(trace):
            return []

        negative_threshold = max(threshold - 0.15, 0.01)
        minimum_silence_ms = min_silence_duration_seconds * 1000
        minimum_speech_ms = min_speech_duration_seconds * 1000
        triggered = False
        speech_start_ms = 0.0
        silence_start_ms = 0.0
        raw_intervals: list[list[float]] = []
        for frame_idx, score in enumerate(trace.scores):
            frame_start_ms = frame_idx * trace.step_ms
            if score >= threshold and not triggered:
                triggered = True
                speech_start_ms = frame_start_ms
                silence_start_ms = 0.0
                continue
            if score >= threshold and silence_start_ms:
                silence_start_ms = 0.0
            if score < negative_threshold and triggered:
                if not silence_start_ms:
                    silence_start_ms = frame_start_ms
                if frame_start_ms - silence_start_ms < minimum_silence_ms:
                    continue
                if silence_start_ms - speech_start_ms >= minimum_speech_ms:
                    raw_intervals.append([speech_start_ms, silence_start_ms])
                triggered = False
                silence_start_ms = 0.0
        if triggered and trace.duration_ms - speech_start_ms >= minimum_speech_ms:
            raw_intervals.append([speech_start_ms, float(trace.duration_ms)])
        return self._get_padded_intervals(
            raw_intervals, trace.duration_ms, padding_seconds
        )

    def get_trace(self, audio: AudioSegment) -> VoiceActivityTrace:
        """Infer frame-level scores from the Silero VAD model.

        Arguments:
            audio: source audio
        Returns:
            model scores aligned to the source timeline
        """
        try:
            load_silero_vad = transcription.import_silero_vad_load_silero_vad()
            torch = transcription.import_torch()
        except ImportError as exc:
            raise VoiceActivityError(
                "Silero VAD requires the optional transcription dependencies."
            ) from exc

        samples = get_mono_pcm16_samples(audio, self.sample_rate).astype(np.float32)
        samples /= np.iinfo(np.int16).max
        if not len(samples):
            return VoiceActivityTrace(
                np.empty(0, dtype=np.float32),
                start_ms=16.0,
                step_ms=32.0,
                duration_ms=0,
            )
        samples /= max(0.1, float(np.max(np.abs(samples))))
        try:
            model = self._load_model(load_silero_vad)
            reset_states = cast(Callable[[], object], getattr(model, "reset_states"))
            run_model = cast(Callable[[object, int], object], model)
            no_grad = cast(
                Callable[[], AbstractContextManager[object]], getattr(torch, "no_grad")
            )
            reset_states()
            probabilities = []
            with no_grad():
                for frame_start_idx in range(0, len(samples), 512):
                    frame = samples[frame_start_idx : frame_start_idx + 512]
                    if len(frame) < 512:
                        frame = np.pad(frame, (0, 512 - len(frame)))
                    output = run_model(torch.from_numpy(frame), self.sample_rate)
                    probability = float(getattr(output, "item")())
                    if not 0 <= probability <= 1:
                        raise ValueError(
                            f"Silero VAD returned score outside [0, 1]: {probability}"
                        )
                    probabilities.append(probability)
        except (AssertionError, ImportError, OSError, RuntimeError, ValueError) as exc:
            raise VoiceActivityError(f"Unable to run Silero VAD: {exc}") from exc
        return VoiceActivityTrace(
            np.asarray(probabilities, dtype=np.float32),
            start_ms=16.0,
            step_ms=32.0,
            duration_ms=len(audio),
        )

    def _get_padded_intervals(
        self, raw_intervals: list[list[float]], duration_ms: int, padding_seconds: float
    ) -> list[tuple[int, int]]:
        """Apply Silero's internal padding followed by configured padding.

        Arguments:
            raw_intervals: unpadded speech intervals in milliseconds
            duration_ms: source audio duration in milliseconds
            padding_seconds: configured context around detected speech
        Returns:
            padded speech intervals
        """
        internal_padding_ms = 30.0
        for interval_idx, interval in enumerate(raw_intervals):
            if interval_idx == 0:
                interval[0] = max(0.0, interval[0] - internal_padding_ms)
            if interval_idx != len(raw_intervals) - 1:
                silence_ms = raw_intervals[interval_idx + 1][0] - interval[1]
                if silence_ms < 2 * internal_padding_ms:
                    interval[1] += floor(silence_ms / 2)
                    raw_intervals[interval_idx + 1][0] = max(
                        0.0, raw_intervals[interval_idx + 1][0] - floor(silence_ms / 2)
                    )
                else:
                    interval[1] = min(
                        float(duration_ms), interval[1] + internal_padding_ms
                    )
                    raw_intervals[interval_idx + 1][0] = max(
                        0.0, raw_intervals[interval_idx + 1][0] - internal_padding_ms
                    )
            else:
                interval[1] = min(float(duration_ms), interval[1] + internal_padding_ms)
        return get_padded_intervals(
            ((start_ms, end_ms) for start_ms, end_ms in raw_intervals),
            duration_ms,
            padding_seconds,
        )

    def _load_model(self, load_silero_vad: Callable[..., object]) -> object:
        """Lazily load the official packaged Silero model.

        Arguments:
            load_silero_vad: official Silero model loader
        Returns:
            configured Silero model
        """
        if self._model is not None:
            return self._model

        self._model = load_silero_vad(onnx=True, opset_version=16)
        return self._model
