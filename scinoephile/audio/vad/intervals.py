#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Conversion of voice-activity scores into timeline intervals."""

from __future__ import annotations

from collections.abc import Iterable
from math import ceil

import numpy as np

from .trace import VoiceActivityTrace

__all__ = [
    "get_active_frame_intervals",
    "get_frame_boundary_ms",
    "get_padded_intervals",
    "get_threshold_speech_intervals",
]


def get_active_frame_intervals(
    scores: np.ndarray,
    threshold: float,
    minimum_silence_frames: int,
    minimum_speech_frames: int,
) -> list[tuple[int, int]]:
    """Get significant half-open runs of active score frames.

    Arguments:
        scores: consecutive voice-activity scores
        threshold: minimum score treated as active
        minimum_silence_frames: inactive frames required to separate active runs
        minimum_speech_frames: active frames required to retain a run
    Returns:
        retained active frame-index ranges
    """
    runs: list[tuple[int, int]] = []
    run_start_idx: int | None = None
    for frame_idx, score in enumerate(scores):
        if score >= threshold:
            if run_start_idx is None:
                run_start_idx = frame_idx
            continue
        if run_start_idx is not None:
            runs.append((run_start_idx, frame_idx))
            run_start_idx = None
    if run_start_idx is not None:
        runs.append((run_start_idx, len(scores)))

    bridged_runs: list[tuple[int, int]] = []
    if runs:
        bridged_start_idx, bridged_end_idx = runs[0]
        for next_start_idx, next_end_idx in runs[1:]:
            if next_start_idx - bridged_end_idx < minimum_silence_frames:
                bridged_end_idx = next_end_idx
                continue
            bridged_runs.append((bridged_start_idx, bridged_end_idx))
            bridged_start_idx = next_start_idx
            bridged_end_idx = next_end_idx
        bridged_runs.append((bridged_start_idx, bridged_end_idx))

    return [
        (start_idx, end_idx)
        for start_idx, end_idx in bridged_runs
        if end_idx - start_idx >= minimum_speech_frames
    ]


def get_frame_boundary_ms(trace: VoiceActivityTrace, frame_idx: int) -> float:
    """Get a trace-frame boundary clipped to the source timeline.

    Arguments:
        trace: frame-level voice-activity score trace
        frame_idx: half-open frame boundary index
    Returns:
        boundary time in milliseconds
    """
    first_frame_start_ms = trace.start_ms - trace.step_ms / 2
    boundary_ms = first_frame_start_ms + frame_idx * trace.step_ms
    return max(0.0, min(float(trace.duration_ms), boundary_ms))


def get_padded_intervals(
    raw_intervals: Iterable[tuple[float, float]],
    duration_ms: int,
    padding_seconds: float,
) -> list[tuple[int, int]]:
    """Pad, clip, and merge millisecond intervals.

    Arguments:
        raw_intervals: unpadded start and end offsets in milliseconds
        duration_ms: duration of the source audio in milliseconds
        padding_seconds: context retained around each interval
    Returns:
        padded speech intervals
    """
    padding_ms = round(padding_seconds * 1000)
    intervals: list[tuple[int, int]] = []
    for raw_start_ms, raw_end_ms in raw_intervals:
        start_ms = max(0, round(raw_start_ms) - padding_ms)
        end_ms = min(duration_ms, round(raw_end_ms) + padding_ms)
        if intervals and start_ms <= intervals[-1][1]:
            intervals[-1] = (intervals[-1][0], max(intervals[-1][1], end_ms))
        elif end_ms > start_ms:
            intervals.append((start_ms, end_ms))
    return intervals


def get_threshold_speech_intervals(
    trace: VoiceActivityTrace,
    *,
    threshold: float,
    min_speech_duration_seconds: float,
    min_silence_duration_seconds: float,
    padding_seconds: float,
) -> list[tuple[int, int]]:
    """Convert a score trace into configured binary speech intervals.

    Arguments:
        trace: frame-level voice-activity score trace
        threshold: minimum score treated as speech
        min_speech_duration_seconds: minimum retained active-run duration
        min_silence_duration_seconds: minimum silence separating active runs
        padding_seconds: context retained around each interval
    Returns:
        speech start and end offsets in milliseconds
    """
    if not len(trace) or trace.duration_ms <= 0:
        return []
    minimum_silence_frames = ceil(min_silence_duration_seconds * 1000 / trace.step_ms)
    minimum_speech_frames = ceil(min_speech_duration_seconds * 1000 / trace.step_ms)
    frame_intervals = get_active_frame_intervals(
        trace.scores, threshold, minimum_silence_frames, minimum_speech_frames
    )
    raw_intervals = (
        (get_frame_boundary_ms(trace, start_idx), get_frame_boundary_ms(trace, end_idx))
        for start_idx, end_idx in frame_intervals
    )
    return get_padded_intervals(raw_intervals, trace.duration_ms, padding_seconds)
