#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Speech activity intervals detected from audio."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from .transcription import TranscribedSegment, WhisperTranscriber

if TYPE_CHECKING:
    from pydub import AudioSegment

__all__ = [
    "SpeechActivityDetector",
    "SpeechInterval",
    "WhisperSpeechActivityDetector",
    "get_speech_intervals_cleaned",
    "get_speech_intervals_from_segments",
    "get_speech_overlap_duration",
]


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


class WhisperSpeechActivityDetector:
    """Detect speech intervals from Whisper transcription segments."""

    def __init__(
        self,
        transcriber: Callable[[AudioSegment], list[TranscribedSegment]] | None = None,
        merge_gap_ms: int = 150,
        min_duration_ms: int = 100,
    ):
        """Initialize.

        Arguments:
            transcriber: callable that returns transcription segments
            merge_gap_ms: merge speech intervals separated by at most this gap
            min_duration_ms: discard speech intervals shorter than this duration
        """
        self.transcriber = transcriber or WhisperTranscriber()
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
