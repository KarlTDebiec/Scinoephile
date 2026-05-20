#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Speech activity intervals detected from audio."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

import numpy as np

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.subtitles import Series, Subtitle

from .transcription import TranscribedSegment
from .transcription.whisper_transcriber import (
    DEFAULT_WHISPER_MODEL_NAME,
    WhisperTranscriber,
)

if TYPE_CHECKING:
    from pydub import AudioSegment

__all__ = [
    "PreprocessedSpeechActivityDetector",
    "SileroSpeechActivityDetector",
    "SpeechActivityDetector",
    "SpeechInterval",
    "WhisperSpeechActivityDetector",
    "get_speech_intervals_cleaned",
    "get_speech_intervals_from_segments",
    "get_speech_overlap_duration",
    "get_speech_series_from_intervals",
]

_SILERO_EXTRA_MESSAGE = (
    "Silero VAD support requires optional transcription dependencies. "
    "Install scinoephile with the 'transcription' extra."
)


@dataclass(frozen=True, order=True)
class SpeechInterval:
    """Time interval containing speech."""

    start_ms: int
    """Start time in milliseconds."""
    end_ms: int
    """End time in milliseconds."""

    def __post_init__(self):
        """Validate interval bounds."""
        if self.start_ms < 0:
            raise ValueError("Speech interval start must be non-negative")
        if self.end_ms <= self.start_ms:
            raise ValueError("Speech interval end must be greater than start")

    @property
    def duration_ms(self) -> int:
        """Interval duration in milliseconds."""
        return self.end_ms - self.start_ms

    def clipped(self, *, start_ms: int, end_ms: int) -> SpeechInterval | None:
        """Get interval clipped to provided bounds.

        Arguments:
            start_ms: inclusive clip start in milliseconds
            end_ms: exclusive clip end in milliseconds
        Returns:
            clipped interval, or None if no duration remains
        """
        clipped_start_ms = max(self.start_ms, start_ms)
        clipped_end_ms = min(self.end_ms, end_ms)
        if clipped_end_ms <= clipped_start_ms:
            return None
        return SpeechInterval(start_ms=clipped_start_ms, end_ms=clipped_end_ms)

    def shifted(self, offset_ms: int) -> SpeechInterval:
        """Get interval shifted by an offset.

        Arguments:
            offset_ms: milliseconds by which to shift the interval
        Returns:
            shifted interval
        """
        return SpeechInterval(
            start_ms=self.start_ms + offset_ms,
            end_ms=self.end_ms + offset_ms,
        )


class SpeechActivityDetector(Protocol):
    """Callable interface for detecting speech in an audio segment."""

    def __call__(
        self,
        audio: AudioSegment,
        *,
        offset_ms: int = 0,
        cache_audio: AudioSegment | None = None,
    ) -> Sequence[SpeechInterval]:
        """Detect speech intervals.

        Arguments:
            audio: audio segment to inspect
            offset_ms: offset to add to returned intervals
            cache_audio: optional original audio to use for cache keys
        Returns:
            detected speech intervals
        """


class _SpeechTranscriber(Protocol):
    """Callable interface for transcribing speech activity audio."""

    def __call__(
        self,
        audio: AudioSegment,
        *,
        cache_audio: AudioSegment | None = None,
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio segment to transcribe
            cache_audio: optional original audio to use for cache keys
        Returns:
            transcribed segments
        """


class PreprocessedSpeechActivityDetector:
    """Speech activity detector with audio preprocessing."""

    def __init__(
        self,
        *,
        speech_detector: SpeechActivityDetector,
        audio_preprocessor: Callable[[AudioSegment], AudioSegment],
    ):
        """Initialize.

        Arguments:
            speech_detector: speech activity detector to run after preprocessing
            audio_preprocessor: audio preprocessing callable
        """
        self.speech_detector = speech_detector
        self.audio_preprocessor = audio_preprocessor

    def __call__(
        self,
        audio: AudioSegment,
        *,
        offset_ms: int = 0,
        cache_audio: AudioSegment | None = None,
    ) -> Sequence[SpeechInterval]:
        """Detect speech activity after preprocessing audio.

        Arguments:
            audio: audio segment to inspect
            offset_ms: offset to add to returned intervals
            cache_audio: optional original audio to use for cache keys
        Returns:
            detected speech intervals
        """
        if cache_audio is None:
            cache_audio = audio
        cached_intervals = self.get_cached_speech_intervals(
            cache_audio,
            offset_ms=offset_ms,
        )
        if cached_intervals is not None:
            return cached_intervals

        return self.speech_detector(
            self.audio_preprocessor(audio),
            offset_ms=offset_ms,
            cache_audio=cache_audio,
        )

    def get_cached_speech_intervals(
        self,
        audio: AudioSegment,
        *,
        offset_ms: int = 0,
    ) -> Sequence[SpeechInterval] | None:
        """Get cached speech activity from the wrapped detector if available.

        Arguments:
            audio: audio used for cache-key generation
            offset_ms: offset to add to returned intervals
        Returns:
            cached speech intervals, if present
        """
        get_cached_speech_intervals = getattr(
            self.speech_detector,
            "get_cached_speech_intervals",
            None,
        )
        if get_cached_speech_intervals is None:
            return None
        return get_cached_speech_intervals(audio, offset_ms=offset_ms)


class SileroSpeechActivityDetector:
    """Detect speech intervals using Silero VAD."""

    def __init__(
        self,
        model: Any | None = None,
        cache_dir_path: Path | None = None,
        sample_rate: int = 16000,
        threshold: float = 0.5,
    ):
        """Initialize.

        Arguments:
            model: optional loaded Silero model
            cache_dir_path: optional cache directory for raw speech intervals
            sample_rate: sample rate to use for Silero input audio
            threshold: Silero speech probability threshold
        """
        self._model = model
        self.cache_dir_path = None
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)
        self.sample_rate = sample_rate
        if threshold < 0.0 or threshold > 1.0:
            raise ValueError("threshold must be between 0.0 and 1.0")
        self.threshold = threshold

    def __call__(
        self,
        audio: AudioSegment,
        *,
        offset_ms: int = 0,
        cache_audio: AudioSegment | None = None,
    ) -> list[SpeechInterval]:
        """Detect speech intervals.

        Arguments:
            audio: audio segment to inspect
            offset_ms: offset to add to returned intervals
            cache_audio: optional original audio to use for cache keys
        Returns:
            detected speech intervals
        """
        if cache_audio is None:
            cache_audio = audio

        cached_intervals = self.get_cached_speech_intervals(
            cache_audio,
            offset_ms=offset_ms,
        )
        if cached_intervals is not None:
            return cached_intervals

        intervals = self._get_uncached_speech_intervals(audio)
        self._cache_speech_intervals(cache_audio, intervals)
        return [interval.shifted(offset_ms) for interval in intervals]

    @property
    def model(self) -> Any:
        """Get the cached Silero model, loading it if needed."""
        if self._model is None:
            load_silero_vad, _ = self._get_silero_functions()
            self._model = load_silero_vad()
        return self._model

    def get_cached_speech_intervals(
        self,
        audio: AudioSegment,
        *,
        offset_ms: int = 0,
    ) -> list[SpeechInterval] | None:
        """Get cached raw speech intervals for audio if available.

        Arguments:
            audio: audio used for cache-key generation
            offset_ms: offset to add to returned intervals
        Returns:
            cached speech intervals, if present
        """
        cache_path = self._get_cache_path(audio)
        if cache_path is None or not cache_path.exists():
            return None

        with cache_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        cache_path.touch()
        return [
            SpeechInterval(
                start_ms=interval["start_ms"],
                end_ms=interval["end_ms"],
            ).shifted(offset_ms)
            for interval in data
        ]

    def _cache_speech_intervals(
        self, audio: AudioSegment, intervals: Sequence[SpeechInterval]
    ):
        """Cache raw speech intervals for audio.

        Arguments:
            audio: audio used for cache-key generation
            intervals: intervals to cache
        """
        cache_path = self._get_cache_path(audio)
        if cache_path is None:
            return

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("w", encoding="utf-8") as file:
            json.dump(
                [
                    {"start_ms": interval.start_ms, "end_ms": interval.end_ms}
                    for interval in intervals
                ],
                file,
                indent=2,
            )

    def _get_audio_tensor(self, audio: AudioSegment) -> Any:
        """Get normalized mono audio tensor for Silero.

        Arguments:
            audio: audio segment to convert
        Returns:
            normalized mono float tensor
        """
        normalized_audio = (
            audio.set_channels(1).set_frame_rate(self.sample_rate).set_sample_width(2)
        )
        samples = np.array(normalized_audio.get_array_of_samples()).astype(np.float32)
        samples /= 32768.0
        torch = self._get_torch_module()
        return torch.from_numpy(samples)

    def _get_cache_path(self, audio: AudioSegment) -> Path | None:
        """Get cache path based on hash of audio data and detector configuration.

        Arguments:
            audio: audio used to derive the cache key
        Returns:
            path to cache file
        """
        if self.cache_dir_path is None:
            return None

        normalized_audio = (
            audio.set_channels(1).set_frame_rate(self.sample_rate).set_sample_width(2)
        )
        audio_sha256 = hashlib.sha256(normalized_audio.raw_data).hexdigest()
        cache_key = (
            f"{audio_sha256}_silero_sample_rate-{self.sample_rate}"
            f"_threshold-{self.threshold!r}"
        )
        cache_sha256 = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{cache_sha256}.json"

    def _get_uncached_speech_intervals(
        self, audio: AudioSegment
    ) -> list[SpeechInterval]:
        """Get speech intervals without consulting or updating the cache.

        Arguments:
            audio: audio segment to inspect
        Returns:
            detected speech intervals
        """
        _, get_speech_timestamps = self._get_silero_functions()
        timestamps = get_speech_timestamps(
            self._get_audio_tensor(audio),
            self.model,
            threshold=self.threshold,
            sampling_rate=self.sample_rate,
            min_speech_duration_ms=0,
            min_silence_duration_ms=0,
            speech_pad_ms=0,
            return_seconds=True,
        )
        return [
            SpeechInterval(
                start_ms=round(timestamp["start"] * 1000),
                end_ms=round(timestamp["end"] * 1000),
            )
            for timestamp in timestamps
            if timestamp["end"] > timestamp["start"]
        ]

    @staticmethod
    def _get_silero_functions() -> tuple[Any, Any]:
        """Import Silero VAD functions on demand."""
        try:
            from silero_vad import (  # noqa: PLC0415
                get_speech_timestamps,
                load_silero_vad,
            )
        except ImportError as exc:
            raise ImportError(_SILERO_EXTRA_MESSAGE) from exc
        return load_silero_vad, get_speech_timestamps

    @staticmethod
    def _get_torch_module() -> Any:
        """Import torch on demand."""
        try:
            import torch  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(_SILERO_EXTRA_MESSAGE) from exc
        return torch


class WhisperSpeechActivityDetector:
    """Detect speech intervals from Whisper transcription segments."""

    def __init__(
        self,
        transcriber: _SpeechTranscriber | None = None,
        cache_dir_path: Path | None = None,
        model_name: str = DEFAULT_WHISPER_MODEL_NAME,
    ):
        """Initialize.

        Arguments:
            transcriber: callable that returns transcription segments
            cache_dir_path: optional cache directory for raw transcription segments
            model_name: Whisper model name to use when creating a transcriber
        """
        if transcriber is None:
            transcriber = WhisperTranscriber(
                cache_dir_path=cache_dir_path,
                model_name=model_name,
            )
        self.transcriber = transcriber

    def __call__(
        self,
        audio: AudioSegment,
        *,
        offset_ms: int = 0,
        cache_audio: AudioSegment | None = None,
    ) -> list[SpeechInterval]:
        """Detect speech intervals.

        Arguments:
            audio: audio segment to inspect
            offset_ms: offset to add to returned intervals
            cache_audio: optional original audio to use for cache keys
        Returns:
            detected speech intervals
        """
        return get_speech_intervals_from_segments(
            self._get_transcription(audio, cache_audio=cache_audio),
            offset_ms=offset_ms,
        )

    def get_cached_speech_intervals(
        self,
        audio: AudioSegment,
        *,
        offset_ms: int = 0,
    ) -> list[SpeechInterval] | None:
        """Get cached speech intervals from cached transcription if available.

        Arguments:
            audio: audio used for cache-key generation
            offset_ms: offset to add to returned intervals
        Returns:
            cached speech intervals, if present
        """
        get_cached_transcription = getattr(
            self.transcriber,
            "get_cached_transcription",
            None,
        )
        if get_cached_transcription is None:
            return None
        cached_segments = get_cached_transcription(audio)
        if cached_segments is None:
            return None
        return get_speech_intervals_from_segments(cached_segments, offset_ms=offset_ms)

    def _get_transcription(
        self,
        audio: AudioSegment,
        *,
        cache_audio: AudioSegment | None = None,
    ) -> list[TranscribedSegment]:
        """Get transcription segments for audio.

        Arguments:
            audio: audio segment to transcribe
            cache_audio: optional original audio to use for cache keys
        Returns:
            transcribed segments
        """
        if cache_audio is None:
            return self.transcriber(audio)
        return self.transcriber(audio, cache_audio=cache_audio)


def get_speech_intervals_cleaned(
    intervals: Sequence[SpeechInterval],
    *,
    merge_gap_ms: int,
    min_duration_ms: int,
    clip_start_ms: int | None = None,
    clip_end_ms: int | None = None,
) -> list[SpeechInterval]:
    """Clean up speech intervals.

    Arguments:
        intervals: raw speech intervals
        merge_gap_ms: merge speech intervals separated by at most this gap
        min_duration_ms: discard speech intervals shorter than this duration
        clip_start_ms: optional inclusive clip start in milliseconds
        clip_end_ms: optional exclusive clip end in milliseconds
    Returns:
        cleaned speech intervals
    """
    if merge_gap_ms < 0:
        raise ValueError("Merge gap must be non-negative")
    if min_duration_ms < 0:
        raise ValueError("Minimum duration must be non-negative")

    merged_intervals: list[SpeechInterval] = []
    for interval in sorted(intervals):
        if not merged_intervals:
            merged_intervals.append(interval)
            continue

        previous = merged_intervals[-1]
        if interval.start_ms - previous.end_ms <= merge_gap_ms:
            merged_intervals[-1] = SpeechInterval(
                start_ms=previous.start_ms,
                end_ms=max(previous.end_ms, interval.end_ms),
            )
        else:
            merged_intervals.append(interval)

    cleaned_intervals: list[SpeechInterval] = []
    for interval in merged_intervals:
        clipped_interval = interval
        if clip_start_ms is not None or clip_end_ms is not None:
            start_ms = clip_start_ms
            if start_ms is None:
                start_ms = 0
            end_ms = clip_end_ms
            if end_ms is None:
                end_ms = interval.end_ms
            clipped_interval = interval.clipped(start_ms=start_ms, end_ms=end_ms)
            if clipped_interval is None:
                continue

        if clipped_interval.duration_ms >= min_duration_ms:
            cleaned_intervals.append(clipped_interval)

    return cleaned_intervals


def get_speech_intervals_from_segments(
    segments: Sequence[TranscribedSegment],
    *,
    offset_ms: int = 0,
) -> list[SpeechInterval]:
    """Get speech intervals from transcription segments.

    Arguments:
        segments: transcription segments with second-based timings
        offset_ms: milliseconds to add to each interval
    Returns:
        speech intervals in milliseconds
    """
    intervals: list[SpeechInterval] = []
    for segment in segments:
        if not segment.text.strip():
            continue
        start_ms = offset_ms + round(segment.start * 1000)
        end_ms = offset_ms + round(segment.end * 1000)
        if end_ms <= start_ms:
            continue
        intervals.append(SpeechInterval(start_ms=start_ms, end_ms=end_ms))
    return intervals


def get_speech_series_from_intervals(intervals: Sequence[SpeechInterval]) -> Series:
    """Get an empty-text subtitle series from speech intervals.

    Arguments:
        intervals: speech intervals to represent as subtitle events
    Returns:
        subtitle series with one empty-text event per speech interval
    """
    return Series(
        events=[
            Subtitle(start=interval.start_ms, end=interval.end_ms, text="")
            for interval in intervals
        ]
    )


def get_speech_overlap_duration(
    start_ms: int,
    end_ms: int,
    intervals: Sequence[SpeechInterval],
) -> int:
    """Get duration of speech covered by a window.

    Arguments:
        start_ms: inclusive window start in milliseconds
        end_ms: exclusive window end in milliseconds
        intervals: speech intervals to compare
    Returns:
        covered speech duration in milliseconds
    """
    overlap_duration_ms = 0
    for interval in intervals:
        overlap_start_ms = max(start_ms, interval.start_ms)
        overlap_end_ms = min(end_ms, interval.end_ms)
        if overlap_end_ms > overlap_start_ms:
            overlap_duration_ms += overlap_end_ms - overlap_start_ms
    return overlap_duration_ms
