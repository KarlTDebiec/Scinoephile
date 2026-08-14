#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Evaluate aligned multi-source transcriptions against independent references."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from scinoephile.analysis.character_error_rate.line_cer import LineCER
from scinoephile.core.subtitles import Series

from .artifact import AlignmentArtifact
from .timing import TimingMetrics, evaluate_timing, get_reference_for_alignment

__all__ = ["CharacterErrorMetrics", "TranscriptionEvaluation", "evaluate_transcription"]


@dataclass(frozen=True, slots=True)
class CharacterErrorMetrics:
    """Serializable character-error counts for one transcription candidate."""

    cer: float
    """Character error rate."""
    correct: int
    """Correctly matched reference characters."""
    substitutions: int
    """Character substitutions."""
    insertions: int
    """Character insertions."""
    deletions: int
    """Character deletions."""
    reference_length: int
    """Normalized reference character count."""


@dataclass(frozen=True, slots=True)
class TranscriptionEvaluation:
    """Lexical and timing evaluation of one transcription alignment."""

    reference_subtitles: int
    """Reference subtitles overlapping the evaluated alignment."""
    candidate_subtitles: int
    """Merged candidate subtitles in the evaluated alignment."""
    character_errors: dict[str, CharacterErrorMetrics]
    """Character-error metrics keyed by source name and `merged`."""
    timing: TimingMetrics
    """Merged candidate timing metrics."""
    group_counts: dict[str, int]
    """Candidate-to-reference subtitle alignment group counts."""


def evaluate_transcription(
    artifact: AlignmentArtifact, reference: Series
) -> TranscriptionEvaluation:
    """Evaluate aligned ASR sources and merged output against one reference.

    Arguments:
        artifact: aligned multi-source transcription artifact
        reference: independent evaluation reference
    Returns:
        lexical and timing evaluation
    """
    selected_reference = get_reference_for_alignment(artifact, reference)
    reference_text = "".join(
        subtitle.text_with_newline for subtitle in selected_reference
    )
    candidate_texts = {source.name: [] for source in artifact.sources}
    for block in artifact.blocks:
        rows = {row.name: row.text for row in block.rows}
        for source in artifact.sources:
            candidate_texts[source.name].append(
                rows.get(source.name, "").replace("　", "").replace("・", "")
            )
    candidate_texts["merged"] = [
        subtitle.text for block in artifact.blocks for subtitle in block.subtitles
    ]
    character_errors = {
        name: _get_character_error_metrics(LineCER(reference_text, "".join(text_parts)))
        for name, text_parts in candidate_texts.items()
    }
    timing = evaluate_timing(artifact, reference)
    group_counts = Counter(
        f"{len(pair.candidate_indexes)}:{len(pair.reference_indexes)}"
        for pair in timing.pairs
    )
    return TranscriptionEvaluation(
        reference_subtitles=len(selected_reference),
        candidate_subtitles=sum(len(block.subtitles) for block in artifact.blocks),
        character_errors=character_errors,
        timing=timing,
        group_counts=dict(sorted(group_counts.items())),
    )


def _get_character_error_metrics(result: LineCER) -> CharacterErrorMetrics:
    """Copy one character-error result into a serializable value object.

    Arguments:
        result: calculated line-level character error
    Returns:
        serializable character-error metrics
    """
    return CharacterErrorMetrics(
        cer=result.cer,
        correct=result.correct,
        substitutions=result.substitutions,
        insertions=result.insertions,
        deletions=result.deletions,
        reference_length=result.reference_length,
    )
