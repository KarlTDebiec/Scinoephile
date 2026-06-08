#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series-level line diffing for written Cantonese subtitles."""

from __future__ import annotations

from scinoephile.analysis.diff import LineDiffKind, SeriesDiff
from scinoephile.analysis.diff.series_diff import _SeriesDiffLineRecord
from scinoephile.core.subtitles import Series

from .character_equivalence import get_yue_diff_normalized
from .line_cer import YueLineCER
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
        messages = [YueLineDiff.from_line_diff(message) for message in self.messages]
        self.messages = [
            message for message in messages if not self._is_yue_diff_ignored(message)
        ]
        self._stacked_messages = [
            YueLineDiff.from_line_diff(message) for message in self._stacked_messages
        ]

    def get_stacked_str(
        self,
        *,
        color: bool = True,
        three: Series | None = None,
        include_equal: bool = False,
    ) -> str:
        """Format the diff as stacked Yue-aware character-aligned output.

        Arguments:
            color: whether to emit ANSI color escapes
            three: optional third subtitle series to append below first-side matches
            include_equal: whether to include unchanged aligned subtitles
        Returns:
            formatted multi-line diff string
        """
        if include_equal or three is not None:
            return super().get_stacked_str(
                color=color,
                three=three,
                include_equal=include_equal,
            )

        messages = [
            message
            for message in self._stacked_messages
            if message.kind != LineDiffKind.EQUAL
        ]
        return "\n".join(message.get_stacked_str(color=color) for message in messages)

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
                norm = get_yue_diff_normalized(stripped)
                if norm:
                    records.append(
                        _SeriesDiffLineRecord(
                            idx=line_idx,
                            event_idx=event_idx,
                            text=stripped,
                            norm=norm,
                        )
                    )
                    line_idx += 1
            event_records.append(tuple(records))
        return event_records

    @staticmethod
    def _is_yue_diff_ignored(message: YueLineDiff) -> bool:
        """Check whether a Yue line diff contains only ignored differences.

        Arguments:
            message: Yue line diff to inspect
        Returns:
            whether the diff has no Yue-flexible character edits
        """
        if message.kind in {LineDiffKind.DELETE, LineDiffKind.INSERT}:
            return False
        result = YueLineCER(
            "".join(message.one_texts or ()),
            "".join(message.two_texts or ()),
        )
        return (
            result.substitutions == 0
            and result.insertions == 0
            and result.deletions == 0
        )
