#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of timed multi-source transcription alignment helpers."""

from __future__ import annotations

from scinoephile.analysis.alignment.timed_msa import Aligner, Alignment, Column, Token
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
    get_timed_alignment_sequence,
    get_timed_multisource_alignment_rows,
    get_timed_reference_alignment_sequence,
    get_transcription_alignment_block,
)
from scinoephile.lang.yue.transcription import YueTimedTokenSimilarity


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
    alignment = Alignment(
        source_names=("one", "two"),
        columns=(
            Column((Token("係", 0.0, 0.1), Token("是", 0.0, 0.1))),
            Column((None, None), pause_interval_seconds=(0.1, 0.8)),
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


def test_get_transcription_alignment_block_uses_current_artifact_models():
    """Test a lexical alignment becomes a validated portable artifact block."""
    alignment = Alignment(
        source_names=("one", "two"),
        columns=(
            Column((Token("係", 0.1, 0.2), Token("是", 0.1, 0.2))),
            Column((Token("好", 0.7, 0.8), Token("好", 0.7, 0.8))),
        ),
    )
    merged_segments = [
        TranscribedSegment(
            id=7,
            seek=0,
            start=10.0,
            end=10.9,
            text="係好",
            words=[
                TranscribedWord(
                    text="係", start=10.1, end=10.2, confidence=0.9, speaker="speaker"
                ),
                TranscribedWord(
                    text="好", start=10.7, end=10.8, confidence=0.9, speaker="speaker"
                ),
            ],
        )
    ]

    block = get_transcription_alignment_block(
        alignment,
        merged_segments,
        Aligner(YueTimedTokenSimilarity()),
        block_index=1,
        buffered_start_ms=10_000,
        buffered_end_ms=12_000,
        core_start_ms=10_000,
        core_end_ms=12_000,
        pause_intervals_seconds=((0.2, 0.7),),
        timing_sources={7: "ctc-request"},
    )

    assert [row.name for row in block.rows] == ["one", "two"]
    assert any(column.kind == "pause" for column in block.columns)
    assert len(block.merged) == len(block.columns)
    assert block.subtitles[0].timing_source == "ctc-request"
    assert block.subtitles[0].speaker == "speaker"


def test_alignment_rows_add_language_singing_and_music():
    """FireRed classifications should project onto every alignment column."""
    alignment = Alignment(
        source_names=("one", "two"),
        columns=(
            Column((Token("甲", 0.0, 0.2), Token("甲", 0.0, 0.2))),
            Column((None, None), pause_interval_seconds=(0.2, 0.5)),
            Column((Token("乙", 0.5, 0.7), Token("乙", 0.5, 0.7))),
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
