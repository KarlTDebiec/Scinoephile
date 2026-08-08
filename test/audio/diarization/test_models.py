#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for typed speaker diarization results."""

from __future__ import annotations

from pytest import raises

from scinoephile.audio.diarization import SpeakerDiarizationResult, SpeakerTurn
from scinoephile.audio.transcription import TranscribedSegment, TranscribedWord


def test_result_preserves_overlaps_and_assigns_exclusive_speakers():
    """Regular overlaps should coexist with deterministic ASR word assignment."""
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
    segment = TranscribedSegment(
        id=0,
        seek=0,
        start=0.1,
        end=1.3,
        text="AB",
        words=[
            TranscribedWord(text="A", start=0.1, end=0.4, confidence=1.0),
            TranscribedWord(text="B", start=0.9, end=1.3, confidence=1.0),
        ],
    )

    assigned = result.assign_speakers([segment])

    assert len(result.turns) == 2
    assert result.turns[0].end > result.turns[1].start
    assert [word.speaker for word in assigned[0].words or []] == [
        "SPEAKER_00",
        "SPEAKER_01",
    ]
    assert [word.speaker_turn_start for word in assigned[0].words or []] == [0.0, 1.0]
    assert [word.speaker_turn_end for word in assigned[0].words or []] == [1.0, 2.0]
    assert [word.speaker for word in segment.words or []] == [None, None]


def test_assignment_uses_source_timeline_offset():
    """Block-relative words should reconcile against source-relative turns."""
    result = SpeakerDiarizationResult(
        turns=[SpeakerTurn(start=10.0, end=12.0, speaker="SPEAKER_07")],
        exclusive_turns=[SpeakerTurn(start=10.0, end=12.0, speaker="SPEAKER_07")],
    )
    segment = TranscribedSegment(
        id=0,
        seek=0,
        start=0.2,
        end=0.5,
        text="A",
        words=[TranscribedWord(text="A", start=0.2, end=0.5, confidence=1.0)],
    )

    assigned = result.assign_speakers([segment], offset_seconds=10.0)

    assert (assigned[0].words or [])[0].speaker == "SPEAKER_07"
    assert (assigned[0].words or [])[0].speaker_turn_start == 10.0
    assert (assigned[0].words or [])[0].speaker_turn_end == 12.0


def test_reconciliation_splits_safe_internal_speaker_transitions():
    """Reconciliation should split mapped words without mutating the input."""
    result = SpeakerDiarizationResult(
        turns=[],
        exclusive_turns=[
            SpeakerTurn(start=0.0, end=0.5, speaker="SPEAKER_00"),
            SpeakerTurn(start=0.5, end=1.5, speaker="SPEAKER_01"),
        ],
    )
    segment = TranscribedSegment(
        id=8,
        seek=0,
        start=0.1,
        end=1.2,
        text="甲乙",
        words=[
            TranscribedWord(text="甲", start=0.2, end=0.4, confidence=1.0),
            TranscribedWord(text="乙", start=0.7, end=1.0, confidence=1.0),
        ],
    )

    reconciled = result.reconcile_transcription([segment])

    assert [item.id for item in reconciled] == [0, 1]
    assert [item.text for item in reconciled] == ["甲", "乙"]
    assert [(item.start, item.end) for item in reconciled] == [(0.1, 0.4), (0.7, 1.2)]
    assert [(item.words or [])[0].speaker for item in reconciled] == [
        "SPEAKER_00",
        "SPEAKER_01",
    ]
    assert [word.speaker for word in segment.words or []] == [None, None]


def test_reconciliation_keeps_segment_when_word_text_cannot_map_safely():
    """Reconciliation should retain one unit when splitting would alter text."""
    result = SpeakerDiarizationResult(
        turns=[],
        exclusive_turns=[
            SpeakerTurn(start=0.0, end=0.5, speaker="SPEAKER_00"),
            SpeakerTurn(start=0.5, end=1.5, speaker="SPEAKER_01"),
        ],
    )
    segment = TranscribedSegment(
        id=0,
        seek=0,
        start=0.1,
        end=1.2,
        text="one two",
        words=[
            TranscribedWord(text="one", start=0.2, end=0.4, confidence=1.0),
            TranscribedWord(text="two", start=0.7, end=1.0, confidence=1.0),
        ],
    )

    reconciled = result.reconcile_transcription([segment])

    assert len(reconciled) == 1
    assert reconciled[0].text == "one two"
    assert [word.speaker for word in reconciled[0].words or []] == [
        "SPEAKER_00",
        "SPEAKER_01",
    ]


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
