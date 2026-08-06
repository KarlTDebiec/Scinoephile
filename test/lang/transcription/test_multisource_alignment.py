#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Cantonese-aware timed multi-source alignment helpers."""

from __future__ import annotations

import numpy as np

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
from scinoephile.audio.transcription import (
    TranscribedSegment,
    TranscribedWord,
    VoiceActivityTrace,
)
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.multisource_alignment import (
    CantoneseTimedTokenSimilarity,
    get_timed_alignment_sequence,
    get_timed_multisource_alignment_chunks,
    get_timed_reference_alignment_sequence,
    get_timed_reference_boundary_markers,
    get_timed_text_alignment_sequence,
    render_timed_multisource_alignment,
)


def test_cantonese_similarity_orders_substitution_evidence():
    """Test the substitution matrix ranks progressively weaker evidence."""
    similarity = CantoneseTimedTokenSimilarity(timing_weight=0.0)
    token = TimedAlignmentToken("係", 0.0, 0.1)

    exact = similarity(token, TimedAlignmentToken("係", 0.0, 0.1))
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

    assert exact > script > equivalent
    assert equivalent > same_jyutping > same_jyutping_base > unrelated


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


def test_get_timed_reference_boundary_markers_applies_source_offset():
    """Test each reference subtitle end produces a local fullwidth marker."""
    reference = Series(
        events=[
            Subtitle(start=10_000, end=11_000, text="甲"),
            Subtitle(start=11_500, end=12_000, text="乙"),
        ]
    )

    markers = get_timed_reference_boundary_markers(reference, offset_seconds=10.0)

    assert markers == ((1.0, "｜"), (2.0, "｜"))


def test_get_timed_text_alignment_sequence_distributes_lexical_characters():
    """Untimed consensus text should receive uniform approximate timings."""
    sequence = get_timed_text_alignment_sequence(
        "merged", "我，係。", start_seconds=1.0, end_seconds=3.0
    )

    assert sequence.name == "merged"
    assert [
        (token.text, token.start_seconds, token.end_seconds)
        for token in sequence.tokens
    ] == [("我", 1.0, 2.0), ("係", 2.0, 3.0)]


def test_get_timed_multisource_alignment_chunks_preserves_column_rows():
    """Structured chunks should retain equal-width ASR and speaker evidence."""
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

    chunks = get_timed_multisource_alignment_chunks(
        alignment,
        alignment_offset_seconds=10.0,
        diarization=diarization,
        traditionalize=True,
    )

    assert len(chunks) == 1
    assert chunks[0].start_seconds == 10.0
    assert chunks[0].end_seconds == 10.8
    assert [(source.name, source.text) for source in chunks[0].sources] == [
        ("one", "係・"),
        ("two", "是・"),
    ]
    assert chunks[0].speaker == "Ａ・"


def test_alignment_chunks_add_language_singing_and_music_rows():
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

    chunks = get_timed_multisource_alignment_chunks(
        alignment,
        audio_events=events,
        classification_offset_seconds=10.0,
        language_identification=languages,
    )

    assert chunks[0].language_trace == "粵・日"
    assert chunks[0].language_legend == {"粵": "zh-yue", "日": "ja"}
    assert chunks[0].singing_trace == "唱・　"
    assert chunks[0].music_trace == "　・樂"


def test_render_timed_alignment_adds_exclusive_speaker_and_vad_row():
    """Test rendering labels speakers and unattributed pyannote speech."""
    alignment = TimedMultiSequenceAlignment(
        source_names=("whisper", "mimo", "qwen", "merged", "reference"),
        columns=(
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("我", 0.0, 0.1),
                    TimedAlignmentToken("我", 0.0, 0.1),
                    TimedAlignmentToken("我", 0.0, 0.1),
                    TimedAlignmentToken("我", 0.0, 0.1),
                    TimedAlignmentToken("我", 0.0, 0.1),
                )
            ),
            TimedAlignmentColumn(
                (None, None, None, None, None), marker="｜", marker_time_seconds=0.1
            ),
            TimedAlignmentColumn(
                (None, TimedAlignmentToken("为", 0.1, 0.2), None, None, None)
            ),
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("係", 0.2, 0.3),
                    TimedAlignmentToken("是", 0.2, 0.3),
                    TimedAlignmentToken("系", 0.2, 0.3),
                    TimedAlignmentToken("係", 0.2, 0.3),
                    TimedAlignmentToken("係", 0.2, 0.3),
                )
            ),
        ),
    )
    diarization = SpeakerDiarizationResult(
        turns=[SpeakerTurn(start=0.0, end=0.1, speaker="SPEAKER_02")],
        exclusive_turns=[SpeakerTurn(start=0.0, end=0.1, speaker="SPEAKER_02")],
    )
    trace = VoiceActivityTrace(
        np.asarray([1.0, 1.0, 0.0], dtype=np.float32),
        start_ms=10_050.0,
        step_ms=100.0,
        duration_ms=10_300,
    )

    rendered = render_timed_multisource_alignment(
        alignment,
        alignment_offset_seconds=10.0,
        diarization=diarization,
        primary_source_names=("whisper", "mimo", "qwen"),
        voice_activity_trace=trace,
        voice_activity_offset_seconds=10.0,
        columns_per_chunk=4,
        traditionalize=True,
    )

    assert "whisper    我｜　係" in rendered
    assert "mimo       我｜為是" in rendered
    assert "qwen       我｜　係" in rendered
    assert "speaker    Ａ｜＊　" in rendered
    assert "merged     我｜　係" in rendered
    assert "reference  我｜　係" in rendered
    assert "「　」=alignment gap" in rendered
    assert "・=timed pause" in rendered
    assert "｜=reference subtitle boundary" in rendered
    assert "010.000-010.300s" in rendered
    chunk_start = rendered.index("[")
    assert (
        rendered.index("speaker", chunk_start)
        < rendered.index("merged", chunk_start)
        < rendered.index("reference", chunk_start)
    )
