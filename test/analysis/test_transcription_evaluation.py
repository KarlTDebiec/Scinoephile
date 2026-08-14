#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of aligned multi-source transcription evaluation."""

from __future__ import annotations

from scinoephile.analysis.transcription.artifact import (
    AlignmentArtifact,
    AlignmentBlock,
    AlignmentColumn,
    AlignmentRow,
    AlignmentSource,
    AlignmentSubtitle,
)
from scinoephile.analysis.transcription.evaluation import evaluate_transcription
from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle


def test_evaluation_calculates_cer_across_subtitle_boundaries():
    """CER should compare continuous text rather than candidate segmentation."""
    texts = ("甲乙丙丁戊", "己庚辛壬癸", "子丑寅卯辰", "巳午未申酉", "戌亥天地人")
    combined_text = "".join(texts)
    columns = tuple(
        AlignmentColumn(
            index=index + 1, start_ms=index * 200, end_ms=(index + 1) * 200, kind="text"
        )
        for index in range(len(combined_text))
    )
    subtitles = tuple(
        AlignmentSubtitle(
            index=index + 1,
            text=text,
            speech_start_ms=index * 1_000,
            speech_end_ms=(index + 1) * 1_000,
            timing_source="source",
            start_ms=index * 1_000,
            end_ms=(index + 1) * 1_000,
        )
        for index, text in enumerate(texts)
    )
    artifact = AlignmentArtifact(
        language=Language.yue_hant,
        audio_duration_ms=5_000,
        sources=(
            AlignmentSource(name="one", backend="test", model="one"),
            AlignmentSource(name="two", backend="test", model="two"),
        ),
        blocks=(
            AlignmentBlock(
                index=1,
                core_start_ms=0,
                core_end_ms=5_000,
                buffered_start_ms=0,
                buffered_end_ms=5_000,
                columns=columns,
                rows=(
                    AlignmentRow(name="one", text=combined_text),
                    AlignmentRow(name="two", text=combined_text),
                ),
                speaker="＊" * len(combined_text),
                merged=combined_text,
                subtitles=subtitles,
            ),
        ),
    )
    reference = Series(
        events=[
            Subtitle(start=index * 1_000, end=(index + 1) * 1_000, text=text)
            for index, text in enumerate(texts)
        ]
    )

    evaluation = evaluate_transcription(artifact, reference)

    assert set(evaluation.character_errors) == {"one", "two", "merged"}
    for metrics in evaluation.character_errors.values():
        assert metrics.cer == 0.0
        assert metrics.correct == len(combined_text)
        assert metrics.substitutions == 0
        assert metrics.insertions == 0
        assert metrics.deletions == 0
