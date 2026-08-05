#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for splitting voice-activity traces into stable speech blocks."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from scinoephile.audio.transcription import (
    SpeechBlock,
    SpeechBlockSplitter,
    VoiceActivityTrace,
)


def _get_trace(
    duration_ms: int, active_intervals: Sequence[tuple[int, int]]
) -> VoiceActivityTrace:
    """Build a one-millisecond trace with selected active intervals.

    Arguments:
        duration_ms: source duration in milliseconds
        active_intervals: half-open active intervals in milliseconds
    Returns:
        synthetic voice-activity trace
    """
    scores = np.zeros(duration_ms, dtype=np.float32)
    for start_ms, end_ms in active_intervals:
        scores[start_ms:end_ms] = 1.0
    return VoiceActivityTrace(
        scores, start_ms=0.5, step_ms=1.0, duration_ms=duration_ms
    )


def test_splitter_cuts_exact_three_second_gap_at_midpoint():
    """An exact three-second internal gap should cut at its midpoint."""
    trace = _get_trace(7_000, [(1_000, 2_000), (5_000, 6_000)])

    blocks = SpeechBlockSplitter()(trace)

    assert blocks == [
        SpeechBlock(
            index=0,
            start_ms=0,
            end_ms=3_500,
            buffered_start_ms=0,
            buffered_end_ms=4_500,
        ),
        SpeechBlock(
            index=1,
            start_ms=3_500,
            end_ms=7_000,
            buffered_start_ms=2_500,
            buffered_end_ms=7_000,
        ),
    ]


def test_splitter_does_not_cut_2999_millisecond_gap():
    """A gap one millisecond below the threshold should remain one block."""
    trace = _get_trace(7_000, [(1_000, 2_000), (4_999, 6_000)])

    blocks = SpeechBlockSplitter()(trace)

    assert blocks == [
        SpeechBlock(
            index=0,
            start_ms=0,
            end_ms=7_000,
            buffered_start_ms=0,
            buffered_end_ms=7_000,
        )
    ]


def test_splitter_tiles_complete_source_and_clips_context():
    """Core blocks should tile the source while padded windows clip at its edges."""
    trace = _get_trace(12_000, [(1_000, 2_000), (6_000, 7_000), (10_000, 11_000)])

    blocks = SpeechBlockSplitter()(trace)

    assert blocks == [
        SpeechBlock(
            index=0,
            start_ms=0,
            end_ms=4_000,
            buffered_start_ms=0,
            buffered_end_ms=5_000,
        ),
        SpeechBlock(
            index=1,
            start_ms=4_000,
            end_ms=8_500,
            buffered_start_ms=3_000,
            buffered_end_ms=9_500,
        ),
        SpeechBlock(
            index=2,
            start_ms=8_500,
            end_ms=12_000,
            buffered_start_ms=7_500,
            buffered_end_ms=12_000,
        ),
    ]
    assert blocks[0].start_ms == 0
    assert blocks[-1].end_ms == trace.duration_ms
    assert all(
        left.end_ms == right.start_ms
        for left, right in zip(blocks, blocks[1:], strict=False)
    )


def test_splitter_ignores_leading_and_trailing_silence():
    """Only silence bounded by retained speech runs should create a cut."""
    trace = _get_trace(9_000, [(4_000, 5_000)])

    blocks = SpeechBlockSplitter()(trace)

    assert blocks == [
        SpeechBlock(
            index=0,
            start_ms=0,
            end_ms=9_000,
            buffered_start_ms=0,
            buffered_end_ms=9_000,
        )
    ]


def test_splitter_handles_silent_and_zero_duration_traces():
    """Silence should retain its timeline, while an empty timeline has no blocks."""
    silent_trace = _get_trace(5_000, [])
    zero_duration_trace = VoiceActivityTrace(
        np.empty(0, dtype=np.float32), start_ms=0.0, step_ms=1.0, duration_ms=0
    )
    splitter = SpeechBlockSplitter()

    assert splitter(silent_trace) == [
        SpeechBlock(
            index=0,
            start_ms=0,
            end_ms=5_000,
            buffered_start_ms=0,
            buffered_end_ms=5_000,
        )
    ]
    assert splitter(zero_duration_trace) == []
