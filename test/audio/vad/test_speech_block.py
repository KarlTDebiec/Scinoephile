#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of splitting VAD traces into stable complete-source audio blocks."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pytest

from scinoephile.audio.vad import (
    SpeechBlock,
    SpeechBlockSettings,
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


def test_splitter_separates_exact_three_second_gap():
    """An exact three-second internal gap should separate audio blocks."""
    trace = _get_trace(7_000, [(1_000, 2_000), (5_000, 6_000)])

    blocks = SpeechBlockSplitter()(trace)

    assert blocks == [
        SpeechBlock(index=0, start_ms=0, end_ms=3_500),
        SpeechBlock(index=1, start_ms=3_500, end_ms=7_000),
    ]


def test_splitter_does_not_cut_2999_millisecond_gap():
    """A gap one millisecond below the threshold should remain one block."""
    trace = _get_trace(7_000, [(1_000, 2_000), (4_999, 6_000)])

    blocks = SpeechBlockSplitter()(trace)

    assert blocks == [SpeechBlock(index=0, start_ms=0, end_ms=7_000)]


def test_splitter_partitions_complete_audio_at_gap_midpoints():
    """Blocks should cover complete audio with hard cuts at gap midpoints."""
    trace = _get_trace(12_000, [(1_000, 2_000), (6_000, 7_000), (10_000, 11_000)])

    blocks = SpeechBlockSplitter()(trace)

    assert blocks == [
        SpeechBlock(index=0, start_ms=0, end_ms=4_000),
        SpeechBlock(index=1, start_ms=4_000, end_ms=8_500),
        SpeechBlock(index=2, start_ms=8_500, end_ms=12_000),
    ]


def test_splitter_includes_leading_and_trailing_silence():
    """A lone speech group should leave the complete source in one block."""
    trace = _get_trace(9_000, [(4_000, 5_000)])

    blocks = SpeechBlockSplitter()(trace)

    assert blocks == [SpeechBlock(index=0, start_ms=0, end_ms=9_000)]


def test_splitter_handles_silent_and_zero_duration_traces():
    """Silent audio should remain covered while empty audio has no blocks."""
    silent_trace = _get_trace(5_000, [])
    zero_duration_trace = VoiceActivityTrace(
        np.empty(0, dtype=np.float32), start_ms=0.0, step_ms=1.0, duration_ms=0
    )
    splitter = SpeechBlockSplitter()

    assert splitter(silent_trace) == [SpeechBlock(index=0, start_ms=0, end_ms=5_000)]
    assert splitter(zero_duration_trace) == []


def test_splitter_bridges_short_silence_before_filtering_short_speech():
    """Brief score dips should not split speech into discarded fragments."""
    trace = _get_trace(1_000, [(100, 300), (350, 550)])

    blocks = SpeechBlockSplitter()(trace)

    assert blocks == [SpeechBlock(index=0, start_ms=0, end_ms=1_000)]


def test_splitter_preserves_minimum_silence_before_filtering_short_speech():
    """A score dip reaching the bridge threshold should remain meaningful."""
    trace = _get_trace(1_000, [(100, 300), (400, 600)])

    blocks = SpeechBlockSplitter()(trace)

    assert blocks == [SpeechBlock(index=0, start_ms=0, end_ms=1_000)]


def test_speech_block_settings_reject_negative_minimum_silence():
    """The short-silence bridge duration should be non-negative."""
    with pytest.raises(
        ValueError, match="Minimum block-planning silence must be non-negative."
    ):
        SpeechBlockSettings(min_silence_duration_seconds=-0.1)
