#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Experimental series diffing with character alignment projected to lines."""

from __future__ import annotations

import difflib
from collections.abc import Iterator
from dataclasses import dataclass

from scinoephile.analysis.line_alignment import LineAlignment, LineAlignmentOperation
from scinoephile.core.subtitles import Series

from .line_diff import LineDiff
from .line_diff_kind import LineDiffKind
from .series_diff import SeriesDiff, _SeriesDiffLineRecord

__all__ = ["AlignmentSeriesDiff"]


@dataclass(frozen=True)
class _AlignmentBlockSide:
    """One side of a subtitle block prepared for character alignment."""

    line_idxs: tuple[int, ...]
    """Global line indices."""

    lines: tuple[str, ...]
    """Original line text."""

    normlines: tuple[str, ...]
    """Normalized line text."""

    text: str
    """Joined normalized text."""

    char_line_idxs: tuple[tuple[int, ...], ...]
    """Local line indices touched by each joined-text character."""


class AlignmentSeriesDiff:
    """Experimentally compute series diffs by aligning joined subtitle blocks."""

    def __init__(
        self,
        one: Series,
        two: Series,
        *,
        one_lbl: str = "one",
        two_lbl: str = "two",
        similarity_cutoff: float = 0.6,
    ):
        """Initialize alignment-derived diff state.

        Arguments:
            one: first subtitle series
            two: second subtitle series
            one_lbl: label for first series in messages
            two_lbl: label for second series in messages
            similarity_cutoff: similarity cutoff for many-to-many shifted text
        """
        self.one_lbl = one_lbl
        self.two_lbl = two_lbl
        self.similarity_cutoff = similarity_cutoff
        self.messages: list[LineDiff] = []
        self._diff(one, two)

    def __iter__(self) -> Iterator[LineDiff]:
        """Iterate over line-level diff messages.

        Returns:
            iterator over diff messages
        """
        return iter(self.messages)

    def __str__(self) -> str:
        """Format the diff for human-readable display.

        Returns:
            formatted multi-line diff representation
        """
        if not self.messages:
            return "[]"

        formatted_messages = "\n".join(
            f"    {str(message)!r}," for message in self.messages
        )
        return f"[\n{formatted_messages}\n]"

    def get_stacked_str(self, *, color: bool = True) -> str:
        """Format the diff as stacked, character-aligned output.

        Arguments:
            color: whether to emit ANSI color escapes
        Returns:
            formatted multi-line diff string
        """
        return "\n".join(message.get_stacked_str(color=color) for message in self)

    def _add_changed_span(
        self,
        one_side: _AlignmentBlockSide,
        two_side: _AlignmentBlockSide,
        one_local_idxs: tuple[int, ...],
        two_local_idxs: tuple[int, ...],
    ):
        """Add messages for one changed aligned span.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            one_local_idxs: local line indices touched on the first side
            two_local_idxs: local line indices touched on the second side
        """
        if not one_local_idxs:
            self._add_insert_messages(two_side, two_local_idxs)
            return
        if not two_local_idxs:
            self._add_delete_messages(one_side, one_local_idxs)
            return

        kind = self._get_changed_span_kind(
            one_side,
            two_side,
            one_local_idxs,
            two_local_idxs,
        )
        self._add_message(
            kind,
            one_side,
            two_side,
            one_local_idxs,
            two_local_idxs,
        )

    def _add_delete_messages(
        self,
        one_side: _AlignmentBlockSide,
        one_local_idxs: tuple[int, ...],
    ):
        """Add delete messages for first-side-only changed lines.

        Arguments:
            one_side: first side of the current block
            one_local_idxs: local line indices touched on the first side
        """
        for one_local_idx in one_local_idxs:
            self.messages.append(
                LineDiff(
                    kind=LineDiffKind.DELETE,
                    one_lbl=self.one_lbl,
                    two_lbl=self.two_lbl,
                    one_idxs=(one_side.line_idxs[one_local_idx],),
                    one_texts=(one_side.lines[one_local_idx],),
                )
            )

    def _add_insert_messages(
        self,
        two_side: _AlignmentBlockSide,
        two_local_idxs: tuple[int, ...],
    ):
        """Add insert messages for second-side-only changed lines.

        Arguments:
            two_side: second side of the current block
            two_local_idxs: local line indices touched on the second side
        """
        for two_local_idx in two_local_idxs:
            self.messages.append(
                LineDiff(
                    kind=LineDiffKind.INSERT,
                    one_lbl=self.one_lbl,
                    two_lbl=self.two_lbl,
                    two_idxs=(two_side.line_idxs[two_local_idx],),
                    two_texts=(two_side.lines[two_local_idx],),
                )
            )

    def _add_message(
        self,
        kind: LineDiffKind,
        one_side: _AlignmentBlockSide,
        two_side: _AlignmentBlockSide,
        one_local_idxs: tuple[int, ...],
        two_local_idxs: tuple[int, ...],
    ):
        """Add a message for a changed span touching both sides.

        Arguments:
            kind: kind of diff message
            one_side: first side of the current block
            two_side: second side of the current block
            one_local_idxs: local line indices touched on the first side
            two_local_idxs: local line indices touched on the second side
        """
        self.messages.append(
            LineDiff(
                kind=kind,
                one_lbl=self.one_lbl,
                two_lbl=self.two_lbl,
                one_idxs=tuple(one_side.line_idxs[idx] for idx in one_local_idxs),
                two_idxs=tuple(two_side.line_idxs[idx] for idx in two_local_idxs),
                one_texts=tuple(one_side.lines[idx] for idx in one_local_idxs),
                two_texts=tuple(two_side.lines[idx] for idx in two_local_idxs),
            )
        )

    def _diff(self, one: Series, two: Series) -> list[LineDiff]:
        """Compare subtitle series by aligning joined pause-delimited blocks.

        Arguments:
            one: first subtitle series
            two: second subtitle series

        Returns:
            list of difference messages
        """
        one_line_records = SeriesDiff._get_series_event_line_records(one)
        two_line_records = SeriesDiff._get_series_event_line_records(two)
        block_pairs = SeriesDiff._get_block_event_index_pairs_by_pause(one, two)
        for one_event_idxs, two_event_idxs in block_pairs:
            one_side = self._get_block_side(one_event_idxs, one_line_records)
            two_side = self._get_block_side(two_event_idxs, two_line_records)
            self._diff_block(one_side, two_side)
        return self.messages

    def _diff_block(
        self,
        one_side: _AlignmentBlockSide,
        two_side: _AlignmentBlockSide,
    ):
        """Compare a subtitle block using character alignment.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
        """
        if not one_side.lines:
            self._add_insert_messages(two_side, tuple(range(len(two_side.lines))))
            return
        if not two_side.lines:
            self._add_delete_messages(one_side, tuple(range(len(one_side.lines))))
            return

        one_pos = 0
        two_pos = 0
        one_changed: set[int] = set()
        two_changed: set[int] = set()
        spans: list[tuple[tuple[int, ...], tuple[int, ...]]] = []

        def flush_changed():
            """Record the current changed span."""
            if not one_changed and not two_changed:
                return
            one_local_idxs = tuple(sorted(one_changed))
            two_local_idxs = tuple(sorted(two_changed))
            spans.append((one_local_idxs, two_local_idxs))
            one_changed.clear()
            two_changed.clear()

        for column in LineAlignment(one_side.text, two_side.text).alignment_pairs:
            if column.operation == LineAlignmentOperation.MATCH:
                flush_changed()
            else:
                if column.one is not None:
                    one_changed.update(one_side.char_line_idxs[one_pos])
                if column.two is not None:
                    two_changed.update(two_side.char_line_idxs[two_pos])

            if column.one is not None:
                one_pos += 1
            if column.two is not None:
                two_pos += 1

        flush_changed()
        spans = self._merge_changed_spans(spans)
        spans = self._merge_adjacent_one_sided_spans(
            spans,
            one_side,
            two_side,
        )
        spans = self._pair_bracketed_one_sided_spans(spans)
        for one_local_idxs, two_local_idxs in spans:
            self._add_changed_span(
                one_side,
                two_side,
                one_local_idxs,
                two_local_idxs,
            )

    def _get_changed_span_kind(
        self,
        one_side: _AlignmentBlockSide,
        two_side: _AlignmentBlockSide,
        one_local_idxs: tuple[int, ...],
        two_local_idxs: tuple[int, ...],
    ) -> LineDiffKind:
        """Classify a changed span touching both sides.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            one_local_idxs: local line indices touched on the first side
            two_local_idxs: local line indices touched on the second side
        Returns:
            kind of diff message
        """
        one_joined = self._join_normlines(one_side, one_local_idxs)
        two_joined = self._join_normlines(two_side, two_local_idxs)

        if len(one_local_idxs) == 1 and len(two_local_idxs) == 1:
            kind = LineDiffKind.EDIT
        elif len(one_local_idxs) == 1:
            if one_joined == two_joined:
                kind = LineDiffKind.SPLIT
            else:
                kind = LineDiffKind.SPLIT_EDIT
        elif len(two_local_idxs) == 1:
            if one_joined == two_joined:
                kind = LineDiffKind.MERGE
            else:
                kind = LineDiffKind.MERGE_EDIT
        else:
            ratio = difflib.SequenceMatcher(
                None,
                one_joined,
                two_joined,
                autojunk=False,
            ).ratio()
            if ratio >= self.similarity_cutoff:
                kind = LineDiffKind.SHIFT
            else:
                kind = LineDiffKind.EDIT

        return kind

    @staticmethod
    def _get_block_side(
        event_idxs: tuple[int, ...],
        line_records: list[tuple[_SeriesDiffLineRecord, ...]],
    ) -> _AlignmentBlockSide:
        """Get alignment-ready data for one side of a subtitle block.

        Arguments:
            event_idxs: event indices in the block
            line_records: text line records grouped by subtitle event
        Returns:
            alignment-ready side data
        """
        records = [
            record for event_idx in event_idxs for record in line_records[event_idx]
        ]
        line_idxs = tuple(record.idx for record in records)
        lines = tuple(record.text for record in records)
        normlines = tuple(record.norm for record in records)

        chunks: list[str] = []
        char_line_idxs: list[tuple[int, ...]] = []
        for local_idx, normline in enumerate(normlines):
            if local_idx > 0:
                chunks.append("\n")
                char_line_idxs.append((local_idx - 1, local_idx))
            chunks.append(normline)
            char_line_idxs.extend((local_idx,) for _ in normline)

        return _AlignmentBlockSide(
            line_idxs=line_idxs,
            lines=lines,
            normlines=normlines,
            text="".join(chunks),
            char_line_idxs=tuple(char_line_idxs),
        )

    @staticmethod
    def _join_normlines(
        side: _AlignmentBlockSide,
        local_idxs: tuple[int, ...],
    ) -> str:
        """Join normalized lines for classification.

        Arguments:
            side: block side containing normalized lines
            local_idxs: local line indices to join
        Returns:
            normalized lines joined with spaces
        """
        return " ".join(side.normlines[idx] for idx in local_idxs)

    def _merge_adjacent_one_sided_spans(
        self,
        spans: list[tuple[tuple[int, ...], tuple[int, ...]]],
        one_side: _AlignmentBlockSide,
        two_side: _AlignmentBlockSide,
    ) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
        """Merge adjacent one-sided spans whose line text is similar.

        Arguments:
            spans: changed spans
            one_side: first side of the current block
            two_side: second side of the current block
        Returns:
            changed spans with similar adjacent one-sided spans paired
        """
        merged: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
        idx = 0
        while idx < len(spans):
            if idx + 1 >= len(spans):
                merged.append(spans[idx])
                idx += 1
                continue

            one_idxs, two_idxs = spans[idx]
            next_one_idxs, next_two_idxs = spans[idx + 1]
            if self._should_merge_adjacent_one_sided_spans(
                one_side,
                two_side,
                one_idxs,
                two_idxs,
                next_one_idxs,
                next_two_idxs,
            ):
                merged.append(
                    (
                        tuple(sorted({*one_idxs, *next_one_idxs})),
                        tuple(sorted({*two_idxs, *next_two_idxs})),
                    )
                )
                idx += 2
                continue

            merged.append(spans[idx])
            idx += 1

        return merged

    @staticmethod
    def _merge_changed_spans(
        spans: list[tuple[tuple[int, ...], tuple[int, ...]]],
    ) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
        """Merge changed character spans that project to the same line change.

        Arguments:
            spans: raw changed spans from character alignment
        Returns:
            merged line-level changed spans
        """
        merged: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
        for next_one, next_two in spans:
            if not merged:
                merged.append((next_one, next_two))
                continue

            prev_one, prev_two = merged[-1]
            if AlignmentSeriesDiff._should_merge_changed_spans(
                prev_one,
                prev_two,
                next_one,
                next_two,
            ):
                one_idxs = tuple(sorted({*prev_one, *next_one}))
                two_idxs = tuple(sorted({*prev_two, *next_two}))
                merged[-1] = (one_idxs, two_idxs)
            else:
                merged.append((next_one, next_two))
        return merged

    @staticmethod
    def _pair_bracketed_one_sided_spans(
        spans: list[tuple[tuple[int, ...], tuple[int, ...]]],
    ) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
        """Pair one-sided spans bracketed by line-aligned spans.

        Arguments:
            spans: changed spans
        Returns:
            changed spans with bracketed one-sided lines paired
        """
        paired: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
        for idx, (one_idxs, two_idxs) in enumerate(spans):
            if one_idxs and two_idxs:
                paired.append((one_idxs, two_idxs))
                continue
            if idx == 0 or idx + 1 >= len(spans):
                paired.append((one_idxs, two_idxs))
                continue

            prev_one_idxs, prev_two_idxs = spans[idx - 1]
            next_one_idxs, next_two_idxs = spans[idx + 1]
            if not (
                prev_one_idxs and prev_two_idxs and next_one_idxs and next_two_idxs
            ):
                paired.append((one_idxs, two_idxs))
                continue

            if not one_idxs and len(two_idxs) == 1:
                missing_one_idxs = tuple(range(prev_one_idxs[-1] + 1, next_one_idxs[0]))
                if len(missing_one_idxs) == 1:
                    paired.append((missing_one_idxs, two_idxs))
                    continue
            if not two_idxs and len(one_idxs) == 1:
                missing_two_idxs = tuple(range(prev_two_idxs[-1] + 1, next_two_idxs[0]))
                if len(missing_two_idxs) == 1:
                    paired.append((one_idxs, missing_two_idxs))
                    continue

            paired.append((one_idxs, two_idxs))
        return paired

    def _should_merge_adjacent_one_sided_spans(
        self,
        one_side: _AlignmentBlockSide,
        two_side: _AlignmentBlockSide,
        one_idxs: tuple[int, ...],
        two_idxs: tuple[int, ...],
        next_one_idxs: tuple[int, ...],
        next_two_idxs: tuple[int, ...],
    ) -> bool:
        """Check whether adjacent one-sided spans should be paired.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            one_idxs: first-side local line indices in the current span
            two_idxs: second-side local line indices in the current span
            next_one_idxs: first-side local line indices in the next span
            next_two_idxs: second-side local line indices in the next span
        Returns:
            whether the spans should be paired
        """
        if one_idxs and two_idxs:
            return False
        if next_one_idxs and next_two_idxs:
            return False
        if bool(one_idxs) == bool(next_one_idxs):
            return False
        if len(one_idxs) + len(next_one_idxs) != 1:
            return False
        if len(two_idxs) + len(next_two_idxs) != 1:
            return False

        merged_one_idxs = tuple(sorted({*one_idxs, *next_one_idxs}))
        merged_two_idxs = tuple(sorted({*two_idxs, *next_two_idxs}))
        one_text = self._join_normlines(one_side, merged_one_idxs)
        two_text = self._join_normlines(two_side, merged_two_idxs)
        ratio = difflib.SequenceMatcher(
            None,
            one_text,
            two_text,
            autojunk=False,
        ).ratio()
        return ratio >= self.similarity_cutoff

    @staticmethod
    def _should_merge_changed_spans(
        prev_one: tuple[int, ...],
        prev_two: tuple[int, ...],
        next_one: tuple[int, ...],
        next_two: tuple[int, ...],
    ) -> bool:
        """Check whether raw changed spans belong to the same line change.

        Arguments:
            prev_one: first-side local line indices in the previous span
            prev_two: second-side local line indices in the previous span
            next_one: first-side local line indices in the next span
            next_two: second-side local line indices in the next span
        Returns:
            whether the spans should be merged before message creation
        """
        prev_one_set = set(prev_one)
        prev_two_set = set(prev_two)
        next_one_set = set(next_one)
        next_two_set = set(next_two)

        if prev_one_set & next_one_set:
            return True
        if prev_two_set & next_two_set:
            return True
        if prev_one_set & next_two_set:
            return True
        if prev_two_set & next_one_set:
            return True
        return False
