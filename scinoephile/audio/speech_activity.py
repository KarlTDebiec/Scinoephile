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

from .transcription import TranscribedSegment, WhisperTranscriber

if TYPE_CHECKING:
    from pydub import AudioSegment

__all__ = [
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
    ) -> Sequence[SpeechInterval]:
        """Detect speech intervals.

        Arguments:
            audio: audio segment to inspect
            offset_ms: offset to add to returned intervals
        Returns:
            detected speech intervals
        """


class SileroSpeechActivityDetector:
    """Detect speech intervals using Silero VAD."""

    def __init__(
        self,
        model: Any | None = None,
        cache_dir_path: Path | None = None,
        merge_gap_ms: int = 150,
        min_duration_ms: int = 100,
        sample_rate: int = 16000,
    ):
        """Initialize.

        Arguments:
            model: optional loaded Silero model
            cache_dir_path: optional cache directory for raw speech intervals
            merge_gap_ms: merge speech intervals separated by at most this gap
            min_duration_ms: discard speech intervals shorter than this duration
            sample_rate: sample rate to use for Silero input audio
        """
        self._model = model
        self.cache_dir_path = None
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)
        self.merge_gap_ms = merge_gap_ms
        self.min_duration_ms = min_duration_ms
        self.sample_rate = sample_rate

    def __call__(
        self,
        audio: AudioSegment,
        *,
        offset_ms: int = 0,
    ) -> list[SpeechInterval]:
        """Detect speech intervals.

        Arguments:
            audio: audio segment to inspect
            offset_ms: offset to add to returned intervals
        Returns:
            detected speech intervals
        """
        intervals = self.get_cached_speech_intervals(audio)
        if intervals is None:
            intervals = self._get_uncached_speech_intervals(audio)
            self._cache_speech_intervals(audio, intervals)

        shifted_intervals = [interval.shifted(offset_ms) for interval in intervals]
        return get_speech_intervals_cleaned(
            shifted_intervals,
            merge_gap_ms=self.merge_gap_ms,
            min_duration_ms=self.min_duration_ms,
            clip_start_ms=offset_ms,
            clip_end_ms=offset_ms + len(audio),
        )

    @property
    def model(self) -> Any:
        """Get the cached Silero model, loading it if needed."""
        if self._model is None:
            load_silero_vad, _ = self._get_silero_functions()
            self._model = load_silero_vad()
        return self._model

    def get_cached_speech_intervals(
        self, audio: AudioSegment
    ) -> list[SpeechInterval] | None:
        """Get cached raw speech intervals for audio if available.

        Arguments:
            audio: audio used for cache-key generation
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
            )
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
        cache_key = f"{audio_sha256}_silero_sample_rate-{self.sample_rate}"
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
            sampling_rate=self.sample_rate,
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
        transcriber: Callable[[AudioSegment], list[TranscribedSegment]] | None = None,
        cache_dir_path: Path | None = None,
        merge_gap_ms: int = 150,
        min_duration_ms: int = 100,
    ):
        """Initialize.

        Arguments:
            transcriber: callable that returns transcription segments
            cache_dir_path: optional cache directory for raw transcription segments
            merge_gap_ms: merge speech intervals separated by at most this gap
            min_duration_ms: discard speech intervals shorter than this duration
        """
        if transcriber is None:
            transcriber = WhisperTranscriber(cache_dir_path=cache_dir_path)
        self.transcriber = transcriber
        self.merge_gap_ms = merge_gap_ms
        self.min_duration_ms = min_duration_ms

    def __call__(
        self,
        audio: AudioSegment,
        *,
        offset_ms: int = 0,
    ) -> list[SpeechInterval]:
        """Detect speech intervals.

        Arguments:
            audio: audio segment to inspect
            offset_ms: offset to add to returned intervals
        Returns:
            detected speech intervals
        """
        intervals = get_speech_intervals_from_segments(
            self.transcriber(audio),
            offset_ms=offset_ms,
        )
        return get_speech_intervals_cleaned(
            intervals,
            merge_gap_ms=self.merge_gap_ms,
            min_duration_ms=self.min_duration_ms,
            clip_start_ms=offset_ms,
            clip_end_ms=offset_ms + len(audio),
        )


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
