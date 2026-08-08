#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Cantonese-aware timed multi-source alignment helpers."""

from __future__ import annotations

from scinoephile.analysis.multisequence_alignment import (
    TimedAlignmentColumn,
    TimedAlignmentToken,
    TimedMultiSequenceAlignment,
)
from scinoephile.audio.classification import (
    AudioEvent,
    AudioEventDetectionResult,
    AudioEventSpan,
    LanguageIdentificationResult,
    LanguageSpan,
)
from scinoephile.audio.diarization import SpeakerDiarizationResult, SpeakerTurn
from scinoephile.audio.transcription import TranscribedSegment, TranscribedWord
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.multisource_alignment import (
    CantoneseTimedTokenSimilarity,
    get_timed_alignment_sequence,
    get_timed_multisource_alignment_rows,
    get_timed_reference_alignment_sequence,
)


def test_cantonese_similarity_orders_substitution_evidence():
    """Test the substitution matrix ranks progressively weaker evidence."""
    similarity = CantoneseTimedTokenSimilarity(timing_weight=0.0)
    token = TimedAlignmentToken("係", 0.0, 0.1)

    exact = similarity(token, TimedAlignmentToken("係", 0.0, 0.1))
    compatibility_width = similarity(
        TimedAlignmentToken("J", 0.0, 0.1), TimedAlignmentToken("Ｊ", 0.0, 0.1)
    )
    script = similarity(
        TimedAlignmentToken("裡", 0.0, 0.1), TimedAlignmentToken("里", 0.0, 0.1)
    )
    equivalent = similarity(token, TimedAlignmentToken("是", 0.0, 0.1))
    same_jyutping = similarity(
        TimedAlignmentToken("事", 0.0, 0.1), TimedAlignmentToken("是", 0.0, 0.1)
    )
    same_jyutping_base = similarity(
        TimedAlignmentToken("嗰", 0.0, 0.1), TimedAlignmentToken("個", 0.0, 0.1)
    )
    unrelated = similarity(token, TimedAlignmentToken("八", 0.0, 0.1))

    assert compatibility_width == exact
    assert exact > script > equivalent
    assert equivalent > same_jyutping > same_jyutping_base > unrelated


def test_cantonese_similarity_keeps_lexical_evidence_stronger_than_timing():
    """Recognized pronunciation should beat an unrelated same-time character."""
    similarity = CantoneseTimedTokenSimilarity(
        timing_weight=2.0, timing_tolerance_seconds=0.75
    )
    distant_pronunciation = similarity(
        TimedAlignmentToken("嗰", 0.0, 0.1), TimedAlignmentToken("個", 3.0, 3.1)
    )
    unrelated_same_time = similarity(
        TimedAlignmentToken("嗰", 0.0, 0.1), TimedAlignmentToken("八", 0.0, 0.1)
    )

    assert distant_pronunciation > unrelated_same_time


def test_get_timed_alignment_sequence_splits_units_and_omits_punctuation():
    """Test multi-character ASR units receive approximate character timings."""
    segments = [
        TranscribedSegment(
            id=0,
            seek=0,
            start=0.0,
            end=1.0,
            text=" 係呀！",
            words=[TranscribedWord(text=" 係呀！", start=0.2, end=0.6, confidence=0.9)],
        )
    ]

    sequence = get_timed_alignment_sequence("whisper", segments)

    assert [token.text for token in sequence.tokens] == ["係", "呀"]
    assert [(token.start_seconds, token.end_seconds) for token in sequence.tokens] == [
        (0.2, 0.4),
        (0.4, 0.6),
    ]


def test_get_timed_reference_alignment_sequence_applies_source_offset():
    """Test subtitle reference characters receive alignment-local timings."""
    reference = Series(events=[Subtitle(start=10_000, end=12_000, text="这是！")])

    sequence = get_timed_reference_alignment_sequence(
        "reference", reference, offset_seconds=10.0
    )

    assert [token.text for token in sequence.tokens] == ["这", "是"]
    assert [(token.start_seconds, token.end_seconds) for token in sequence.tokens] == [
        (0.0, 1.0),
        (1.0, 2.0),
    ]


def test_get_timed_multisource_alignment_rows_preserves_columns():
    """Structured rows should retain equal-width ASR and speaker evidence."""
    alignment = TimedMultiSequenceAlignment(
        source_names=("one", "two"),
        columns=(
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("係", 0.0, 0.1),
                    TimedAlignmentToken("是", 0.0, 0.1),
                )
            ),
            TimedAlignmentColumn((None, None), pause_interval_seconds=(0.1, 0.8)),
        ),
    )
    diarization = SpeakerDiarizationResult(
        turns=[SpeakerTurn(start=0.0, end=0.1, speaker="speaker")],
        exclusive_turns=[SpeakerTurn(start=0.0, end=0.1, speaker="speaker")],
    )

    rows = get_timed_multisource_alignment_rows(
        alignment, diarization=diarization, traditionalize=True
    )

    assert [(source.name, source.text) for source in rows.sources] == [
        ("one", "係・"),
        ("two", "是・"),
    ]
    assert rows.speaker == "Ａ・"


def test_alignment_rows_add_language_singing_and_music():
    """FireRed classifications should project onto every alignment column."""
    alignment = TimedMultiSequenceAlignment(
        source_names=("one", "two"),
        columns=(
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("甲", 0.0, 0.2),
                    TimedAlignmentToken("甲", 0.0, 0.2),
                )
            ),
            TimedAlignmentColumn((None, None), pause_interval_seconds=(0.2, 0.5)),
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("乙", 0.5, 0.7),
                    TimedAlignmentToken("乙", 0.5, 0.7),
                )
            ),
        ),
    )
    languages = LanguageIdentificationResult(
        spans=[
            LanguageSpan(start=10.0, end=10.3, language="zh-yue", confidence=0.9),
            LanguageSpan(start=10.4, end=10.8, language="ja", confidence=0.8),
        ]
    )
    events = AudioEventDetectionResult(
        spans=[
            AudioEventSpan(start=10.0, end=10.3, event=AudioEvent.SINGING),
            AudioEventSpan(start=10.4, end=10.8, event=AudioEvent.MUSIC),
        ]
    )

    rows = get_timed_multisource_alignment_rows(
        alignment,
        audio_events=events,
        language_identification=languages,
        source_offset_seconds=10.0,
    )

    assert rows.language_trace == "粵・日"
    assert rows.language_legend == {"粵": "zh-yue", "日": "ja"}
    assert rows.singing_trace == "唱・　"
    assert rows.music_trace == "　・樂"
