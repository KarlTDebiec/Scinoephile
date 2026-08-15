#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Evaluate aligned multi-source transcriptions against independent references."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.analysis.character_error_rate.line_cer import LineCER
from scinoephile.core.subtitles import Series

from .artifact import AlignmentArtifact
from .timing import TimingMetrics, evaluate_timing, get_reference_for_alignment

__all__ = [
    "CharacterErrorMetrics",
    "TranscriptionEvaluation",
    "evaluate_character_errors",
    "evaluate_transcription",
]


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


def evaluate_character_errors(
    artifact: AlignmentArtifact, reference: Series
) -> dict[str, CharacterErrorMetrics]:
    """Evaluate aligned ASR sources and merged output against one reference.

    Arguments:
        artifact: aligned multi-source transcription artifact
        reference: independent evaluation reference
    Returns:
        character-error metrics keyed by source name and `merged`
    """
    selected_reference = get_reference_for_alignment(artifact, reference)
    reference_text = "".join(
        subtitle.text_with_newline for subtitle in selected_reference
    )
    source_texts = {source.name: [] for source in artifact.sources}
    for block in artifact.blocks:
        rows = {row.name: row.text for row in block.rows}
        for source in artifact.sources:
            text = rows.get(source.name, "").replace("　", "").replace("・", "")
            if text:
                source_texts[source.name].append(text)
    candidates = {name: "".join(texts) for name, texts in source_texts.items()}
    candidates["merged"] = "".join(
        subtitle.text_with_newline for subtitle in artifact.get_series()
    )
    return {
        name: _get_character_error_metrics(LineCER(reference_text, candidate))
        for name, candidate in candidates.items()
    }


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
    character_errors = evaluate_character_errors(artifact, reference)
    timing = evaluate_timing(artifact, reference)
    return TranscriptionEvaluation(
        reference_subtitles=len(selected_reference),
        candidate_subtitles=sum(len(block.subtitles) for block in artifact.blocks),
        character_errors=character_errors,
        timing=timing,
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
