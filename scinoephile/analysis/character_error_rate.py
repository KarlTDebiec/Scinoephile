#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Character error rate helpers for text and subtitle series."""

from __future__ import annotations

from dataclasses import dataclass
from math import inf

from scinoephile.core.subtitles import Series
from scinoephile.core.text import full_punc_chars, half_punc_chars, whitespace_chars

from .line_diff_kind import LineDiffKind
from .series_diff import SeriesDiff

__all__ = [
    "CharacterErrorRateResult",
    "get_series_cer",
    "get_text_cer",
]


@dataclass(frozen=True)
class CharacterErrorRateResult:
    """Aggregate character error rate results."""

    cer: float
    """Character error rate."""

    substitutions: int
    """Number of character substitutions."""

    insertions: int
    """Number of character insertions."""

    deletions: int
    """Number of character deletions."""

    correct: int
    """Number of correctly matched reference characters."""

    reference_length: int
    """Number of characters in the normalized reference text."""


def get_series_cer(reference: Series, candidate: Series) -> CharacterErrorRateResult:
    """Compute character error rate between subtitle series.

    Arguments:
        reference: reference subtitle series
        candidate: candidate subtitle series
    Returns:
        character error rate results
    """
    reference_text = _normalize_text_for_cer(_get_series_text(reference))
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
    normalized_reference = _normalize_text_for_cer(reference)
    normalized_candidate = _normalize_text_for_cer(candidate)
    substitutions, insertions, deletions, correct = _get_edit_counts(
        normalized_reference,
        normalized_candidate,
    )
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


def _get_edit_counts(reference: str, candidate: str) -> tuple[int, int, int, int]:
    """Compute aggregate edit counts for two normalized strings.

    Arguments:
        reference: normalized reference text
        candidate: normalized candidate text
    Returns:
        substitutions, insertions, deletions, and correct counts
    """
    rows = len(reference) + 1
    cols = len(candidate) + 1
    dp: list[list[tuple[int, int, int, int, int]]] = [
        [(0, 0, 0, 0, 0) for _ in range(cols)] for _ in range(rows)
    ]

    for i in range(1, rows):
        distance, substitutions, insertions, deletions, correct = dp[i - 1][0]
        dp[i][0] = (distance + 1, substitutions, insertions, deletions + 1, correct)
    for j in range(1, cols):
        distance, substitutions, insertions, deletions, correct = dp[0][j - 1]
        dp[0][j] = (distance + 1, substitutions, insertions + 1, deletions, correct)

    for i in range(1, rows):
        for j in range(1, cols):
            if reference[i - 1] == candidate[j - 1]:
                distance, substitutions, insertions, deletions, correct = dp[i - 1][
                    j - 1
                ]
                dp[i][j] = (
                    distance,
                    substitutions,
                    insertions,
                    deletions,
                    correct + 1,
                )
                continue

            candidates = []

            distance, substitutions, insertions, deletions, correct = dp[i - 1][j - 1]
            candidates.append(
                (distance + 1, substitutions + 1, insertions, deletions, correct)
            )

            distance, substitutions, insertions, deletions, correct = dp[i][j - 1]
            candidates.append(
                (distance + 1, substitutions, insertions + 1, deletions, correct)
            )

            distance, substitutions, insertions, deletions, correct = dp[i - 1][j]
            candidates.append(
                (distance + 1, substitutions, insertions, deletions + 1, correct)
            )

            dp[i][j] = min(candidates, key=_get_edit_sort_key)

    _, substitutions, insertions, deletions, correct = dp[-1][-1]
    return substitutions, insertions, deletions, correct


def _get_edit_sort_key(
    value: tuple[int, int, int, int, int],
) -> tuple[int, int, int, int]:
    """Provide a stable tie-break key for edit operations.

    Arguments:
        value: distance/count tuple from the dynamic program
    Returns:
        sort key favoring fewer insertions, then fewer deletions, then
        fewer substitutions
    """
    distance, substitutions, insertions, deletions, _correct = value
    return distance, insertions, deletions, substitutions


def _get_series_text(series: Series) -> str:
    """Flatten a subtitle series into text for CER evaluation.

    Arguments:
        series: subtitle series
    Returns:
        concatenated subtitle text
    """
    return "".join(event.text_with_newline for event in series)


def _normalize_text_for_cer(text: str) -> str:
    """Normalize text for CER evaluation.

    Arguments:
        text: raw text to normalize
    Returns:
        normalized text
    """
    chars_to_remove = whitespace_chars | half_punc_chars | full_punc_chars
    return "".join(
        char for char in text if not char.isspace() and char not in chars_to_remove
    )
