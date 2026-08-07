#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reference-free display timing for CTC-aligned merged subtitles."""

from __future__ import annotations

from scinoephile.analysis.transcription_alignment import SubtitleTimingSettings
from scinoephile.analysis.transcription_timing import get_display_intervals
from scinoephile.audio.transcription import TranscribedSegment

__all__ = ["get_segments_with_display_timing"]


def get_segments_with_display_timing(
    segments: list[TranscribedSegment],
    audio_duration_seconds: float,
    settings: SubtitleTimingSettings | None = None,
) -> list[TranscribedSegment]:
    """Pad CTC speech intervals into neighboring silence without overlap.

    Word timings remain the reference-free estimate of actual speech. Segment
    start and end times become SRT display intervals. When neighboring requested
    padding collides, the intervening interval is divided at the midpoint between
    the adjacent speech bounds.

    Arguments:
        segments: chronologically ordered CTC-aligned merged subtitles
        audio_duration_seconds: complete source duration
        settings: optional display-timing settings
    Returns:
        copied segments with adjusted display bounds and unchanged word timings
    Raises:
        ValueError: if source duration or segment speech timing is invalid
    """
    speech_intervals = [_get_speech_interval(segment) for segment in segments]
    display_intervals = get_display_intervals(
        speech_intervals, audio_duration_seconds, settings
    )

    return [
        segment.model_copy(deep=True, update={"start": start, "end": end})
        for segment, (start, end) in zip(segments, display_intervals, strict=True)
    ]


def _get_speech_interval(segment: TranscribedSegment) -> tuple[float, float]:
    """Get one segment's CTC speech interval independent of display padding."""
    start_seconds = segment.start
    end_seconds = segment.end
    if segment.words:
        start_seconds = segment.words[0].start
        end_seconds = segment.words[-1].end
    if end_seconds <= start_seconds:
        raise ValueError("Merged subtitle speech duration must be positive.")
    return start_seconds, end_seconds
