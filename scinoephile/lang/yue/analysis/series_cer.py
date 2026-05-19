#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series-level character error rate for written Cantonese subtitles."""

from __future__ import annotations

from scinoephile.analysis.character_error_rate import SeriesCER
from scinoephile.analysis.diff import LineDiffKind
from scinoephile.core.subtitles import Series

from .character_equivalence import get_yue_diff_normalized
from .line_cer import YueLineCER
from .series_diff import YueSeriesDiff

__all__ = ["YueSeriesCER"]


class YueSeriesCER(SeriesCER):
    """Cantonese-flexible series-level character error rate."""

    @staticmethod
    def _get_normalized_reference_text(series: Series) -> str:
        """Get Yue-normalized series text for CER reference length.

        Arguments:
            series: subtitle series to normalize
        Returns:
            Yue-normalized reference text
        """
        normalized_lines = []
        for event in series:
            for line in event.text_with_newline.splitlines():
                norm = get_yue_diff_normalized(line.strip())
                if norm:
                    normalized_lines.append(norm)
        return "".join(normalized_lines)

    def _init_metrics(self, reference: Series, candidate: Series):
        """Initialize metrics by comparing subtitle series.

        Arguments:
            reference: reference subtitle series
            candidate: candidate subtitle series
        """
        reference_text = self._get_normalized_reference_text(reference)
        series_diff = YueSeriesDiff(reference, candidate)

        self.substitutions = 0
        self.insertions = 0
        self.deletions = 0
        for message in series_diff:
            if message.kind == LineDiffKind.DELETE:
                chunk_result = YueLineCER("".join(message.one_texts or []), "")
            elif message.kind == LineDiffKind.INSERT:
                chunk_result = YueLineCER("", "".join(message.two_texts or []))
            else:
                chunk_result = YueLineCER(
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
