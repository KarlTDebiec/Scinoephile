#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of multi-source transcription alignment artifact construction."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.alignment.timed_msa import (
    Column,
    MsaAligner,
    MsaAlignment,
    Token,
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
from scinoephile.audio.vad import SpeechBlock
from scinoephile.lang.yue.transcription import YueTokenSimilarity
from scinoephile.workflows.transcription_alignment import (
    build_transcription_alignment_block,
)


def test_build_transcription_alignment_block_uses_current_artifact_models():
    """Test a lexical alignment becomes a validated portable artifact block."""
    alignment = MsaAlignment(
        source_names=("merged", "two"),
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

    diarization = SpeakerDiarizationResult(
        turns=[SpeakerTurn(start=10.1, end=10.2, speaker="speaker")],
        exclusive_turns=[SpeakerTurn(start=10.1, end=10.2, speaker="speaker")],
    )

    block = build_transcription_alignment_block(
        alignment,
        merged_segments,
        MsaAligner(YueTokenSimilarity()),
        speech_block=SpeechBlock(
            index=0,
            start_ms=10_000,
            end_ms=12_000,
            buffered_start_ms=10_000,
            buffered_end_ms=12_000,
        ),
        diarization=diarization,
        pause_intervals_seconds=((0.2, 0.7),),
        timing_sources={7: "ctc-request"},
    )

    assert [(row.name, row.text) for row in block.rows] == [
        ("merged", "係・・好"),
        ("two", "是・・好"),
    ]
    assert any(column.kind == "pause" for column in block.columns)
    assert block.merged == "係・・好"
    assert block.speaker == "Ａ・・　"
    assert block.subtitles[0].timing_source == "ctc-request"
    assert block.subtitles[0].speaker == "Ａ"


def test_build_transcription_alignment_block_adds_classification_rows():
    """FireRed classifications should project onto every alignment column."""
    alignment = MsaAlignment(
        source_names=("one", "two"),
        columns=(
            Column((Token("甲", 0.0, 0.2), Token("甲", 0.0, 0.2))),
            Column((Token("乙", 0.5, 0.7), Token("乙", 0.5, 0.7))),
        ),
    )
    merged_segments = [
        TranscribedSegment(
            id=8,
            seek=0,
            start=10.0,
            end=10.7,
            text="甲乙",
            words=[
                TranscribedWord(text="甲", start=10.0, end=10.2, confidence=0.9),
                TranscribedWord(text="乙", start=10.5, end=10.7, confidence=0.9),
            ],
        )
    ]
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

    block = build_transcription_alignment_block(
        alignment,
        merged_segments,
        MsaAligner(YueTokenSimilarity()),
        speech_block=SpeechBlock(
            index=0,
            start_ms=10_000,
            end_ms=12_000,
            buffered_start_ms=10_000,
            buffered_end_ms=12_000,
        ),
        audio_events=events,
        language_identification=languages,
        pause_intervals_seconds=((0.2, 0.5),),
    )

    assert block.language_trace == "粵・日"
    assert block.language_legend == {"粵": "zh-yue", "日": "ja"}
    assert block.singing_trace == "唱・　"
    assert block.music_trace == "　・樂"


def test_build_transcription_alignment_block_rejects_invalid_segment_timing():
    """Malformed merged segment timing should not be repaired in the artifact."""
    alignment = MsaAlignment(
        source_names=("one", "two"),
        columns=(Column((Token("甲", 0.0, 0.2), Token("甲", 0.0, 0.2))),),
    )
    merged_segments = [
        TranscribedSegment(id=9, seek=0, start=10.2, end=10.0, text="甲")
    ]

    with raises(ValueError, match="end must not precede"):
        build_transcription_alignment_block(
            alignment,
            merged_segments,
            MsaAligner(YueTokenSimilarity()),
            speech_block=SpeechBlock(
                index=0,
                start_ms=10_000,
                end_ms=12_000,
                buffered_start_ms=10_000,
                buffered_end_ms=12_000,
            ),
        )
