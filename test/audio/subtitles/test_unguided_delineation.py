#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for deterministic unguided subtitle delineation."""

from __future__ import annotations

from collections.abc import Sequence

from pytest import approx

from scinoephile.audio.subtitles.delineation import (
    UnguidedBoundaryEvidence,
    UnguidedDelineationSettings,
    UnguidedDelineator,
)
from scinoephile.audio.transcription import TranscribedSegment, TranscribedWord


def _get_segment(
    words: Sequence[TranscribedWord],
    *,
    segment_id: int = 0,
    start: float | None = None,
    end: float | None = None,
    text: str | None = None,
) -> TranscribedSegment:
    """Build a transcription segment from synthetic timed words.

    Arguments:
        words: timed words belonging to the segment
        segment_id: segment identifier
        start: explicit segment start, or None to use the first word start
        end: explicit segment end, or None to use the last word end
        text: explicit segment text, or None to concatenate word text
    Returns:
        synthetic transcribed segment
    """
    if start is None:
        start = words[0].start
    if end is None:
        end = words[-1].end
    if text is None:
        text = "".join(word.text for word in words)
    return TranscribedSegment(
        id=segment_id, seek=0, start=start, end=end, text=text, words=list(words)
    )


def _get_two_word_boundary(
    *,
    first_text: str = "甲",
    pause_seconds: float = 0.1,
    following_voice_activity_score: float | None = 1.0,
    first_speaker: str | None = "SPEAKER_00",
    second_speaker: str | None = "SPEAKER_00",
) -> UnguidedBoundaryEvidence:
    """Delineate two words and return their only boundary evidence.

    Arguments:
        first_text: outgoing word text
        pause_seconds: silence between the words
        following_voice_activity_score: outgoing word's following-gap VAD score
        first_speaker: outgoing word speaker
        second_speaker: incoming word speaker
    Returns:
        evidence for the boundary between the two words
    """
    first = TranscribedWord(
        text=first_text,
        start=0.0,
        end=0.4,
        confidence=1.0,
        following_voice_activity_score=following_voice_activity_score,
        speaker=first_speaker,
    )
    second = TranscribedWord(
        text="乙",
        start=0.4 + pause_seconds,
        end=0.8 + pause_seconds,
        confidence=1.0,
        speaker=second_speaker,
    )

    result = UnguidedDelineator()([_get_segment([first, second])])

    assert len(result.boundaries) == 1
    return result.boundaries[0]


def test_delineation_preserves_word_text_and_uses_word_timings():
    """Selected subtitles should reconstruct every word with exact edge timings."""
    words = [
        TranscribedWord(text="甲", start=0.2, end=0.5, confidence=1.0),
        TranscribedWord(text="乙", start=0.6, end=0.9, confidence=1.0),
        TranscribedWord(text="丙", start=1.0, end=1.3, confidence=1.0),
        TranscribedWord(text="丁", start=1.4, end=1.7, confidence=1.0),
    ]
    settings = UnguidedDelineationSettings(
        target_characters=2,
        max_characters=2,
        preferred_min_duration_seconds=0.0,
        preferred_max_duration_seconds=10.0,
        max_duration_seconds=20.0,
        max_characters_per_second=100.0,
        forced_gap_seconds=100.0,
    )

    result = UnguidedDelineator(settings)([_get_segment(words)])

    assert [segment.text for segment in result.segments] == ["甲乙", "丙丁"]
    assert [(segment.start, segment.end) for segment in result.segments] == [
        (0.2, 0.9),
        (1.0, 1.7),
    ]
    assert "".join(segment.text for segment in result.segments) == "甲乙丙丁"
    assert [
        word.text for segment in result.segments for word in segment.words or []
    ] == ["甲", "乙", "丙", "丁"]
    assert [boundary.index for boundary in result.boundaries if boundary.selected] == [
        2
    ]


def test_boundary_evidence_uses_outgoing_end_and_scores_independent_signals():
    """Pause, low VAD, speaker change, and punctuation should each add evidence."""
    baseline = _get_two_word_boundary()
    long_pause = _get_two_word_boundary(pause_seconds=0.8)
    low_vad = _get_two_word_boundary(following_voice_activity_score=0.0)
    speaker_change = _get_two_word_boundary(second_speaker="SPEAKER_01")
    punctuation = _get_two_word_boundary(first_text="甲。")

    assert baseline.time == approx(0.4)
    assert baseline.pause_seconds == approx(0.1)
    assert baseline.following_voice_activity_score == approx(1.0)
    assert long_pause.pause_score > baseline.pause_score
    assert long_pause.total_score > baseline.total_score
    assert low_vad.voice_activity_score > baseline.voice_activity_score
    assert low_vad.total_score > baseline.total_score
    assert speaker_change.speaker_change is True
    assert speaker_change.speaker_change_score > baseline.speaker_change_score
    assert speaker_change.total_score > baseline.total_score
    assert punctuation.punctuation_score > baseline.punctuation_score
    assert punctuation.total_score > baseline.total_score


def test_forced_pause_selects_boundary_without_speaker_evidence():
    """A sufficiently long pause should split subtitles without known speakers."""
    words = [
        TranscribedWord(text="甲", start=0.0, end=0.2, confidence=1.0),
        TranscribedWord(text="乙", start=0.25, end=0.45, confidence=1.0),
        TranscribedWord(text="丙", start=1.5, end=1.7, confidence=1.0),
        TranscribedWord(text="丁", start=1.75, end=1.95, confidence=1.0),
    ]
    settings = UnguidedDelineationSettings(
        target_characters=9,
        max_characters=20,
        preferred_min_duration_seconds=0.0,
        preferred_max_duration_seconds=10.0,
        max_duration_seconds=20.0,
        max_characters_per_second=100.0,
        forced_gap_seconds=0.8,
    )

    result = UnguidedDelineator(settings)([_get_segment(words)])

    selected = [boundary for boundary in result.boundaries if boundary.selected]
    assert len(selected) == 1
    assert selected[0].index == 2
    assert selected[0].speaker_change is None
    assert selected[0].forced
    assert [segment.text for segment in result.segments] == ["甲乙", "丙丁"]


def test_global_selection_can_skip_locally_strongest_boundary():
    """Global costs should avoid a tempting cut that creates a poor fragment."""
    words = [
        TranscribedWord(text="甲", start=0.0, end=0.2, confidence=1.0),
        TranscribedWord(text="乙", start=0.6, end=0.8, confidence=1.0),
        TranscribedWord(text="丙", start=0.85, end=1.05, confidence=1.0),
        TranscribedWord(text="丁", start=1.1, end=1.3, confidence=1.0),
        TranscribedWord(text="戊", start=1.35, end=1.55, confidence=1.0),
        TranscribedWord(text="己", start=1.6, end=1.8, confidence=1.0),
        TranscribedWord(text="庚", start=1.85, end=2.05, confidence=1.0),
        TranscribedWord(text="辛", start=2.1, end=2.3, confidence=1.0),
    ]
    settings = UnguidedDelineationSettings(
        target_characters=4,
        max_characters=4,
        preferred_min_duration_seconds=0.0,
        preferred_max_duration_seconds=10.0,
        max_duration_seconds=20.0,
        max_characters_per_second=100.0,
        forced_gap_seconds=100.0,
    )

    result = UnguidedDelineator(settings)([_get_segment(words)])

    strongest = max(result.boundaries, key=lambda boundary: boundary.total_score)
    assert strongest.index == 1
    assert not strongest.selected
    assert [boundary.index for boundary in result.boundaries if boundary.selected] == [
        4
    ]
    assert [segment.text for segment in result.segments] == ["甲乙丙丁", "戊己庚辛"]


def test_indivisible_oversized_segment_is_retained_with_relaxed_constraints():
    """Missing word timings should never cause oversized ASR text to be dropped."""
    text = "這是一個冇辦法按字詞時間拆開嘅超長轉錄片段"
    segment = TranscribedSegment(
        id=4, seek=0, start=1.25, end=9.75, text=text, words=None
    )
    settings = UnguidedDelineationSettings(
        target_characters=3,
        max_characters=5,
        preferred_max_duration_seconds=2.0,
        max_duration_seconds=2.0,
    )

    result = UnguidedDelineator(settings)([segment])

    assert len(result.segments) == 1
    assert result.segments[0].text == text
    assert (result.segments[0].start, result.segments[0].end) == (1.25, 9.75)
    assert result.segments[0].words is None
    assert result.boundaries == []
    assert result.used_relaxed_constraints


def test_empty_input_returns_empty_result():
    """An empty transcription should produce an empty, non-relaxed result."""
    result = UnguidedDelineator()([])

    assert result.segments == []
    assert result.boundaries == []
    assert result.total_cost == approx(0.0)
    assert not result.used_relaxed_constraints


def test_speaker_change_uses_diarization_turn_stability_and_end():
    """Speaker evidence and output timing should retain pyannote turn geometry."""
    words = [
        TranscribedWord(
            text="甲",
            start=0.2,
            end=0.4,
            confidence=1.0,
            speaker="A",
            speaker_turn_start=0.0,
            speaker_turn_end=0.8,
        ),
        TranscribedWord(
            text="乙",
            start=1.0,
            end=1.2,
            confidence=1.0,
            speaker="B",
            speaker_turn_start=0.8,
            speaker_turn_end=2.0,
        ),
    ]
    settings = UnguidedDelineationSettings(
        target_characters=1,
        max_characters=1,
        preferred_min_duration_seconds=0.0,
        preferred_max_duration_seconds=10.0,
        max_duration_seconds=20.0,
        max_characters_per_second=100.0,
        forced_gap_seconds=100.0,
        speaker_stability_seconds=0.5,
    )

    result = UnguidedDelineator(settings)([_get_segment(words)])

    assert result.boundaries[0].speaker_change_score == approx(1.0)
    assert result.boundaries[0].time == approx(0.8)
    assert result.boundaries[0].selected
    assert result.segments[0].end == approx(0.8)
