#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series-level line diffing for written Cantonese subtitles."""

from __future__ import annotations

from scinoephile.analysis.diff import SeriesDiff
from scinoephile.analysis.diff.series_diff import _SeriesDiffLineRecord
from scinoephile.core.subtitles import Series

from .character_equivalence import get_yue_diff_normalized
from .line_diff import YueLineDiff

__all__ = ["YueSeriesDiff"]


class YueSeriesDiff(SeriesDiff):
    """Compute Cantonese-flexible line-level differences between subtitle series."""

    def __init__(
        self,
        one: Series,
        two: Series,
        *,
        one_lbl: str = "one",
        two_lbl: str = "two",
        similarity_cutoff: float = 0.6,
        max_alignment_cells: int = 4_000_000,
    ):
        """Initialize and convert messages to Yue-aware line diff records.

        Arguments:
            one: first subtitle series
            two: second subtitle series
            one_lbl: label for first series in messages
            two_lbl: label for second series in messages
            similarity_cutoff: similarity cutoff for many-to-many shifted text
            max_alignment_cells: max dynamic programming cells for block alignment
        """
        super().__init__(
            one,
            two,
            one_lbl=one_lbl,
            two_lbl=two_lbl,
            similarity_cutoff=similarity_cutoff,
            max_alignment_cells=max_alignment_cells,
        )
        self.messages = [
            YueLineDiff.from_line_diff(message) for message in self.messages
        ]
        self._stacked_messages = [
            YueLineDiff.from_line_diff(message) for message in self._stacked_messages
        ]

    @staticmethod
    def _get_series_event_line_records(
        series: Series,
    ) -> list[tuple[_SeriesDiffLineRecord, ...]]:
        """Extract Cantonese-normalized line records grouped by subtitle event.

        Arguments:
            series: subtitle series to extract lines from
        Returns:
            text line records grouped by subtitle event
        """
        event_records = []
        line_idx = 0
        for event_idx, subtitle in enumerate(series.events):
            records = []
            for line in subtitle.text_with_newline.splitlines():
                stripped = line.strip()
                if stripped:
                    records.append(
                        _SeriesDiffLineRecord(
                            idx=line_idx,
                            event_idx=event_idx,
                            text=stripped,
                            norm=get_yue_diff_normalized(stripped),
                        )
                    )
                    line_idx += 1
            event_records.append(tuple(records))
        return event_records
