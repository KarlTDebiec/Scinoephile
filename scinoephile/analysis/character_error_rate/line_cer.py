#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Line-level character error rate."""

from __future__ import annotations

from math import inf

from scinoephile.analysis.line_alignment import LineAlignment, LineAlignmentOperation
from scinoephile.core.text import remove_punc_and_whitespace

__all__ = ["LineCER"]


class LineCER:
    """Character error rate for one pair of text strings."""

    reference: str
    """Original reference text."""

    candidate: str
    """Original candidate text."""

    normalized_reference: str
    """Reference text after removing punctuation and whitespace."""

    normalized_candidate: str
    """Candidate text after removing punctuation and whitespace."""

    alignment: LineAlignment
    """Character alignment between normalized reference and candidate text."""

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

    def __init__(self, reference: str, candidate: str):
        """Calculate line-level character error rate.

        Arguments:
            reference: reference text
            candidate: candidate text
        """
        self.reference = reference
        self.candidate = candidate

        self.normalized_reference = remove_punc_and_whitespace(reference)
        self.normalized_candidate = remove_punc_and_whitespace(candidate)
        self.alignment = LineAlignment(
            self.normalized_reference, self.normalized_candidate
        )

        self.substitutions = 0
        self.insertions = 0
        self.deletions = 0
        self.correct = 0
        self._init_edits()
        self.reference_length = len(self.normalized_reference)
        self._init_cer()

    def __repr__(self) -> str:
        """Return a reconstructable representation of this result.

        Returns:
            reconstructable representation
        """
        return f"{type(self).__name__}({self.reference!r}, {self.candidate!r})"

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

    def _init_cer(self):
        """Calculate character error rate."""
        if self.reference_length == 0:
            if self.insertions == 0:
                self.cer = 0.0
            else:
                self.cer = inf
        else:
            self.cer = (
                self.substitutions + self.insertions + self.deletions
            ) / self.reference_length

    def _init_edits(self):
        """Count edit operations in this alignment."""
        for pair in self.alignment.alignment_pairs:
            if pair.operation == LineAlignmentOperation.MATCH:
                self.correct += 1
            elif pair.operation == LineAlignmentOperation.SUBSTITUTE:
                self.substitutions += 1
            elif pair.operation == LineAlignmentOperation.INSERT:
                self.insertions += 1
            else:
                self.deletions += 1
