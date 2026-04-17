#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Character error rate helpers for text and subtitle series."""

from __future__ import annotations

from dataclasses import dataclass
from math import inf

from scinoephile.core.subtitles import Series
from scinoephile.core.text import (
    full_punc_chars,
    half_punc_chars,
    whitespace_chars,
)

from .line_diff import LineDiff
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


def get_series_cer(
    reference: Series,
    hypothesis: Series,
) -> CharacterErrorRateResult:
    """Compute character error rate between subtitle series.

    Arguments:
        reference: reference subtitle series
        hypothesis: hypothesis subtitle series
    Returns:
        character error rate results
    """
    reference_text = _normalize_text_for_cer(_get_series_text(reference))
    series_diff = SeriesDiff(reference, hypothesis)

    substitutions = 0
    insertions = 0
    deletions = 0
    for message in series_diff:
        chunk_result = _get_chunk_cer(message)
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


def get_text_cer(
    reference: str,
    hypothesis: str,
) -> CharacterErrorRateResult:
    """Compute character error rate between text strings.

    Arguments:
        reference: reference text
        hypothesis: hypothesis text
    Returns:
        character error rate results
    """
    normalized_reference = _normalize_text_for_cer(reference)
    normalized_hypothesis = _normalize_text_for_cer(hypothesis)
    substitutions, insertions, deletions, correct = _get_edit_counts(
        normalized_reference,
        normalized_hypothesis,
    )
    reference_length = len(normalized_reference)

    if reference_length == 0:
        cer = 0.0 if len(normalized_hypothesis) == 0 else inf
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


def _get_chunk_cer(message: LineDiff) -> CharacterErrorRateResult:
    """Compute CER for a single diff chunk.

    Arguments:
        message: line diff chunk
    Returns:
        character error rate results for the chunk
    """
    if message.kind == LineDiffKind.DELETE:
        return get_text_cer(
            _join_chunk_text(message.one_texts),
            "",
        )
    if message.kind == LineDiffKind.INSERT:
        return get_text_cer(
            "",
            _join_chunk_text(message.one_texts),
        )
    return get_text_cer(
        _join_chunk_text(message.one_texts),
        _join_chunk_text(message.two_texts),
    )


def _get_edit_counts(reference: str, hypothesis: str) -> tuple[int, int, int, int]:
    """Compute aggregate edit counts for two normalized strings.

    Arguments:
        reference: normalized reference text
        hypothesis: normalized hypothesis text
    Returns:
        substitutions, insertions, deletions, and correct counts
    """
    rows = len(reference) + 1
    cols = len(hypothesis) + 1
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
            if reference[i - 1] == hypothesis[j - 1]:
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
        sort key favoring substitutions, then deletions, then insertions
    """
    distance, substitutions, insertions, deletions, _correct = value
    return distance, insertions, deletions, substitutions


def _join_chunk_text(texts: list[str] | None) -> str:
    """Join one diff-side chunk into a single text string.

    Arguments:
        texts: diff-side texts
    Returns:
        joined text
    """
    if texts is None:
        return ""
    return "".join(texts)


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
    return "".join(char for char in text if char not in chars_to_remove)
