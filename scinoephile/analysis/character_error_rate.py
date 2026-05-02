#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Character error rate helpers for text and subtitle series."""

from __future__ import annotations

from math import inf

from scinoephile.core.subtitles import Series
from scinoephile.core.text import remove_punc_and_whitespace

from .character_error_rate_result import CharacterErrorRateResult
from .line_alignment import count_edits, get_aligned_chars
from .line_diff_kind import LineDiffKind
from .series_diff import SeriesDiff

__all__ = [
    "get_series_cer",
    "get_text_cer",
]


def get_series_cer(reference: Series, candidate: Series) -> CharacterErrorRateResult:
    """Compute character error rate between subtitle series.

    Arguments:
        reference: reference subtitle series
        candidate: candidate subtitle series
    Returns:
        character error rate results
    """
    reference_text = remove_punc_and_whitespace(
        "".join(event.text_with_newline for event in reference)
    )
    series_diff = SeriesDiff(reference, candidate)

    substitutions = 0
    insertions = 0
    deletions = 0
    for message in series_diff:
        if message.kind == LineDiffKind.DELETE:
            chunk_result = get_text_cer("".join(message.one_texts or []), "")
        elif message.kind == LineDiffKind.INSERT:
            chunk_result = get_text_cer("", "".join(message.one_texts or []))
        else:
            chunk_result = get_text_cer(
                "".join(message.one_texts or []),
                "".join(message.two_texts or []),
            )
        substitutions += chunk_result.substitutions
        insertions += chunk_result.insertions
        deletions += chunk_result.deletions

    reference_length = len(reference_text)
    correct = reference_length - substitutions - deletions
    if reference_length == 0:
        cer = 0.0 if insertions == 0 else inf
    else:
        cer = (substitutions + insertions + deletions) / reference_length

    return CharacterErrorRateResult(
        cer=cer,
        substitutions=substitutions,
        insertions=insertions,
        deletions=deletions,
        correct=correct,
        reference_length=reference_length,
    )


def get_text_cer(reference: str, candidate: str) -> CharacterErrorRateResult:
    """Compute character error rate between text strings.

    Arguments:
        reference: reference text
        candidate: candidate text
    Returns:
        character error rate results
    """
    normalized_reference = remove_punc_and_whitespace(reference)
    normalized_candidate = remove_punc_and_whitespace(candidate)
    alignment = get_aligned_chars(normalized_reference, normalized_candidate)
    substitutions, insertions, deletions, correct = count_edits(alignment)
    reference_length = len(normalized_reference)

    if reference_length == 0:
        cer = 0.0 if len(normalized_candidate) == 0 else inf
    else:
        cer = (substitutions + insertions + deletions) / reference_length

    return CharacterErrorRateResult(
        cer=cer,
        substitutions=substitutions,
        insertions=insertions,
        deletions=deletions,
        correct=correct,
        reference_length=reference_length,
    )
