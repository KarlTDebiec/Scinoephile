#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for typed speaker diarization results."""

from __future__ import annotations

from pytest import raises

from scinoephile.audio.diarization import SpeakerDiarizationResult, SpeakerTurn


def test_result_preserves_overlaps_and_queries_exclusive_speakers():
    """Regular overlaps should coexist with deterministic interval lookup."""
    result = SpeakerDiarizationResult(
        turns=[
            SpeakerTurn(start=0.0, end=1.2, speaker="SPEAKER_00"),
            SpeakerTurn(start=0.8, end=2.0, speaker="SPEAKER_01"),
        ],
        exclusive_turns=[
            SpeakerTurn(start=0.0, end=1.0, speaker="SPEAKER_00"),
            SpeakerTurn(start=1.0, end=2.0, speaker="SPEAKER_01"),
        ],
    )
    assert len(result.turns) == 2
    assert result.turns[0].end > result.turns[1].start
    assert result.get_exclusive_speaker(0.1, 0.4) == "SPEAKER_00"
    assert result.get_exclusive_speaker(0.9, 1.3) == "SPEAKER_01"
    assert result.get_exclusive_speaker(2.0, 2.1) is None


def test_result_rejects_overlapping_exclusive_turns():
    """Exclusive diarization should reject ambiguous overlapping intervals."""
    with raises(ValueError, match="must not overlap"):
        SpeakerDiarizationResult(
            turns=[],
            exclusive_turns=[
                SpeakerTurn(start=0.0, end=1.1, speaker="SPEAKER_00"),
                SpeakerTurn(start=1.0, end=2.0, speaker="SPEAKER_01"),
            ],
        )
