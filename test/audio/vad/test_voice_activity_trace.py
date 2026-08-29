#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of frame-aligned VAD score traces."""

from __future__ import annotations

import numpy as np
import pytest

from scinoephile.audio.transcription import (
    TranscribedSegment,
    TranscribedWord,
    get_segment_split_at_idx,
)
from scinoephile.audio.transcription.whisper import (
    WHISPER_LARGE_V3_CANTONESE_MODEL,
    WhisperModel,
    WhisperTranscriber,
)
from scinoephile.audio.vad import VoiceActivityTrace
from scinoephile.core import Language


def test_trace_summarizes_partial_frame_overlap():
    """Weight score summaries by each frame's overlap with the query interval."""
    trace = VoiceActivityTrace(
        np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        start_ms=50,
        step_ms=100,
        duration_ms=300,
    )

    assert trace.get_mean_score(0.05, 0.25) == pytest.approx(0.5)
    assert trace.get_peak_score(0.05, 0.25) == pytest.approx(1.0)
    assert trace.get_coverage(0.05, 0.25, 0.75) == pytest.approx(0.25)
    assert trace.get_mean_score(0.4, 0.5) is None


def test_trace_extends_edge_scores_to_audio_boundaries():
    """Represent the full audio timeline when model frame centers are inset."""
    trace = VoiceActivityTrace(
        np.asarray([0.2, 0.8], dtype=np.float32),
        start_ms=30,
        step_ms=20,
        duration_ms=100,
    )

    assert trace.get_mean_score(0, 0.02) == pytest.approx(0.2)
    assert trace.get_mean_score(0.06, 0.1) == pytest.approx(0.8)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"scores": np.asarray([[0.5]])}, "one-dimensional"),
        ({"scores": np.asarray([np.nan])}, "finite"),
        ({"scores": np.asarray([1.1])}, "between zero and one"),
        ({"start_ms": -1}, "start must be non-negative"),
        ({"step_ms": 0}, "step must be positive"),
        ({"duration_ms": -1}, "duration must be non-negative"),
    ],
)
def test_trace_rejects_invalid_values(kwargs: dict[str, object], message: str):
    """Reject malformed scores and geometry.

    Arguments:
        kwargs: invalid constructor override
        message: expected validation error text
    """
    values = {
        "scores": np.asarray([0.5]),
        "start_ms": 50,
        "step_ms": 100,
        "duration_ms": 100,
        **kwargs,
    }

    with pytest.raises(ValueError, match=message):
        VoiceActivityTrace(**values)  # type: ignore[arg-type]


def test_transcriber_attaches_word_and_gap_score_summaries():
    """Combine a VAD trace with timestamped transcription words."""
    transcriber = WhisperTranscriber(
        WhisperModel(WHISPER_LARGE_V3_CANTONESE_MODEL, Language.yue_hant, device="cpu"),
        Language.yue_hant,
    )
    trace = VoiceActivityTrace(
        np.asarray([0.8, 0.8, 0.1, 0.2, 0.9], dtype=np.float32),
        start_ms=50,
        step_ms=100,
        duration_ms=500,
    )
    segment = TranscribedSegment(
        id=0,
        seek=0,
        start=0,
        end=0.5,
        text="甲乙",
        words=[
            TranscribedWord(text="甲", start=0, end=0.2, confidence=1),
            TranscribedWord(text="乙", start=0.4, end=0.5, confidence=1),
        ],
    )

    output = transcriber._add_voice_activity_scores([segment], trace)

    assert output[0].words is not None
    first, second = output[0].words
    assert first.voice_activity_score == pytest.approx(0.8)
    assert first.voice_activity_peak == pytest.approx(0.8)
    assert first.voice_activity_coverage == pytest.approx(1.0)
    assert first.following_voice_activity_score == pytest.approx(0.15)
    assert second.voice_activity_score == pytest.approx(0.9)
    assert second.following_voice_activity_score is None
    assert segment.words is not None
    assert segment.words[0].voice_activity_score is None


def test_split_word_clears_timing_dependent_voice_activity_summaries():
    """Clear score summaries invalidated when a word's time range changes."""
    segment = TranscribedSegment(
        id=0,
        seek=0,
        start=0,
        end=1,
        text="firstsecond",
        words=[
            TranscribedWord(
                text="firstsecond",
                start=0,
                end=1,
                confidence=1,
                following_voice_activity_score=0.1,
                voice_activity_coverage=0.6,
                voice_activity_peak=0.9,
                voice_activity_score=0.7,
            )
        ],
    )

    first_segment, second_segment = get_segment_split_at_idx(segment, 5)

    assert first_segment.words is not None
    assert second_segment.words is not None
    first_word = first_segment.words[0]
    second_word = second_segment.words[0]
    assert first_word.following_voice_activity_score is None
    assert second_word.following_voice_activity_score == pytest.approx(0.1)
    for word in (first_word, second_word):
        assert word.voice_activity_coverage is None
        assert word.voice_activity_peak is None
        assert word.voice_activity_score is None
