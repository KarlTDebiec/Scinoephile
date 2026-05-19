#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Line-level character error rate for written Cantonese subtitles."""

from __future__ import annotations

from math import inf

from scinoephile.analysis.character_error_rate import LineCER
from scinoephile.analysis.line_alignment import LineAlignment, LineAlignmentOperation

from .character_equivalence import get_yue_diff_normalized

__all__ = ["YueLineCER"]


class YueLineCER(LineCER):
    """Character error rate for one pair of written Cantonese text strings."""

    def __init__(self, reference: str, candidate: str):
        """Calculate Cantonese-flexible line-level character error rate.

        Arguments:
            reference: reference text
            candidate: candidate text
        """
        self.reference = reference
        self.candidate = candidate

        self.normalized_reference = get_yue_diff_normalized(reference)
        self.normalized_candidate = get_yue_diff_normalized(candidate)
        self.alignment = LineAlignment(
            self.normalized_reference,
            self.normalized_candidate,
        )

        self.substitutions = 0
        self.insertions = 0
        self.deletions = 0
        self.correct = 0
        self._init_edits()
        self.reference_length = len(self.normalized_reference)
        self.correct = self.reference_length - self.substitutions - self.deletions
        self._init_cer()

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
            if pair.operation == LineAlignmentOperation.SUBSTITUTE:
                self.substitutions += 1
            elif pair.operation == LineAlignmentOperation.INSERT:
                self.insertions += 1
            elif pair.operation == LineAlignmentOperation.DELETE:
                self.deletions += 1
