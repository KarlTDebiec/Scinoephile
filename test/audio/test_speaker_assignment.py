#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of speaker assignment across diarization and transcription results."""

from __future__ import annotations

from pytest import raises

from scinoephile.audio.diarization import SpeakerDiarizationResult, SpeakerTurn
from scinoephile.audio.speaker_assignment import assign_speakers
from scinoephile.audio.transcription import TranscribedSegment, TranscribedWord


def test_assign_speakers_uses_exclusive_turns_without_mutating_input():
    """Assign the greatest-overlap exclusive speaker to copied words."""
    diarization = SpeakerDiarizationResult(
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

    assigned = assign_speakers(diarization, [segment])

    assert [word.speaker for word in assigned[0].words or []] == [
        "SPEAKER_00",
        "SPEAKER_01",
    ]
    assert [word.speaker for word in segment.words or []] == [None, None]


def test_assign_speakers_uses_source_timeline_offset():
    """Reconcile block-relative words against source-relative turns."""
    diarization = SpeakerDiarizationResult(
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

    assigned = assign_speakers(diarization, [segment], offset_seconds=10.0)

    assert (assigned[0].words or [])[0].speaker == "SPEAKER_07"


def test_assign_speakers_rejects_negative_offset():
    """Reject an audio-slice offset before assigning speakers."""
    diarization = SpeakerDiarizationResult(turns=[], exclusive_turns=[])

    with raises(ValueError, match="cannot be negative"):
        assign_speakers(diarization, [], offset_seconds=-1.0)
