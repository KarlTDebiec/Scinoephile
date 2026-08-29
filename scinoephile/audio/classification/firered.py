#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""FireRed spoken-language identification and multi-label audio-event detection."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from logging import getLogger
from math import ceil, isfinite
from pathlib import Path
from typing import TYPE_CHECKING, cast

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.audio.waveform import to_mono_int16
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.cache.runtime import get_distribution_identity
from scinoephile.core.dependencies.transcription import (
    import_firered_aed,
    import_firered_lid,
)
from scinoephile.core.exceptions import DependencyError
from scinoephile.core.ml import get_huggingface_snapshot_dir_path

from .cache import AudioClassificationCache
from .exceptions import AudioClassificationInferenceError
from .models import (
    AudioEvent,
    AudioEventDetectionResult,
    AudioEventSpan,
    LanguageIdentificationResult,
    LanguageSpan,
)

__all__ = ["FireRedAudioEventDetector", "FireRedLanguageIdentifier"]

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)

_LANGUAGE_MODEL_ID = "FireRedTeam/FireRedLID"
"""Official FireRed spoken-language identification model."""
_LANGUAGE_MODEL_REVISION = "1bb4d285c8456429385d9c0810300df4297bc11b"
"""Pinned FireRedLID model revision."""
_EVENT_MODEL_ID = "FireRedTeam/FireRedVAD"
"""Official FireRed multi-label VAD repository."""
_EVENT_MODEL_REVISION = "7990aaccc6b7aec1e527743bd30201f2c4a03b8c"
"""Pinned FireRedVAD model revision."""
_WAVEFORM_CHANNELS = 1
"""Channels supplied to FireRed inference."""
_WAVEFORM_FRAME_RATE = 16_000
"""Sample rate required by FireRed feature extraction."""
_WAVEFORM_SAMPLE_WIDTH = 2
"""PCM sample width required by FireRed feature extraction."""


class FireRedLanguageIdentifier:
    """Identify spoken language over selected source intervals."""

    def __init__(
        self,
        cache_root_path: Path | None,
        *,
        batch_size: int = 8,
        minimum_window_seconds: float = 0.5,
        maximum_window_seconds: float = 30.0,
        use_gpu: bool = False,
        use_half: bool = False,
        overwrite_cache: bool = False,
    ):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache results
            batch_size: utterance windows classified together
            minimum_window_seconds: shorter source intervals are omitted
            maximum_window_seconds: longer source intervals are subdivided
            use_gpu: whether to use CUDA
            use_half: whether to use half precision on CUDA
            overwrite_cache: whether to replace matching cache entries
        Raises:
            ValueError: if batch size or window durations are invalid
        """
        if batch_size <= 0:
            raise ValueError("Language-identification batch size must be positive.")
        if not isfinite(minimum_window_seconds) or minimum_window_seconds <= 0.0:
            raise ValueError("Minimum language window must be positive.")
        if not isfinite(maximum_window_seconds):
            raise ValueError("Maximum language window must be finite.")
        if maximum_window_seconds < 2 * minimum_window_seconds:
            raise ValueError(
                "Maximum language window must be at least twice the minimum."
            )
        self.batch_size = batch_size
        """Utterance windows classified together."""
        self.minimum_window_seconds = minimum_window_seconds
        """Minimum speech-window duration sent to FireRedLID."""
        self.maximum_window_seconds = maximum_window_seconds
        """Maximum speech-window duration sent to FireRedLID."""
        self.use_gpu = use_gpu
        """Whether FireRedLID uses CUDA."""
        self.use_half = use_half
        """Whether FireRedLID uses half precision on CUDA."""
        self._cache = AudioClassificationCache(
            cache_root_path,
            AudioCacheNamespace.CLASSIFICATION_LANGUAGE,
            overwrite_cache,
        )
        """Source-wide language-identification cache."""
        self._model: object | None = None
        """Lazily loaded FireRedLID model."""

    def __call__(
        self,
        audio: AudioSegment,
        intervals_ms: Sequence[tuple[int, int]],
        *,
        offset_seconds: float = 0.0,
    ) -> LanguageIdentificationResult:
        """Identify language in selected audio intervals.

        Arguments:
            audio: complete source audio
            intervals_ms: ordered source intervals in milliseconds
            offset_seconds: source-timeline offset added to result spans
        Returns:
            source-timeline language identification spans
        Raises:
            DependencyError: if optional dependencies are missing
            AudioClassificationInferenceError: if model loading or inference fails
            ValueError: if the offset or source intervals are invalid
        """
        if not isfinite(offset_seconds) or offset_seconds < 0.0:
            raise ValueError("Language-identification offset must be non-negative.")
        windows = self._get_windows(intervals_ms, len(audio))
        cache_identity = self._get_cache_identity(windows, offset_seconds)
        cached_result = self._cache.load(
            audio, cache_identity, LanguageIdentificationResult
        )
        if cached_result is not None:
            return cached_result
        if not windows:
            result = LanguageIdentificationResult(spans=[])
            self._cache.save(audio, cache_identity, result)
            return result

        samples = to_mono_int16(audio, _WAVEFORM_FRAME_RATE)
        model = self._get_model()
        spans: list[LanguageSpan] = []
        try:
            process = getattr(model, "process")
            for batch_start in range(0, len(windows), self.batch_size):
                batch_windows = windows[batch_start : batch_start + self.batch_size]
                utterance_ids = [
                    f"window_{batch_start + index:06d}"
                    for index in range(len(batch_windows))
                ]
                waveforms = [
                    [
                        _WAVEFORM_FRAME_RATE,
                        samples[
                            round(start * _WAVEFORM_FRAME_RATE) : round(
                                end * _WAVEFORM_FRAME_RATE
                            )
                        ],
                    ]
                    for start, end in batch_windows
                ]
                raw_results = process(utterance_ids, waveforms)
                results_by_id = {
                    str(item.get("uttid")): item
                    for item in cast(Sequence[Mapping[str, object]], raw_results)
                }
                for utterance_id, (start, end) in zip(
                    utterance_ids, batch_windows, strict=True
                ):
                    raw_result = results_by_id.get(utterance_id)
                    if raw_result is None:
                        raise AudioClassificationInferenceError(
                            f"FireRedLID returned no result for {utterance_id}."
                        )
                    language = _normalize_language(str(raw_result.get("lang", "")))
                    if not language:
                        raise AudioClassificationInferenceError(
                            f"FireRedLID returned no language for {utterance_id}."
                        )
                    spans.append(
                        LanguageSpan(
                            start=start + offset_seconds,
                            end=end + offset_seconds,
                            language=language,
                            confidence=_get_float(raw_result.get("confidence")),
                        )
                    )
        except AudioClassificationInferenceError:
            raise
        except Exception as exc:
            raise AudioClassificationInferenceError(
                f"FireRed language identification failed: {exc}"
            ) from exc

        result = LanguageIdentificationResult(spans=spans)
        self._cache.save(audio, cache_identity, result)
        return result

    def _get_cache_identity(
        self, windows: Sequence[tuple[float, float]], offset_seconds: float
    ) -> CacheIdentity:
        """Get exact model identity and result-affecting settings.

        Arguments:
            windows: source-relative windows submitted to FireRedLID
            offset_seconds: source-timeline offset added to result spans
        Returns:
            configuration identifying reusable language-identification output
        """
        return {
            "model_id": _LANGUAGE_MODEL_ID,
            "model_revision": _LANGUAGE_MODEL_REVISION,
            "offset_seconds": offset_seconds,
            "runtime": get_distribution_identity("fireredasr2s"),
            "analysis_windows": [[start, end] for start, end in windows],
            "use_gpu": self.use_gpu,
            "use_half": self.use_half,
            "waveform_channels": _WAVEFORM_CHANNELS,
            "waveform_frame_rate": _WAVEFORM_FRAME_RATE,
            "waveform_sample_width": _WAVEFORM_SAMPLE_WIDTH,
        }

    def _get_model(self) -> object:
        """Lazily download and load FireRedLID.

        Returns:
            loaded FireRedLID model
        Raises:
            DependencyError: if optional dependencies are missing
            AudioClassificationInferenceError: if the model cannot be loaded
        """
        if self._model is not None:
            return self._model
        try:
            model_dir_path = get_huggingface_snapshot_dir_path(
                _LANGUAGE_MODEL_ID,
                _LANGUAGE_MODEL_REVISION,
                ("cmvn.ark", "dict.txt", "model.pth.tar"),
            )
            model_cls, config_cls = import_firered_lid()
            config_factory = cast(Callable[..., object], config_cls)
            model_factory = cast(
                Callable[[str | Path, object], object],
                getattr(model_cls, "from_pretrained"),
            )
            config = config_factory(use_gpu=self.use_gpu, use_half=self.use_half)
            self._model = model_factory(model_dir_path, config)
        except DependencyError:
            raise
        except Exception as exc:
            raise AudioClassificationInferenceError(
                f"Unable to load FireRedLID: {exc}"
            ) from exc
        return self._model

    def _get_windows(
        self, intervals_ms: Sequence[tuple[int, int]], audio_duration_ms: int
    ) -> tuple[tuple[float, float], ...]:
        """Validate, clip, and subdivide selected audio intervals.

        Arguments:
            intervals_ms: ordered source intervals in milliseconds
            audio_duration_ms: duration of the source audio in milliseconds
        Returns:
            clipped and subdivided intervals in seconds
        Raises:
            ValueError: if intervals are unordered or have nonpositive duration
        """
        windows = []
        previous_end_ms = 0
        for start_ms, end_ms in intervals_ms:
            if start_ms < previous_end_ms or end_ms <= start_ms:
                raise ValueError("Language-identification intervals must be ordered.")
            previous_end_ms = end_ms
            clipped_start = max(0.0, start_ms / 1000)
            clipped_end = min(audio_duration_ms / 1000, end_ms / 1000)
            duration = clipped_end - clipped_start
            if duration < self.minimum_window_seconds:
                continue
            window_count = ceil(duration / self.maximum_window_seconds)
            window_duration = duration / window_count
            for window_idx in range(window_count):
                window_start = clipped_start + window_idx * window_duration
                if window_idx == window_count - 1:
                    window_end = clipped_end
                else:
                    window_end = clipped_start + (window_idx + 1) * window_duration
                windows.append((window_start, window_end))
        return tuple(windows)


class FireRedAudioEventDetector:
    """Detect independent speech, singing, and music intervals with FireRed mVAD."""

    def __init__(
        self,
        cache_root_path: Path | None,
        *,
        speech_threshold: float = 0.4,
        singing_threshold: float = 0.5,
        music_threshold: float = 0.5,
        use_gpu: bool = False,
        overwrite_cache: bool = False,
    ):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache
            speech_threshold: minimum speech detection score
            singing_threshold: minimum singing detection score
            music_threshold: minimum music detection score
            use_gpu: whether to use CUDA
            overwrite_cache: whether to replace matching cache entries
        Raises:
            ValueError: if a detection threshold is outside [0, 1]
        """
        for name, threshold in (
            ("speech", speech_threshold),
            ("singing", singing_threshold),
            ("music", music_threshold),
        ):
            if not isfinite(threshold) or not 0.0 <= threshold <= 1.0:
                raise ValueError(f"FireRed {name} threshold must be in [0, 1].")
        self.thresholds = {
            AudioEvent.SPEECH: speech_threshold,
            AudioEvent.SINGING: singing_threshold,
            AudioEvent.MUSIC: music_threshold,
        }
        """Independent decision thresholds by event type."""
        self.use_gpu = use_gpu
        """Whether FireRed mVAD uses CUDA."""
        self._cache = AudioClassificationCache(
            cache_root_path, AudioCacheNamespace.CLASSIFICATION_EVENT, overwrite_cache
        )
        """Source-wide audio-event cache."""
        self._model: object | None = None
        """Lazily loaded FireRed mVAD model."""

    def __call__(
        self, audio: AudioSegment, *, offset_seconds: float = 0.0
    ) -> AudioEventDetectionResult:
        """Detect source-wide independent speech, singing, and music spans.

        Arguments:
            audio: complete source audio
            offset_seconds: source-timeline offset added to result spans
        Returns:
            source-timeline audio event spans
        Raises:
            DependencyError: if optional dependencies are missing
            AudioClassificationInferenceError: if model loading or inference fails
            ValueError: if the offset is negative
        """
        if not isfinite(offset_seconds) or offset_seconds < 0.0:
            raise ValueError("Audio-event offset must be non-negative.")
        cache_identity = self._get_cache_identity(offset_seconds)
        cached_result = self._cache.load(
            audio, cache_identity, AudioEventDetectionResult
        )
        if cached_result is not None:
            return cached_result
        try:
            samples = to_mono_int16(audio, _WAVEFORM_FRAME_RATE)
            result, _ = getattr(self._get_model(), "detect")(samples)
            timestamps = cast(
                Mapping[str, Sequence[Sequence[float]]], result["event2timestamps"]
            )
            missing_events = [
                event.value for event in AudioEvent if event.value not in timestamps
            ]
            if missing_events:
                raise AudioClassificationInferenceError(
                    f"FireRed audio-event detection omitted {missing_events}."
                )
            spans = sorted(
                (
                    AudioEventSpan(
                        start=float(start) + offset_seconds,
                        end=float(end) + offset_seconds,
                        event=event,
                    )
                    for event in AudioEvent
                    for start, end in timestamps.get(event.value, ())
                ),
                key=lambda span: (span.start, span.end, span.event),
            )
        except AudioClassificationInferenceError:
            raise
        except Exception as exc:
            raise AudioClassificationInferenceError(
                f"FireRed audio-event detection failed: {exc}"
            ) from exc
        output = AudioEventDetectionResult(spans=spans)
        self._cache.save(audio, cache_identity, output)
        return output

    def _get_cache_identity(self, offset_seconds: float) -> CacheIdentity:
        """Get exact model identity and result-affecting settings.

        Arguments:
            offset_seconds: source-timeline offset added to result spans
        Returns:
            configuration identifying reusable audio-event output
        """
        return {
            "model_id": _EVENT_MODEL_ID,
            "model_revision": _EVENT_MODEL_REVISION,
            "offset_seconds": offset_seconds,
            "runtime": get_distribution_identity("fireredasr2s"),
            "thresholds": {
                event.value: threshold for event, threshold in self.thresholds.items()
            },
            "use_gpu": self.use_gpu,
            "waveform_channels": _WAVEFORM_CHANNELS,
            "waveform_frame_rate": _WAVEFORM_FRAME_RATE,
            "waveform_sample_width": _WAVEFORM_SAMPLE_WIDTH,
        }

    def _get_model(self) -> object:
        """Lazily download and load FireRed multi-label VAD.

        Returns:
            loaded FireRed multi-label VAD model
        Raises:
            DependencyError: if optional dependencies are missing
            AudioClassificationInferenceError: if the model cannot be loaded
        """
        if self._model is not None:
            return self._model
        try:
            model_root = get_huggingface_snapshot_dir_path(
                _EVENT_MODEL_ID,
                _EVENT_MODEL_REVISION,
                ("AED/cmvn.ark", "AED/model.pth.tar"),
            )
            model_cls, config_cls = import_firered_aed()
            config_factory = cast(Callable[..., object], config_cls)
            model_factory = cast(
                Callable[[str | Path, object], object],
                getattr(model_cls, "from_pretrained"),
            )
            config = config_factory(
                use_gpu=self.use_gpu,
                speech_threshold=self.thresholds[AudioEvent.SPEECH],
                singing_threshold=self.thresholds[AudioEvent.SINGING],
                music_threshold=self.thresholds[AudioEvent.MUSIC],
            )
            self._model = model_factory(model_root / "AED", config)
        except DependencyError:
            raise
        except Exception as exc:
            raise AudioClassificationInferenceError(
                f"Unable to load FireRed multi-label VAD: {exc}"
            ) from exc
        return self._model


def _get_float(value: object) -> float:
    """Convert a FireRed scalar result to float with a clear failure.

    Arguments:
        value: raw FireRed scalar value
    Returns:
        floating-point value
    Raises:
        TypeError: if the value is not numeric text or a numeric scalar
    """
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise TypeError(f"FireRed returned a nonnumeric scalar: {value!r}")
    return float(value)


def _normalize_language(language: str) -> str:
    """Normalize FireRed's space-separated Chinese dialect labels.

    Arguments:
        language: raw FireRed language label
    Returns:
        normalized language label
    """
    parts = language.strip().lower().replace("_", "-").split()
    if not parts:
        return ""
    return "-".join(parts)
