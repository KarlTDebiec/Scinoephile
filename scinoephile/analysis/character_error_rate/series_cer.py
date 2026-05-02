#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series-level character error rate."""

from __future__ import annotations

from scinoephile.analysis.diff import LineDiffKind, SeriesDiff
from scinoephile.core.subtitles import Series
from scinoephile.core.text import remove_punc_and_whitespace

from .line_cer import LineCER

__all__ = ["SeriesCER"]


class SeriesCER:
    """Series-level character error rate."""

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

    def __init__(self, reference: Series, candidate: Series):
        """Initialize by comparing subtitle series.

        Arguments:
            reference: reference subtitle series
            candidate: candidate subtitle series
        """
        self._init(reference, candidate)

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

    def _init(self, reference: Series, candidate: Series):
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
                chunk_result = LineCER("".join(message.one_texts or []), "")
            elif message.kind == LineDiffKind.INSERT:
                chunk_result = LineCER("", "".join(message.one_texts or []))
            else:
                chunk_result = LineCER(
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
