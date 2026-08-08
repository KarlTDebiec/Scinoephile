#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Voice activity detection shared by transcription backends."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from contextlib import AbstractContextManager
from copy import deepcopy
from enum import StrEnum
from hashlib import sha256
from importlib.metadata import Distribution, PackageNotFoundError, distribution
from json import JSONDecodeError, loads
from math import ceil, floor
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING, cast
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import numpy as np

from scinoephile.core.dependencies.transcription import (
    import_pyannote_audio,
    import_pyannote_audio_voice_activity_detection,
    import_ten_vad,
    import_torch,
    import_whisper_timestamped_transcribe,
)

from .exceptions import TranscriptionError
from .voice_activity_trace import VoiceActivityTrace

__all__ = ["VADImplementation", "VoiceActivityDetector"]

if TYPE_CHECKING:
    from pydub import AudioSegment

_CACHE_IDENTITY_VERSION = "3"
"""Version of Scinoephile's VAD cache identity schema."""

_POSTPROCESSING_VERSION = "2"
"""Version of Scinoephile's probability-to-interval postprocessing."""

_TRACE_IDENTITY_VERSION = "1"
"""Version of Scinoephile's frame-level score trace identity."""

_PYANNOTE_VAD_MODEL_ID = "pyannote/segmentation-3.0"
"""Hugging Face model used by pyannote voice activity detection."""

_PYANNOTE_VAD_MODEL_REVISION = "e66f3d3b9eb0873085418a7b813d3b369bf160bb"
"""Pinned Hugging Face revision of the pyannote segmentation model."""

_SILERO_MODEL_COMMIT = "be95df9152c0d7618fa1edfeb296fc3dae32376f"
"""Commit referenced by the tested Silero model tag."""

_SILERO_MODEL_REVISION = "v6.2"
"""Silero model tag compatible with Whisper Timestamped's version parser."""

_TEN_TESTED_REVISION = "22a3bcd4509d0faaa8eef4881e8af5f39c178950"
"""Official TEN VAD revision tested by Scinoephile."""


class VADImplementation(StrEnum):
    """Voice activity detection implementations."""

    SILERO = "silero"
    """Use Whisper Timestamped's Silero detector."""
    TEN = "ten"
    """Use the official TEN VAD runtime."""
    PYANNOTE = "pyannote"
    """Use pyannote's speaker-segmentation model as a speech detector."""


class VoiceActivityDetector:
    """Detect speech intervals using a selected VAD implementation."""

    def __init__(
        self,
        implementation: VADImplementation = VADImplementation.SILERO,
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
            min_speech_duration_seconds: minimum retained TEN speech duration
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
        if implementation is VADImplementation.PYANNOTE and sample_rate != 16000:
            raise ValueError("pyannote VAD requires 16000 Hz audio.")
        if implementation is VADImplementation.TEN and sample_rate != 16000:
            raise ValueError("TEN VAD requires a sample rate of 16000 Hz.")
        if implementation is VADImplementation.TEN and frame_size not in {160, 256}:
            raise ValueError("TEN VAD frame size must be 160 or 256 samples.")

        self.implementation = implementation
        """VAD implementation."""

        self.threshold = threshold
        """Minimum model score treated as speech."""

        self.frame_size = frame_size
        """TEN inference frame size in samples."""

        self.min_speech_duration_seconds = min_speech_duration_seconds
        """Minimum retained TEN speech duration."""

        self.min_silence_duration_seconds = min_silence_duration_seconds
        """Minimum silence separating speech intervals."""

        self.padding_seconds = padding_seconds
        """Context retained around speech intervals."""

        self.sample_rate = sample_rate
        """Sample rate expected by the VAD implementation."""

        self._cache_nonce = uuid4().hex
        """Process-local cache discriminator used when artifacts are unavailable."""

        self._resolved_cache_identity: dict[str, object] | None = None
        """Memoized cache identity after all runtime artifacts are identified."""

        self._pyannote_vad_pipeline: object | None = None
        """Lazily loaded pyannote voice activity detection pipeline."""

        self._silero_vad_model: object | None = None
        """Lazily loaded Silero voice activity detection model."""

    @property
    def cache_identity(self) -> dict[str, object]:
        """Get the configuration identifying reusable VAD output.

        Returns:
            VAD implementation, model, runtime, and postprocessing configuration
        """
        if self._resolved_cache_identity is not None:
            return deepcopy(self._resolved_cache_identity)

        if self.implementation is VADImplementation.SILERO:
            runtime_identity = _get_distribution_identity(
                "whisper-timestamped", "whisper_timestamped"
            )
            model_artifact_sha256 = _get_silero_model_artifact_sha256()
            identity: dict[str, object] = {
                "cache_identity_version": _CACHE_IDENTITY_VERSION,
                "implementation": self.implementation.value,
                "model": "snakers4/silero-vad",
                "model_artifact_sha256": model_artifact_sha256 or "unavailable",
                "model_revision": _SILERO_MODEL_REVISION,
                "model_revision_commit": _SILERO_MODEL_COMMIT,
                "model_version": _SILERO_MODEL_REVISION,
                "min_silence_duration_seconds": self.min_silence_duration_seconds,
                "min_speech_duration_seconds": self.min_speech_duration_seconds,
                "padding_seconds": self.padding_seconds,
                "postprocessing_version": _POSTPROCESSING_VERSION,
                "runtime": runtime_identity,
                "sample_rate": self.sample_rate,
                "threshold": self.threshold,
            }
            if (
                model_artifact_sha256 is None
                or "artifact_sha256" not in runtime_identity
            ):
                identity["unavailable_artifact_nonce"] = self._cache_nonce
            else:
                self._resolved_cache_identity = identity
            return deepcopy(identity)

        if self.implementation is VADImplementation.PYANNOTE:
            runtime_identity = _get_distribution_identity("pyannote.audio", "pyannote")
            identity = {
                "cache_identity_version": _CACHE_IDENTITY_VERSION,
                "implementation": self.implementation.value,
                "min_silence_duration_seconds": self.min_silence_duration_seconds,
                "min_speech_duration_seconds": self.min_speech_duration_seconds,
                "model": _PYANNOTE_VAD_MODEL_ID,
                "model_revision": _PYANNOTE_VAD_MODEL_REVISION,
                "model_version": _PYANNOTE_VAD_MODEL_REVISION,
                "padding_seconds": self.padding_seconds,
                "postprocessing_version": _POSTPROCESSING_VERSION,
                "runtime": runtime_identity,
                "sample_rate": self.sample_rate,
                "threshold": self.threshold,
            }
            if "artifact_sha256" not in runtime_identity:
                identity["unavailable_artifact_nonce"] = self._cache_nonce
            else:
                self._resolved_cache_identity = identity
            return deepcopy(identity)

        runtime_identity = _get_distribution_identity("ten-vad", "ten_vad")
        identity = {
            "cache_identity_version": _CACHE_IDENTITY_VERSION,
            "implementation": self.implementation.value,
            "model": "ten-vad-native",
            "model_version": runtime_identity["version"],
            "frame_size": self.frame_size,
            "min_silence_duration_seconds": self.min_silence_duration_seconds,
            "min_speech_duration_seconds": self.min_speech_duration_seconds,
            "padding_seconds": self.padding_seconds,
            "postprocessing_version": _POSTPROCESSING_VERSION,
            "runtime": runtime_identity,
            "sample_rate": self.sample_rate,
            "tested_revision": _TEN_TESTED_REVISION,
            "threshold": self.threshold,
        }
        if "artifact_sha256" not in runtime_identity:
            identity["unavailable_artifact_nonce"] = self._cache_nonce
        else:
            self._resolved_cache_identity = identity
        return deepcopy(identity)

    @property
    def trace_cache_identity(self) -> dict[str, object]:
        """Get the configuration identifying reusable frame-level model scores.

        Returns:
            VAD implementation, model, runtime, and inference geometry
        """
        identity = self.cache_identity
        for key in (
            "cache_identity_version",
            "min_silence_duration_seconds",
            "min_speech_duration_seconds",
            "padding_seconds",
            "postprocessing_version",
            "threshold",
        ):
            identity.pop(key, None)
        identity["trace_identity_version"] = _TRACE_IDENTITY_VERSION
        return identity

    def __call__(self, audio: AudioSegment) -> list[tuple[int, int]]:
        """Detect speech intervals.

        Arguments:
            audio: source audio
        Returns:
            speech start and end offsets in milliseconds
        """
        return self.get_speech_intervals(self.get_trace(audio))

    def get_speech_intervals(self, trace: VoiceActivityTrace) -> list[tuple[int, int]]:
        """Derive configured binary speech intervals from a model-score trace.

        Arguments:
            trace: frame-level voice activity model scores
        Returns:
            speech start and end offsets in milliseconds
        """
        if self.implementation is VADImplementation.PYANNOTE:
            return self._get_pyannote_speech_intervals(trace)
        if self.implementation is VADImplementation.TEN:
            return self._get_speech_intervals_from_probabilities(
                trace.scores.tolist(), trace.duration_ms
            )
        return self._get_silero_speech_intervals(trace)

    def get_trace(self, audio: AudioSegment) -> VoiceActivityTrace:
        """Infer frame-level voice activity scores.

        Arguments:
            audio: source audio
        Returns:
            model scores aligned to the original audio timeline
        """
        if self.implementation is VADImplementation.PYANNOTE:
            return self._get_pyannote_trace(audio)
        if self.implementation is VADImplementation.TEN:
            return self._get_ten_trace(audio)
        return self._get_silero_trace(audio)

    def _get_padded_intervals(
        self, raw_intervals: Iterable[tuple[float, float]], duration_ms: int
    ) -> list[tuple[int, int]]:
        """Pad, clip, and merge raw millisecond intervals.

        Arguments:
            raw_intervals: unpadded start and end offsets in milliseconds
            duration_ms: duration of the original audio in milliseconds
        Returns:
            padded speech intervals
        """
        padding_ms = round(self.padding_seconds * 1000)
        intervals: list[tuple[int, int]] = []
        for raw_start_ms, raw_end_ms in raw_intervals:
            start_ms = max(0, round(raw_start_ms) - padding_ms)
            end_ms = min(duration_ms, round(raw_end_ms) + padding_ms)
            if intervals and start_ms <= intervals[-1][1]:
                intervals[-1] = (intervals[-1][0], max(intervals[-1][1], end_ms))
            elif end_ms > start_ms:
                intervals.append((start_ms, end_ms))
        return intervals

    def _get_pyannote_speech_intervals(
        self, trace: VoiceActivityTrace
    ) -> list[tuple[int, int]]:
        """Derive speech intervals from pyannote segmentation scores."""
        if not len(trace):
            return []

        raw_intervals: list[tuple[float, float]] = []
        current_start_ms = trace.start_ms
        is_active = bool(trace.scores[0] > self.threshold)
        for frame_idx, score in enumerate(trace.scores[1:], 1):
            timestamp_ms = trace.start_ms + frame_idx * trace.step_ms
            if is_active:
                if score < self.threshold:
                    raw_intervals.append((current_start_ms, timestamp_ms))
                    current_start_ms = timestamp_ms
                    is_active = False
            elif score > self.threshold:
                current_start_ms = timestamp_ms
                is_active = True
        if is_active:
            last_timestamp_ms = trace.start_ms + (len(trace) - 1) * trace.step_ms
            raw_intervals.append((current_start_ms, last_timestamp_ms))

        minimum_silence_ms = self.min_silence_duration_seconds * 1000
        merged_intervals: list[tuple[float, float]] = []
        for start_ms, end_ms in raw_intervals:
            if (
                merged_intervals
                and start_ms - merged_intervals[-1][1] <= minimum_silence_ms
            ):
                merged_intervals[-1] = (merged_intervals[-1][0], end_ms)
            else:
                merged_intervals.append((start_ms, end_ms))
        minimum_speech_ms = self.min_speech_duration_seconds * 1000
        retained_intervals = [
            interval
            for interval in merged_intervals
            if interval[1] - interval[0] >= minimum_speech_ms
        ]
        return self._get_padded_intervals(retained_intervals, trace.duration_ms)

    def _get_pyannote_trace(self, audio: AudioSegment) -> VoiceActivityTrace:
        """Get frame-level scores from pyannote's segmentation model."""
        if not len(audio):
            return VoiceActivityTrace(
                np.empty(0, dtype=np.float32),
                start_ms=0.0,
                step_ms=16.875,
                duration_ms=0,
            )

        try:
            torch = import_torch()
            pipeline = self._load_pyannote_vad_pipeline(torch)
            normalized_audio = (
                audio.set_channels(1)
                .set_frame_rate(self.sample_rate)
                .set_sample_width(2)
            )
            samples = np.asarray(
                normalized_audio.get_array_of_samples(), dtype=np.float32
            ).reshape(1, -1)
            samples /= float(1 << 15)
            run_inference = cast(
                Callable[[Mapping[str, object]], object],
                getattr(pipeline, "_segmentation"),
            )
            segmentation = run_inference(
                {"sample_rate": self.sample_rate, "waveform": torch.from_numpy(samples)}
            )
            raw_scores = np.asarray(getattr(segmentation, "data"), dtype=np.float32)
            if raw_scores.ndim != 2 or raw_scores.shape[1] != 1:
                raise TranscriptionError(
                    "pyannote VAD returned malformed segmentation scores."
                )
            sliding_window = getattr(segmentation, "sliding_window")
            start_seconds = float(getattr(sliding_window, "start"))
            frame_duration_seconds = float(getattr(sliding_window, "duration"))
            step_seconds = float(getattr(sliding_window, "step"))
            return VoiceActivityTrace(
                raw_scores[:, 0],
                start_ms=(start_seconds + frame_duration_seconds / 2) * 1000,
                step_ms=step_seconds * 1000,
                duration_ms=len(audio),
            )
        except TranscriptionError:
            raise
        except Exception as exc:
            raise TranscriptionError(f"Unable to run pyannote VAD: {exc}") from exc

    def _get_silero_padded_intervals(
        self, raw_intervals: list[list[float]], duration_ms: int
    ) -> list[tuple[int, int]]:
        """Apply Silero's internal padding followed by configured padding."""
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
        return self._get_padded_intervals(
            ((start_ms, end_ms) for start_ms, end_ms in raw_intervals), duration_ms
        )

    def _get_silero_speech_intervals(
        self, trace: VoiceActivityTrace
    ) -> list[tuple[int, int]]:
        """Derive speech intervals using Silero's hysteresis postprocessing."""
        if not len(trace):
            return []

        negative_threshold = max(self.threshold - 0.15, 0.01)
        minimum_silence_ms = self.min_silence_duration_seconds * 1000
        minimum_speech_ms = self.min_speech_duration_seconds * 1000
        triggered = False
        speech_start_ms = 0.0
        silence_start_ms = 0.0
        raw_intervals: list[list[float]] = []
        for frame_idx, score in enumerate(trace.scores):
            frame_start_ms = frame_idx * trace.step_ms
            if score >= self.threshold and not triggered:
                triggered = True
                speech_start_ms = frame_start_ms
                silence_start_ms = 0.0
                continue
            if score >= self.threshold and silence_start_ms:
                silence_start_ms = 0.0
            if score < negative_threshold and triggered:
                if not silence_start_ms:
                    silence_start_ms = frame_start_ms
                if frame_start_ms - silence_start_ms < minimum_silence_ms:
                    continue
                if silence_start_ms - speech_start_ms > minimum_speech_ms:
                    raw_intervals.append([speech_start_ms, silence_start_ms])
                triggered = False
                silence_start_ms = 0.0
        if triggered and trace.duration_ms - speech_start_ms > minimum_speech_ms:
            raw_intervals.append([speech_start_ms, float(trace.duration_ms)])
        return self._get_silero_padded_intervals(raw_intervals, trace.duration_ms)

    def _get_silero_trace(self, audio: AudioSegment) -> VoiceActivityTrace:
        """Get frame-level scores from the Silero VAD model."""
        try:
            torch = import_torch()
            whisper_timestamped_transcribe = import_whisper_timestamped_transcribe()
        except ImportError as exc:
            raise TranscriptionError(
                "Silero VAD requires the optional transcription dependencies."
            ) from exc

        normalized_audio = (
            audio.set_channels(1).set_frame_rate(self.sample_rate).set_sample_width(2)
        )
        samples = np.asarray(normalized_audio.get_array_of_samples(), dtype=np.float32)
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
            model = self._load_silero_vad_model(torch, whisper_timestamped_transcribe)
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
        except (AssertionError, OSError, RuntimeError, ValueError) as exc:
            raise TranscriptionError(f"Unable to run Silero VAD: {exc}") from exc
        return VoiceActivityTrace(
            np.asarray(probabilities, dtype=np.float32),
            start_ms=16.0,
            step_ms=32.0,
            duration_ms=len(audio),
        )

    def _get_speech_intervals_from_probabilities(
        self, probabilities: list[float], duration_ms: int
    ) -> list[tuple[int, int]]:
        """Convert TEN frame probabilities into padded speech intervals.

        Arguments:
            probabilities: speech probability for each consecutive TEN frame
            duration_ms: duration of the original audio
        Returns:
            speech start and end offsets in milliseconds
        """
        if not probabilities or duration_ms <= 0:
            return []

        frame_duration_seconds = self.frame_size / self.sample_rate
        raw_intervals = self._get_unpadded_speech_frame_intervals(probabilities)
        padding_ms = round(self.padding_seconds * 1000)
        padded_intervals: list[tuple[int, int]] = []
        for start_idx, end_idx in raw_intervals:
            start_ms = max(
                0, round(start_idx * frame_duration_seconds * 1000) - padding_ms
            )
            end_ms = min(
                duration_ms, round(end_idx * frame_duration_seconds * 1000) + padding_ms
            )
            if padded_intervals and start_ms <= padded_intervals[-1][1]:
                previous_start_ms, previous_end_ms = padded_intervals[-1]
                padded_intervals[-1] = (previous_start_ms, max(previous_end_ms, end_ms))
            elif end_ms > start_ms:
                padded_intervals.append((start_ms, end_ms))
        return padded_intervals

    def _get_ten_trace(self, audio: AudioSegment) -> VoiceActivityTrace:
        """Get frame-level scores from the official TEN VAD runtime."""
        normalized_audio = (
            audio.set_channels(1).set_frame_rate(self.sample_rate).set_sample_width(2)
        )
        samples = np.array(normalized_audio.get_array_of_samples(), dtype=np.int16)
        if not len(samples):
            return VoiceActivityTrace(
                np.empty(0, dtype=np.float32),
                start_ms=self.frame_size / self.sample_rate * 500,
                step_ms=self.frame_size / self.sample_rate * 1000,
                duration_ms=0,
            )

        try:
            ten_vad = import_ten_vad()
            detector = ten_vad.TenVad(hop_size=self.frame_size, threshold=0.5)
        except (
            AssertionError,
            ImportError,
            NotImplementedError,
            OSError,
            RuntimeError,
        ) as exc:
            raise TranscriptionError(
                "Unable to initialize TEN VAD. Install the official ten-vad package "
                "after reviewing and accepting its additional license conditions."
            ) from exc

        probabilities: list[float] = []
        try:
            for frame_start_idx in range(0, len(samples), self.frame_size):
                frame = samples[frame_start_idx : frame_start_idx + self.frame_size]
                if len(frame) < self.frame_size:
                    frame = np.pad(frame, (0, self.frame_size - len(frame)))
                probability, _ = detector.process(frame.astype(np.int16, copy=False))
                if not isinstance(probability, int | float):
                    raise ValueError("TEN VAD returned a non-numeric probability.")
                probability = float(probability)
                if not 0 <= probability <= 1:
                    raise ValueError(
                        f"TEN VAD returned probability outside [0, 1]: {probability}"
                    )
                probabilities.append(probability)
        except (AssertionError, OSError, RuntimeError, ValueError) as exc:
            raise TranscriptionError(f"Unable to run TEN VAD: {exc}") from exc

        step_ms = self.frame_size / self.sample_rate * 1000
        return VoiceActivityTrace(
            np.asarray(probabilities, dtype=np.float32),
            start_ms=step_ms / 2,
            step_ms=step_ms,
            duration_ms=len(audio),
        )

    def _get_unpadded_speech_frame_intervals(
        self, probabilities: list[float]
    ) -> list[tuple[int, int]]:
        """Get unpadded speech intervals expressed as TEN frame indexes.

        Arguments:
            probabilities: speech probability for each consecutive TEN frame
        Returns:
            speech start and end frame indexes
        """
        frame_duration_seconds = self.frame_size / self.sample_rate
        minimum_silence_frames = max(
            1, ceil(self.min_silence_duration_seconds / frame_duration_seconds)
        )
        minimum_speech_frames = ceil(
            self.min_speech_duration_seconds / frame_duration_seconds
        )
        raw_intervals: list[tuple[int, int]] = []
        speech_start_idx: int | None = None
        silence_start_idx: int | None = None

        for frame_idx, probability in enumerate(probabilities):
            if probability >= self.threshold:
                if speech_start_idx is None:
                    speech_start_idx = frame_idx
                silence_start_idx = None
                continue
            if speech_start_idx is None:
                continue
            if silence_start_idx is None:
                silence_start_idx = frame_idx
            if frame_idx + 1 - silence_start_idx < minimum_silence_frames:
                continue
            if silence_start_idx - speech_start_idx >= minimum_speech_frames:
                raw_intervals.append((speech_start_idx, silence_start_idx))
            speech_start_idx = None
            silence_start_idx = None

        if speech_start_idx is None:
            return raw_intervals
        speech_end_idx = len(probabilities)
        if silence_start_idx is not None:
            speech_end_idx = silence_start_idx
        if speech_end_idx - speech_start_idx >= minimum_speech_frames:
            raw_intervals.append((speech_start_idx, speech_end_idx))
        return raw_intervals

    def _load_pyannote_vad_pipeline(self, torch: object) -> object:
        """Lazily load and configure pyannote voice activity detection.

        Arguments:
            torch: imported Torch module
        Returns:
            configured pyannote VAD pipeline
        """
        if self._pyannote_vad_pipeline is not None:
            return self._pyannote_vad_pipeline
        try:
            pyannote_audio = import_pyannote_audio()
            model_class = getattr(pyannote_audio, "Model")
            from_pretrained = cast(
                Callable[..., object], getattr(model_class, "from_pretrained")
            )
            model = from_pretrained(
                _PYANNOTE_VAD_MODEL_ID, revision=_PYANNOTE_VAD_MODEL_REVISION
            )
            if model is None:
                raise TranscriptionError(
                    "Unable to load the gated pyannote segmentation model. Accept "
                    "its Hugging Face conditions and configure a Hugging Face token."
                )
            pipeline_class = import_pyannote_audio_voice_activity_detection()
            pipeline = pipeline_class(segmentation=model)
            instantiate = cast(
                Callable[[Mapping[str, float]], object],
                getattr(pipeline, "instantiate"),
            )
            instantiate(
                {
                    "min_duration_off": self.min_silence_duration_seconds,
                    "min_duration_on": self.min_speech_duration_seconds,
                }
            )
            device = cast(Callable[[str], object], getattr(torch, "device"))("cpu")
            cast(Callable[[object], object], getattr(pipeline, "to"))(device)
        except ImportError as exc:
            raise TranscriptionError(
                "pyannote VAD requires the optional transcription dependencies."
            ) from exc
        except TranscriptionError:
            raise
        except Exception as exc:
            exception_name = type(exc).__name__
            message = str(exc).casefold()
            if exception_name in {
                "GatedRepoError",
                "RepositoryNotFoundError",
                "UnauthorizedError",
            } or any(token in message for token in ("401", "403", "gated repo")):
                raise TranscriptionError(
                    "Hugging Face has not authorized pyannote segmentation-3.0. "
                    "Accept the model conditions and configure a Hugging Face token."
                ) from exc
            raise TranscriptionError(
                f"Unable to initialize pyannote VAD: {exc}"
            ) from exc
        self._pyannote_vad_pipeline = pipeline
        return pipeline

    def _load_silero_vad_model(
        self, torch: object, whisper_timestamped_transcribe: object
    ) -> object:
        """Lazily load Whisper Timestamped's pinned Silero model.

        Arguments:
            torch: imported Torch module
            whisper_timestamped_transcribe: Whisper Timestamped transcribe module
        Returns:
            configured Silero model
        """
        if self._silero_vad_model is not None:
            return self._silero_vad_model

        get_vad_segments = cast(
            Callable[..., object],
            getattr(whisper_timestamped_transcribe, "get_vad_segments"),
        )
        from_numpy = cast(Callable[[np.ndarray], object], getattr(torch, "from_numpy"))
        get_vad_segments(
            from_numpy(np.zeros(512, dtype=np.float32)),
            sample_rate=self.sample_rate,
            output_sample=False,
            min_speech_duration=0.1,
            min_silence_duration=0.1,
            dilatation=0,
            method=f"silero:{_SILERO_MODEL_REVISION}",
        )
        models = getattr(whisper_timestamped_transcribe, "_silero_vad_model", None)
        if not isinstance(models, Mapping) or _SILERO_MODEL_REVISION not in models:
            raise TranscriptionError(
                "Whisper Timestamped did not expose its initialized Silero model."
            )
        self._silero_vad_model = models[_SILERO_MODEL_REVISION]
        return self._silero_vad_model


def _get_distribution_artifact_sha256(
    installed_distribution: Distribution, package_name: str
) -> str | None:
    """Hash installed runtime files belonging to one distribution package.

    Arguments:
        installed_distribution: installed package distribution metadata
        package_name: import package whose runtime files should be hashed
    Returns:
        SHA-256 digest of installed runtime files, if all can be identified
    """
    distribution_files = installed_distribution.files
    if distribution_files is None:
        return None
    package_parts = tuple(package_name.split("."))
    runtime_files = [
        package_path
        for package_path in distribution_files
        if package_path.parts[: len(package_parts)] == package_parts
        and "__pycache__" not in package_path.parts
        and package_path.suffix != ".pyc"
    ]
    if not runtime_files:
        return None

    digest = sha256()
    for package_path in sorted(runtime_files, key=lambda value: value.as_posix()):
        installed_path = Path(str(installed_distribution.locate_file(package_path)))
        if not installed_path.is_file():
            return None
        digest.update(package_path.as_posix().encode())
        digest.update(b"\0")
        try:
            with installed_path.open("rb") as file_handle:
                while chunk := file_handle.read(1024 * 1024):
                    digest.update(chunk)
        except OSError:
            return None
    return digest.hexdigest()


def _get_distribution_identity(
    distribution_name: str, package_name: str
) -> dict[str, str]:
    """Get an installed distribution's version, source, and artifact identity.

    Arguments:
        distribution_name: installed distribution name
        package_name: import package containing its runtime artifacts
    Returns:
        installed distribution identity, or an unavailable marker
    """
    try:
        installed_distribution = distribution(distribution_name)
    except PackageNotFoundError:
        return {"distribution": distribution_name, "version": "unavailable"}

    identity = {
        "distribution": distribution_name,
        "version": installed_distribution.version,
    }
    if artifact_sha256 := _get_distribution_artifact_sha256(
        installed_distribution, package_name
    ):
        identity["artifact_sha256"] = artifact_sha256

    direct_url_text = installed_distribution.read_text("direct_url.json")
    if direct_url_text is None:
        return identity
    try:
        direct_url = loads(direct_url_text)
    except (JSONDecodeError, TypeError):
        return identity
    if not isinstance(direct_url, Mapping):
        return identity
    if isinstance(source_url := direct_url.get("url"), str):
        identity["source_url"] = _sanitize_source_url(source_url)
    vcs_info = direct_url.get("vcs_info")
    if not isinstance(vcs_info, Mapping):
        return identity
    if isinstance(vcs := vcs_info.get("vcs"), str):
        identity["source_vcs"] = vcs
    if isinstance(commit_id := vcs_info.get("commit_id"), str):
        identity["source_commit"] = commit_id
    if isinstance(requested_revision := vcs_info.get("requested_revision"), str):
        identity["source_requested_revision"] = requested_revision
    return identity


def _get_silero_model_artifact_sha256() -> str | None:
    """Hash the cached Silero Torch Hub adapter and model artifacts.

    Returns:
        SHA-256 digest, if the pinned model is already available locally
    """
    torch_home_path = Path(environ.get("TORCH_HOME", "~/.cache/torch")).expanduser()
    repository_path = (
        torch_home_path / "hub" / f"snakers4_silero-vad_{_SILERO_MODEL_REVISION}"
    )
    runtime_root_path = repository_path / "src" / "silero_vad"
    hubconf_path = repository_path / "hubconf.py"
    if not hubconf_path.is_file() or not runtime_root_path.is_dir():
        return None
    runtime_paths = [
        path
        for path in runtime_root_path.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]
    if not runtime_paths:
        return None

    digest = sha256()
    for artifact_path in sorted(
        [hubconf_path, *runtime_paths], key=lambda value: value.as_posix()
    ):
        digest.update(artifact_path.relative_to(repository_path).as_posix().encode())
        digest.update(b"\0")
        try:
            with artifact_path.open("rb") as file_handle:
                while chunk := file_handle.read(1024 * 1024):
                    digest.update(chunk)
        except OSError:
            return None
    return digest.hexdigest()


def _sanitize_source_url(source_url: str) -> str:
    """Remove credentials, query, and fragment data from a package source URL.

    Arguments:
        source_url: source URL from PEP 610 distribution metadata
    Returns:
        sanitized source URL safe for cache metadata
    """
    parsed_url = urlsplit(source_url)
    hostname = parsed_url.hostname
    netloc = ""
    if hostname is not None:
        netloc = hostname
        if ":" in hostname:
            netloc = f"[{hostname}]"
        try:
            if parsed_url.port is not None:
                netloc = f"{netloc}:{parsed_url.port}"
        except ValueError:
            netloc = hostname
    return urlunsplit((parsed_url.scheme, netloc, parsed_url.path, "", ""))
