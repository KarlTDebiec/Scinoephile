#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series-level character error rate result record."""

from __future__ import annotations

from scinoephile.analysis.diff import LineDiffKind, SeriesDiff
from scinoephile.core.subtitles import Series
from scinoephile.core.text import remove_punc_and_whitespace

from .line_cer_result import LineCERResult

__all__ = ["SeriesCERResult"]


class SeriesCERResult:
    """Series-level character error rate results."""

    __hash__ = None

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

    def __init__(
        self,
        reference: Series | None = None,
        candidate: Series | None = None,
        *,
        cer: float | None = None,
        substitutions: int | None = None,
        insertions: int | None = None,
        deletions: int | None = None,
        correct: int | None = None,
        reference_length: int | None = None,
    ):
        """Initialize from subtitle series or explicit metric values.

        Arguments:
            reference: reference subtitle series
            candidate: candidate subtitle series
            cer: character error rate
            substitutions: number of substitutions
            insertions: number of insertions
            deletions: number of deletions
            correct: number of correct matches
            reference_length: normalized reference text length
        """
        if reference is not None or candidate is not None:
            if reference is None or candidate is None:
                raise ValueError("reference and candidate must be provided together")
            self._init_from_series(reference, candidate)
        else:
            if (
                cer is None
                or substitutions is None
                or insertions is None
                or deletions is None
                or correct is None
                or reference_length is None
            ):
                raise ValueError("all metric values must be provided")
            self.cer = cer
            self.substitutions = substitutions
            self.insertions = insertions
            self.deletions = deletions
            self.correct = correct
            self.reference_length = reference_length

    def __eq__(self, other: object) -> bool:
        """Compare series CER metrics.

        Arguments:
            other: object to compare against
        Returns:
            whether the two results have equal metrics
        """
        if not isinstance(other, SeriesCERResult):
            return NotImplemented
        return (
            self.cer == other.cer
            and self.substitutions == other.substitutions
            and self.insertions == other.insertions
            and self.deletions == other.deletions
            and self.correct == other.correct
            and self.reference_length == other.reference_length
        )

    def __str__(self) -> str:
        """String representation.

        Returns:
            formatted character error rate summary
        """
        return (
            f"CER: {self.cer}\n"
            f"Correct: {self.correct}\n"
            f"Substitutions: {self.substitutions}\n"
            f"Insertions: {self.insertions}\n"
            f"Deletions: {self.deletions}\n"
            f"Reference length: {self.reference_length}"
        )

    def _init_from_series(self, reference: Series, candidate: Series):
        """Initialize metrics by comparing subtitle series.

        Arguments:
            reference: reference subtitle series
            candidate: candidate subtitle series
        """
        reference_text = remove_punc_and_whitespace(
            "".join(event.text_with_newline for event in reference)
        )
        series_diff = SeriesDiff(reference, candidate)

        self.substitutions = 0
        self.insertions = 0
        self.deletions = 0
        for message in series_diff:
            if message.kind == LineDiffKind.DELETE:
                chunk_result = LineCERResult("".join(message.one_texts or []), "")
            elif message.kind == LineDiffKind.INSERT:
                chunk_result = LineCERResult("", "".join(message.one_texts or []))
            else:
                chunk_result = LineCERResult(
                    "".join(message.one_texts or []),
                    "".join(message.two_texts or []),
                )
            self.substitutions += chunk_result.substitutions
            self.insertions += chunk_result.insertions
            self.deletions += chunk_result.deletions

        self.reference_length = len(reference_text)
        self.correct = self.reference_length - self.substitutions - self.deletions
        if self.reference_length == 0:
            if self.insertions == 0:
                self.cer = 0.0
            else:
                self.cer = float("inf")
        else:
            self.cer = (
                self.substitutions + self.insertions + self.deletions
            ) / self.reference_length
