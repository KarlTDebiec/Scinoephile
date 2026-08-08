#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""FireRed spoken-language identification and multi-label audio-event detection."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from importlib.metadata import PackageNotFoundError, version
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, cast

import numpy as np

from scinoephile.core.dependencies.transcription import (
    import_firered_aed,
    import_firered_lid,
    import_huggingface_hub,
)

from .cache import AudioClassificationCache
from .exceptions import (
    AudioClassificationDependencyError,
    AudioClassificationInferenceError,
)
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

_FIRERED_RUNTIME_REVISION = "4e7d9aaf4482a47cec1724807026b9b151926eb5"
"""Pinned FireRedASR2S runtime revision."""
_LANGUAGE_MODEL_ID = "FireRedTeam/FireRedLID"
"""Official FireRed spoken-language identification model."""
_LANGUAGE_MODEL_REVISION = "1bb4d285c8456429385d9c0810300df4297bc11b"
"""Pinned FireRedLID model revision."""
_EVENT_MODEL_ID = "FireRedTeam/FireRedVAD"
"""Official FireRed multi-label VAD repository."""
_EVENT_MODEL_REVISION = "7990aaccc6b7aec1e527743bd30201f2c4a03b8c"
"""Pinned FireRedVAD model revision."""
_FRAME_RATE = 16_000
"""Sample rate required by FireRed feature extraction."""
_SAMPLE_WIDTH = 2
"""PCM sample width required by FireRed feature extraction."""


class FireRedLanguageIdentifier:
    """Identify spoken language over VAD-derived source intervals."""

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
            minimum_window_seconds: shorter VAD speech intervals are omitted
            maximum_window_seconds: longer VAD speech intervals are subdivided
            use_gpu: whether to use CUDA
            use_half: whether to use half precision on CUDA
            overwrite_cache: whether to replace matching cache entries
        """
        if batch_size <= 0:
            raise ValueError("Language-identification batch size must be positive.")
        if minimum_window_seconds <= 0.0:
            raise ValueError("Minimum language window must be positive.")
        if maximum_window_seconds < minimum_window_seconds:
            raise ValueError(
                "Maximum language window must not be shorter than the minimum."
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
            cache_root_path, "language", overwrite_cache
        )
        """Source-wide language-identification cache."""
        self._model: object | None = None
        """Lazily loaded FireRedLID model."""

    def __call__(
        self,
        audio: AudioSegment,
        speech_intervals_ms: Sequence[tuple[int, int]],
        *,
        offset_seconds: float = 0.0,
    ) -> LanguageIdentificationResult:
        """Identify language in VAD-derived speech windows."""
        if offset_seconds < 0.0:
            raise ValueError("Language-identification offset must be non-negative.")
        windows = self._get_windows(speech_intervals_ms, len(audio))
        metadata = self._get_cache_metadata(windows, offset_seconds)
        cached_result = self._cache.load(audio, metadata, LanguageIdentificationResult)
        if cached_result is not None:
            return cached_result
        if not windows:
            result = LanguageIdentificationResult(spans=[])
            self._cache.save(audio, metadata, result)
            return result

        samples = _get_samples(audio)
        model = self._get_model()
        spans = []
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
                        _FRAME_RATE,
                        samples[round(start * _FRAME_RATE) : round(end * _FRAME_RATE)],
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
                        continue
                    language = _normalize_language(str(raw_result.get("lang", "")))
                    if not language:
                        continue
                    spans.append(
                        LanguageSpan(
                            start=start + offset_seconds,
                            end=end + offset_seconds,
                            language=language,
                            confidence=_get_float(raw_result.get("confidence", 0.0)),
                        )
                    )
        except Exception as exc:
            raise AudioClassificationInferenceError(
                f"FireRed language identification failed: {exc}"
            ) from exc

        result = LanguageIdentificationResult(spans=spans)
        self._cache.save(audio, metadata, result)
        return result

    def _get_model(self) -> object:
        """Lazily download and load FireRedLID."""
        if self._model is not None:
            return self._model
        try:
            huggingface_hub = import_huggingface_hub()
            model_dir = huggingface_hub.snapshot_download(
                repo_id=_LANGUAGE_MODEL_ID,
                revision=_LANGUAGE_MODEL_REVISION,
                allow_patterns=("cmvn.ark", "dict.txt", "model.pth.tar"),
            )
            model_cls, config_cls = import_firered_lid()
            config_factory = cast(Callable[..., object], config_cls)
            model_factory = cast(
                Callable[[str | Path, object], object],
                getattr(model_cls, "from_pretrained"),
            )
            config = config_factory(use_gpu=self.use_gpu, use_half=self.use_half)
            self._model = model_factory(model_dir, config)
        except ImportError as exc:
            raise AudioClassificationDependencyError(str(exc)) from exc
        except Exception as exc:
            raise AudioClassificationInferenceError(
                f"Unable to load FireRedLID: {exc}"
            ) from exc
        return self._model

    def _get_cache_metadata(
        self, windows: Sequence[tuple[float, float]], offset_seconds: float
    ) -> Mapping[str, object]:
        """Get exact model identity and result-affecting settings."""
        return {
            "batch_size": self.batch_size,
            "maximum_window_seconds": self.maximum_window_seconds,
            "minimum_window_seconds": self.minimum_window_seconds,
            "model_id": _LANGUAGE_MODEL_ID,
            "model_revision": _LANGUAGE_MODEL_REVISION,
            "offset_seconds": offset_seconds,
            "runtime_revision": _FIRERED_RUNTIME_REVISION,
            "runtime_version": _get_runtime_version(),
            "speech_windows": [[start, end] for start, end in windows],
            "use_gpu": self.use_gpu,
            "use_half": self.use_half,
        }

    def _get_windows(
        self, speech_intervals_ms: Sequence[tuple[int, int]], audio_duration_ms: int
    ) -> tuple[tuple[float, float], ...]:
        """Validate, clip, and subdivide VAD speech intervals."""
        windows = []
        previous_end_ms = 0
        for start_ms, end_ms in speech_intervals_ms:
            if start_ms < previous_end_ms or end_ms <= start_ms:
                raise ValueError("Language speech intervals must be ordered.")
            previous_end_ms = end_ms
            clipped_start = max(0.0, start_ms / 1000)
            clipped_end = min(audio_duration_ms / 1000, end_ms / 1000)
            window_start = clipped_start
            while clipped_end - window_start >= self.minimum_window_seconds:
                window_end = min(
                    clipped_end, window_start + self.maximum_window_seconds
                )
                windows.append((window_start, window_end))
                window_start = window_end
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
        """Initialize."""
        for name, threshold in (
            ("speech", speech_threshold),
            ("singing", singing_threshold),
            ("music", music_threshold),
        ):
            if not 0.0 <= threshold <= 1.0:
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
            cache_root_path, "audio_event", overwrite_cache
        )
        """Source-wide audio-event cache."""
        self._model: object | None = None
        """Lazily loaded FireRed mVAD model."""

    def __call__(
        self, audio: AudioSegment, *, offset_seconds: float = 0.0
    ) -> AudioEventDetectionResult:
        """Detect source-wide independent speech, singing, and music spans."""
        if offset_seconds < 0.0:
            raise ValueError("Audio-event offset must be non-negative.")
        metadata = self._get_cache_metadata(offset_seconds)
        cached_result = self._cache.load(audio, metadata, AudioEventDetectionResult)
        if cached_result is not None:
            return cached_result
        try:
            result, _ = getattr(self._get_model(), "detect")(_get_samples(audio))
            timestamps = cast(
                Mapping[str, Sequence[Sequence[float]]], result["event2timestamps"]
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
                    if float(end) > float(start)
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
        self._cache.save(audio, metadata, output)
        return output

    def _get_model(self) -> object:
        """Lazily download and load FireRed multi-label VAD."""
        if self._model is not None:
            return self._model
        try:
            huggingface_hub = import_huggingface_hub()
            model_root = Path(
                huggingface_hub.snapshot_download(
                    repo_id=_EVENT_MODEL_ID,
                    revision=_EVENT_MODEL_REVISION,
                    allow_patterns=("AED/cmvn.ark", "AED/model.pth.tar"),
                )
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
        except ImportError as exc:
            raise AudioClassificationDependencyError(str(exc)) from exc
        except Exception as exc:
            raise AudioClassificationInferenceError(
                f"Unable to load FireRed multi-label VAD: {exc}"
            ) from exc
        return self._model

    def _get_cache_metadata(self, offset_seconds: float) -> Mapping[str, object]:
        """Get exact model identity and result-affecting settings."""
        return {
            "model_id": _EVENT_MODEL_ID,
            "model_revision": _EVENT_MODEL_REVISION,
            "offset_seconds": offset_seconds,
            "runtime_revision": _FIRERED_RUNTIME_REVISION,
            "runtime_version": _get_runtime_version(),
            "thresholds": {
                event.value: threshold for event, threshold in self.thresholds.items()
            },
            "use_gpu": self.use_gpu,
        }


def _get_runtime_version() -> str:
    """Get the installed FireRed runtime version for cache identity."""
    try:
        return version("fireredasr2s")
    except PackageNotFoundError as exc:
        raise AudioClassificationDependencyError(
            "Audio classification requires FireRedASR2S. Install Scinoephile "
            "with the 'transcription' extra."
        ) from exc


def _get_samples(audio: AudioSegment) -> np.ndarray:
    """Convert audio to the mono 16 kHz signed PCM required by FireRed."""
    inference_audio = (
        audio.set_channels(1)
        .set_frame_rate(_FRAME_RATE)
        .set_sample_width(_SAMPLE_WIDTH)
    )
    return np.asarray(inference_audio.get_array_of_samples(), dtype=np.int16)


def _normalize_language(language: str) -> str:
    """Normalize FireRed's space-separated Chinese dialect labels."""
    parts = language.strip().lower().replace("_", "-").split()
    if not parts:
        return ""
    return "-".join(parts)


def _get_float(value: object) -> float:
    """Convert a FireRed scalar result to float with a clear failure."""
    if not isinstance(value, (int, float, str)):
        raise TypeError(f"FireRed returned a nonnumeric scalar: {value!r}")
    return float(value)
