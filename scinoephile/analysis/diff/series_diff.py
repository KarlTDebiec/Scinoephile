#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series-level line diffing."""

from __future__ import annotations

import difflib
import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import TypedDict

from scinoephile.analysis.alignment import pairwise
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import are_series_one_to_one
from scinoephile.core.text import remove_punc_and_whitespace

from .line_diff import LineDiff
from .line_diff_kind import LineDiffKind

__all__ = ["SeriesDiff", "SeriesDiffKwargs"]

type _LineIndexes = tuple[int, ...]
"""Ordered local line indexes from one side of a subtitle block."""

type _LineSpan = tuple[_LineIndexes, _LineIndexes]
"""Paired local line indexes from the two sides of a subtitle block."""


class SeriesDiffKwargs(TypedDict, total=False):
    """Keyword arguments for SeriesDiff."""

    one_lbl: str
    """Label for the first subtitle series in diff messages."""

    two_lbl: str
    """Label for the second subtitle series in diff messages."""

    similarity_cutoff: float
    """Similarity threshold used when pairing replacement blocks."""

    max_alignment_cells: int
    """Maximum dynamic programming cells to allocate for a block alignment."""


@dataclass(frozen=True)
class _SeriesDiffLineRecord:
    """One flattened subtitle text line with its global line index."""

    idx: int
    """Zero-based global line index."""

    event_idx: int
    """Zero-based subtitle event index."""

    text: str
    """Raw text line."""

    norm: str
    """Normalized text line used for matching."""

    start: int
    """Subtitle event start time in milliseconds."""

    end: int
    """Subtitle event end time in milliseconds."""


@dataclass(frozen=True)
class _SeriesDiffBlockSide:
    """One side of a subtitle block prepared for character alignment."""

    line_idxs: tuple[int, ...]
    """Global line indices."""

    lines: tuple[str, ...]
    """Original line text."""

    normlines: tuple[str, ...]
    """Normalized line text."""

    times: tuple[tuple[int, int], ...]
    """Subtitle event start and end times by local line index."""

    text: str
    """Joined normalized text."""

    char_line_idxs: tuple[tuple[int, ...], ...]
    """Local line indices touched by each joined-text character."""


class SeriesDiff:
    """Compute line-level differences between subtitle series."""

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
        """Initialize series diff state.

        Arguments:
            one: first subtitle series
            two: second subtitle series
            one_lbl: label for first series in messages
            two_lbl: label for second series in messages
            similarity_cutoff: similarity cutoff for line and span pairing
            max_alignment_cells: max dynamic programming cells for block alignment
        """
        self.one_lbl = one_lbl
        self.two_lbl = two_lbl
        self.similarity_cutoff = similarity_cutoff
        self.max_alignment_cells = max_alignment_cells
        self.messages: list[LineDiff] = []
        self._stacked_messages: list[LineDiff] = []
        self._one = one
        self._one_line_event_idxs: tuple[int, ...] = ()
        self._two_line_event_idxs: tuple[int, ...] = ()
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

    def get_event_indices(
        self, message: LineDiff
    ) -> tuple[tuple[int, ...], tuple[int, ...]]:
        """Get subtitle event indices represented by a line diff message.

        Arguments:
            message: line diff message
        Returns:
            first- and second-side zero-based subtitle event indices
        """
        one_event_idxs = self._get_message_event_indices(
            message.one_idxs, self._one_line_event_idxs
        )
        two_event_idxs = self._get_message_event_indices(
            message.two_idxs, self._two_line_event_idxs
        )
        return one_event_idxs, two_event_idxs

    def get_messages(self, *, include_equal: bool = False) -> tuple[LineDiff, ...]:
        """Get aligned line diff messages.

        Arguments:
            include_equal: whether to include unchanged aligned subtitles
        Returns:
            line diff messages in display order
        """
        if include_equal:
            return tuple(self._stacked_messages)
        return tuple(self.messages)

    def get_stacked_str(
        self,
        *,
        color: bool = True,
        three: Series | None = None,
        include_equal: bool = False,
    ) -> str:
        """Format the diff as stacked, character-aligned output.

        Arguments:
            color: whether to emit ANSI color escapes
            three: optional third subtitle series to append below first-side matches
            include_equal: whether to include unchanged aligned subtitles
        Returns:
            formatted multi-line diff string
        Raises:
            ScinoephileError: if one and three are not one-to-one matched
        """
        messages = self.get_messages(include_equal=include_equal)
        if three is None:
            return "\n".join(
                message.get_stacked_str(color=color) for message in messages
            )

        if not are_series_one_to_one(self._one, three):
            raise ScinoephileError(
                "Third subtitle series must be one-to-one matched with the first "
                "subtitle series"
            )

        return "\n".join(
            message.get_stacked_str(
                color=color, three_texts=self._get_third_texts(message, three)
            )
            for message in messages
        )

    def _add_changed_span(
        self,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
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

        if len(one_local_idxs) == len(two_local_idxs):
            line_pairs = tuple(zip(one_local_idxs, two_local_idxs, strict=True))
            if all(
                one_side.lines[one_idx] == two_side.lines[two_idx]
                for one_idx, two_idx in line_pairs
            ):
                for one_idx, two_idx in line_pairs:
                    self._add_equal_message(
                        one_side=one_side,
                        two_side=two_side,
                        one_local_idxs=(one_idx,),
                        two_local_idxs=(two_idx,),
                    )
                return

        kind = self._get_changed_span_kind(
            one_side, two_side, one_local_idxs, two_local_idxs
        )
        self._add_message(kind, one_side, two_side, one_local_idxs, two_local_idxs)

    def _add_equal_message(
        self,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        one_local_idxs: tuple[int, ...],
        two_local_idxs: tuple[int, ...],
    ):
        """Add an equal message for stacked display.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            one_local_idxs: local line indices on the first side
            two_local_idxs: local line indices on the second side
        """
        self._stacked_messages.append(
            LineDiff(
                kind=LineDiffKind.EQUAL,
                one_lbl=self.one_lbl,
                two_lbl=self.two_lbl,
                one_idxs=tuple(one_side.line_idxs[idx] for idx in one_local_idxs),
                two_idxs=tuple(two_side.line_idxs[idx] for idx in two_local_idxs),
                one_texts=tuple(one_side.lines[idx] for idx in one_local_idxs),
                two_texts=tuple(two_side.lines[idx] for idx in two_local_idxs),
            )
        )

    def _add_equal_messages_until(
        self,
        *,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        one_line_pos: int,
        two_line_pos: int,
        one_line_stop: int,
        two_line_stop: int,
    ) -> tuple[int, int]:
        """Add equal stacked-display messages before a changed span.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            one_line_pos: current first-side local line index
            two_line_pos: current second-side local line index
            one_line_stop: first-side local line index at which to stop
            two_line_stop: second-side local line index at which to stop
        Returns:
            updated first- and second-side local line positions
        """
        one_line_stop = max(one_line_pos, min(one_line_stop, len(one_side.lines)))
        two_line_stop = max(two_line_pos, min(two_line_stop, len(two_side.lines)))
        one_local_idxs = tuple(range(one_line_pos, one_line_stop))
        two_local_idxs = tuple(range(two_line_pos, two_line_stop))
        matcher = difflib.SequenceMatcher(
            None,
            tuple(one_side.normlines[idx] for idx in one_local_idxs),
            tuple(two_side.normlines[idx] for idx in two_local_idxs),
            autojunk=False,
        )
        for tag, one_start, one_end, two_start, two_end in matcher.get_opcodes():
            matched_one_local_idxs = one_local_idxs[one_start:one_end]
            matched_two_local_idxs = two_local_idxs[two_start:two_end]
            if tag == "equal":
                for one_local_idx, two_local_idx in zip(
                    matched_one_local_idxs, matched_two_local_idxs, strict=True
                ):
                    self._add_equal_message(
                        one_side=one_side,
                        two_side=two_side,
                        one_local_idxs=(one_local_idx,),
                        two_local_idxs=(two_local_idx,),
                    )
                continue
            self._add_changed_span(
                one_side, two_side, matched_one_local_idxs, matched_two_local_idxs
            )
        return one_line_stop, two_line_stop

    def _add_delete_messages(
        self, one_side: _SeriesDiffBlockSide, one_local_idxs: tuple[int, ...]
    ):
        """Add delete messages for first-side-only changed lines.

        Arguments:
            one_side: first side of the current block
            one_local_idxs: local line indices touched on the first side
        """
        for one_local_idx in one_local_idxs:
            message = LineDiff(
                kind=LineDiffKind.DELETE,
                one_lbl=self.one_lbl,
                two_lbl=self.two_lbl,
                one_idxs=(one_side.line_idxs[one_local_idx],),
                one_texts=(one_side.lines[one_local_idx],),
            )
            self.messages.append(message)
            self._stacked_messages.append(message)

    def _add_insert_messages(
        self, two_side: _SeriesDiffBlockSide, two_local_idxs: tuple[int, ...]
    ):
        """Add insert messages for second-side-only changed lines.

        Arguments:
            two_side: second side of the current block
            two_local_idxs: local line indices touched on the second side
        """
        for two_local_idx in two_local_idxs:
            message = LineDiff(
                kind=LineDiffKind.INSERT,
                one_lbl=self.one_lbl,
                two_lbl=self.two_lbl,
                two_idxs=(two_side.line_idxs[two_local_idx],),
                two_texts=(two_side.lines[two_local_idx],),
            )
            self.messages.append(message)
            self._stacked_messages.append(message)

    def _add_message(
        self,
        kind: LineDiffKind,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
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
        message = LineDiff(
            kind=kind,
            one_lbl=self.one_lbl,
            two_lbl=self.two_lbl,
            one_idxs=tuple(one_side.line_idxs[idx] for idx in one_local_idxs),
            two_idxs=tuple(two_side.line_idxs[idx] for idx in two_local_idxs),
            one_texts=tuple(one_side.lines[idx] for idx in one_local_idxs),
            two_texts=tuple(two_side.lines[idx] for idx in two_local_idxs),
        )
        self.messages.append(message)
        self._stacked_messages.append(message)

    def _diff(self, one: Series, two: Series) -> list[LineDiff]:
        """Compare subtitle series by aligning joined pause-delimited blocks.

        Arguments:
            one: first subtitle series
            two: second subtitle series
        Returns:
            list of difference messages
        """
        one_line_records = self._get_series_event_line_records(one)
        two_line_records = self._get_series_event_line_records(two)
        self._one_line_event_idxs = tuple(
            record.event_idx
            for event_line_records in one_line_records
            for record in event_line_records
        )
        self._two_line_event_idxs = tuple(
            record.event_idx
            for event_line_records in two_line_records
            for record in event_line_records
        )
        block_pairs = self._get_block_event_index_pairs_by_pause(one, two)
        for one_event_idxs, two_event_idxs in block_pairs:
            one_side = self._get_block_side(one_event_idxs, one_line_records)
            two_side = self._get_block_side(two_event_idxs, two_line_records)
            self._diff_block(one_side, two_side)
        self._validate_message_coverage()
        return self.messages

    def _diff_block(
        self, one_side: _SeriesDiffBlockSide, two_side: _SeriesDiffBlockSide
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
        if len(one_side.text) * len(two_side.text) > self.max_alignment_cells:
            self._diff_block_by_lines(one_side, two_side)
            return

        one_pos = 0
        two_pos = 0
        one_changed: set[int] = set()
        two_changed: set[int] = set()
        changed_columns: list[tuple[pairwise.Operation, int, int]] = []
        spans: list[_LineSpan] = []

        def flush_changed():
            """Record the current changed span."""
            if not one_changed and not two_changed:
                return
            separator_span = self._get_separator_only_changed_span(
                one_side, two_side, changed_columns
            )
            if separator_span is None:
                one_local_idxs = tuple(sorted(one_changed))
                two_local_idxs = tuple(sorted(two_changed))
                spans.append((one_local_idxs, two_local_idxs))
            else:
                spans.append(separator_span)
            one_changed.clear()
            two_changed.clear()
            changed_columns.clear()

        for column in pairwise.Alignment(one_side.text, two_side.text).columns:
            if column.operation == pairwise.Operation.MATCH:
                flush_changed()
            else:
                changed_columns.append((column.operation, one_pos, two_pos))
                if column.one is not None:
                    one_changed.update(
                        self._get_changed_line_idxs(one_side, one_pos, column.operation)
                    )
                if column.two is not None:
                    two_changed.update(
                        self._get_changed_line_idxs(two_side, two_pos, column.operation)
                    )
                if column.operation == pairwise.Operation.DELETE:
                    two_changed.update(
                        self._get_context_line_idxs(
                            source_side=one_side,
                            target_side=two_side,
                            source_pos=one_pos,
                            target_pos=two_pos,
                        )
                    )
                if column.operation == pairwise.Operation.INSERT:
                    one_changed.update(
                        self._get_context_line_idxs(
                            source_side=two_side,
                            target_side=one_side,
                            source_pos=two_pos,
                            target_pos=one_pos,
                        )
                    )

            if column.one is not None:
                one_pos += 1
            if column.two is not None:
                two_pos += 1

        flush_changed()
        spans = self._merge_changed_spans(spans)
        spans = self._fill_changed_span_gaps(
            self._merge_adjacent_one_sided_spans(spans, one_side, two_side)
        )
        spans = self._claim_temporally_supported_boundary_gaps(
            spans, one_side, two_side
        )
        spans = self._split_uncovered_multiline_spans(spans, one_side, two_side)
        spans = self._unclaim_shifted_boundary_lines(spans, one_side, two_side)
        spans = self._pair_one_sided_spans_with_implicit_lines(
            spans, one_side, two_side
        )
        self._add_block_messages(one_side, two_side, spans)

    def _add_block_messages(
        self,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        spans: list[_LineSpan],
    ):
        """Add equal and changed messages for a diffed block.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            spans: changed spans in block order
        """
        one_line_pos = 0
        two_line_pos = 0
        for raw_one_local_idxs, raw_two_local_idxs in spans:
            # Drop spans already represented by preceding implicit matches
            one_local_idxs = tuple(
                idx for idx in raw_one_local_idxs if idx >= one_line_pos
            )
            two_local_idxs = tuple(
                idx for idx in raw_two_local_idxs if idx >= two_line_pos
            )
            if not one_local_idxs and not two_local_idxs:
                continue
            one_line_stop = one_line_pos
            if one_local_idxs:
                one_line_stop = one_local_idxs[0]
            two_line_stop = two_line_pos
            if two_local_idxs:
                two_line_stop = two_local_idxs[0]
            if one_local_idxs:
                if not two_local_idxs:
                    two_line_stop = two_line_pos + (one_line_stop - one_line_pos)
            elif two_local_idxs:
                one_line_stop = one_line_pos + (two_line_stop - two_line_pos)
            one_line_pos, two_line_pos = self._add_equal_messages_until(
                one_side=one_side,
                two_side=two_side,
                one_line_pos=one_line_pos,
                two_line_pos=two_line_pos,
                one_line_stop=one_line_stop,
                two_line_stop=two_line_stop,
            )
            self._add_changed_span(one_side, two_side, one_local_idxs, two_local_idxs)
            if one_local_idxs:
                one_line_pos = one_local_idxs[-1] + 1
            if two_local_idxs:
                two_line_pos = two_local_idxs[-1] + 1
        one_line_pos, two_line_pos = self._add_equal_messages_until(
            one_side=one_side,
            two_side=two_side,
            one_line_pos=one_line_pos,
            two_line_pos=two_line_pos,
            one_line_stop=len(one_side.lines),
            two_line_stop=len(two_side.lines),
        )
        self._add_delete_messages(
            one_side, tuple(range(one_line_pos, len(one_side.lines)))
        )
        self._add_insert_messages(
            two_side, tuple(range(two_line_pos, len(two_side.lines)))
        )

    def _diff_block_by_lines(
        self, one_side: _SeriesDiffBlockSide, two_side: _SeriesDiffBlockSide
    ):
        """Compare a large subtitle block using line-level fallback alignment.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
        """
        spans: list[_LineSpan] = []
        matcher = difflib.SequenceMatcher(
            None, one_side.normlines, two_side.normlines, autojunk=False
        )
        for tag, one_start, one_end, two_start, two_end in matcher.get_opcodes():
            if tag == "equal":
                continue
            spans.append(
                (tuple(range(one_start, one_end)), tuple(range(two_start, two_end)))
            )

        self._add_block_messages(one_side, two_side, spans)

    def _get_changed_span_kind(
        self,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
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
                None, one_joined, two_joined, autojunk=False
            ).ratio()
            if ratio >= self.similarity_cutoff:
                kind = LineDiffKind.SHIFT
            else:
                kind = LineDiffKind.EDIT

        return kind

    def _get_context_line_idxs(
        self,
        *,
        source_side: _SeriesDiffBlockSide,
        target_side: _SeriesDiffBlockSide,
        source_pos: int,
        target_pos: int,
    ) -> tuple[int, ...]:
        """Get similar target-side context lines for a one-sided character edit.

        Arguments:
            source_side: side containing the one-sided edited character
            target_side: side from which to borrow an aligned context line
            source_pos: character position on the source side
            target_pos: current character position on the target side
        Returns:
            target-side local line indices similar to the edited source line
        """
        source_line_idxs = source_side.char_line_idxs[source_pos]
        if len(source_line_idxs) != 1:
            return ()

        candidates = []
        if target_pos > 0:
            candidates.extend(target_side.char_line_idxs[target_pos - 1])
        if target_pos < len(target_side.char_line_idxs):
            candidates.extend(target_side.char_line_idxs[target_pos])

        source_idx = source_line_idxs[0]
        source_text = source_side.normlines[source_idx]
        context_idxs = []
        for candidate_idx in candidates:
            if candidate_idx in context_idxs:
                continue
            candidate_text = target_side.normlines[candidate_idx]
            ratio = difflib.SequenceMatcher(
                None, source_text, candidate_text, autojunk=False
            ).ratio()
            if ratio >= self.similarity_cutoff:
                context_idxs.append(candidate_idx)

        return tuple(context_idxs)

    @staticmethod
    def _get_changed_line_idxs(
        side: _SeriesDiffBlockSide, char_pos: int, operation: pairwise.Operation
    ) -> tuple[int, ...]:
        """Get local line indices touched by a changed character.

        Arguments:
            side: block side containing the changed character
            char_pos: position of the changed character in side text
            operation: alignment operation involving the character
        Returns:
            local line indices touched by the changed character
        """
        line_idxs = side.char_line_idxs[char_pos]
        char = side.text[char_pos]
        if char == "\n" and operation in {
            pairwise.Operation.DELETE,
            pairwise.Operation.INSERT,
        }:
            return (line_idxs[-1],)
        return line_idxs

    def _get_separator_only_changed_span(
        self,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        changed_columns: list[tuple[pairwise.Operation, int, int]],
    ) -> _LineSpan | None:
        """Get changed line spans for a changed separator-only run.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            changed_columns: changed alignment columns in the current run
        Returns:
            line spans if the run is only an inserted/deleted separator newline
        """
        if len(changed_columns) != 1:
            return None

        span = self._get_separator_span(one_side, two_side, changed_columns[0])
        if span is None:
            return None
        one_local_idxs, two_local_idxs = span
        if not self._is_separator_span_valid(
            one_side, two_side, one_local_idxs, two_local_idxs
        ):
            return None

        return span

    def _is_separator_span_valid(
        self,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        one_local_idxs: tuple[int, ...],
        two_local_idxs: tuple[int, ...],
    ) -> bool:
        """Check whether a separator-only changed span should be paired.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            one_local_idxs: local line indices touched on the first side
            two_local_idxs: local line indices touched on the second side
        Returns:
            whether the separator-only span should be paired
        """
        if not one_local_idxs or not two_local_idxs:
            return False
        if not self._are_lines_similar(
            one_side, two_side, one_local_idxs, two_local_idxs
        ):
            return False
        if len(one_local_idxs) > len(two_local_idxs):
            target_text = SeriesDiff._join_normlines(two_side, two_local_idxs)
            if not self._are_separator_lines_covered(
                one_side, one_local_idxs, target_text
            ):
                return False
        elif len(two_local_idxs) > len(one_local_idxs):
            target_text = SeriesDiff._join_normlines(one_side, one_local_idxs)
            if not self._are_separator_lines_covered(
                two_side, two_local_idxs, target_text
            ):
                return False

        return True

    @staticmethod
    def _get_separator_span(
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        changed_column: tuple[pairwise.Operation, int, int],
    ) -> _LineSpan | None:
        """Get line spans for one changed separator column.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            changed_column: changed alignment column
        Returns:
            line spans if the column is an inserted/deleted separator newline
        """
        operation, one_pos, two_pos = changed_column
        if operation == pairwise.Operation.DELETE:
            return SeriesDiff._get_separator_delete_span(
                one_side, two_side, one_pos, two_pos
            )
        if operation == pairwise.Operation.INSERT:
            return SeriesDiff._get_separator_insert_span(
                one_side, two_side, one_pos, two_pos
            )
        return None

    @staticmethod
    def _get_separator_delete_span(
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        one_pos: int,
        two_pos: int,
    ) -> _LineSpan | None:
        """Get line spans for a deleted separator newline.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            one_pos: first-side character position
            two_pos: second-side character position
        Returns:
            line spans if the deleted character is a line separator
        """
        if one_side.text[one_pos] != "\n":
            return None
        one_local_idxs = one_side.char_line_idxs[one_pos]
        if len(one_local_idxs) != 2:
            return None
        two_local_idxs = SeriesDiff._get_separator_target_line_idxs(two_side, two_pos)
        return (one_local_idxs, two_local_idxs)

    @staticmethod
    def _get_separator_insert_span(
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        one_pos: int,
        two_pos: int,
    ) -> _LineSpan | None:
        """Get line spans for an inserted separator newline.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            one_pos: first-side character position
            two_pos: second-side character position
        Returns:
            line spans if the inserted character is a line separator
        """
        if two_side.text[two_pos] != "\n":
            return None
        one_local_idxs = SeriesDiff._get_separator_target_line_idxs(one_side, one_pos)
        two_local_idxs = two_side.char_line_idxs[two_pos]
        if len(two_local_idxs) != 2:
            return None
        return (one_local_idxs, two_local_idxs)

    @staticmethod
    def _get_separator_target_line_idxs(
        side: _SeriesDiffBlockSide, target_pos: int
    ) -> tuple[int, ...]:
        """Get the target line bridged by a removed or inserted separator.

        Arguments:
            side: target side without the changed separator
            target_pos: target-side character position opposite the separator
        Returns:
            local line index bridged by the separator
        """
        if target_pos <= 0 or target_pos >= len(side.char_line_idxs):
            return ()

        previous_line_idxs = side.char_line_idxs[target_pos - 1]
        next_line_idxs = side.char_line_idxs[target_pos]
        bridged_line_idxs = tuple(
            line_idx for line_idx in previous_line_idxs if line_idx in next_line_idxs
        )
        if len(bridged_line_idxs) != 1:
            return ()
        return bridged_line_idxs

    def _are_separator_lines_covered(
        self, side: _SeriesDiffBlockSide, local_idxs: tuple[int, ...], target_text: str
    ) -> bool:
        """Check whether each separator-side line is covered by target text.

        Arguments:
            side: side containing the inserted or deleted separator
            local_idxs: local line indices touched by the separator
            target_text: joined text on the opposite side
        Returns:
            whether every touched line is mostly represented in target text
        """
        target_compact = remove_punc_and_whitespace(target_text)
        line_coverage_cutoff = max(self.similarity_cutoff, 0.7)
        combined_coverage_cutoff = max(self.similarity_cutoff, 0.75)
        lines_compact = ""
        for local_idx in local_idxs:
            line_compact = remove_punc_and_whitespace(side.normlines[local_idx])
            if not line_compact:
                continue
            lines_compact += line_compact
            best_ratio = self._get_best_substring_similarity(
                line_compact, target_compact
            )
            if best_ratio < line_coverage_cutoff:
                return False

        combined_ratio = self._get_best_substring_similarity(
            lines_compact, target_compact
        )
        return combined_ratio >= combined_coverage_cutoff

    @staticmethod
    def _get_best_substring_similarity(needle: str, haystack: str) -> float:
        """Get the best nearby-length substring similarity for a text span.

        Arguments:
            needle: text to search for
            haystack: text that may contain the needle text
        Returns:
            best similarity against a nearby-length haystack substring
        """
        if not needle or not haystack:
            return 0.0

        if len(haystack) <= len(needle):
            return difflib.SequenceMatcher(
                None, needle, haystack, autojunk=False
            ).ratio()

        best_ratio = 0.0
        min_candidate_length = max(1, len(needle) - 1)
        max_candidate_length = min(len(haystack), len(needle) + 1)
        for candidate_length in range(min_candidate_length, max_candidate_length + 1):
            for start_idx in range(len(haystack) - candidate_length + 1):
                candidate = haystack[start_idx : start_idx + candidate_length]
                ratio = difflib.SequenceMatcher(
                    None, needle, candidate, autojunk=False
                ).ratio()
                best_ratio = max(best_ratio, ratio)

        return best_ratio

    @staticmethod
    def _get_implicit_line_similarity(one_text: str, two_text: str) -> float:
        """Score full-line or contained-line similarity for implicit pairing.

        Arguments:
            one_text: normalized first-side line
            two_text: normalized second-side line
        Returns:
            best full-line or substring similarity
        """
        full_ratio = difflib.SequenceMatcher(
            None, one_text, two_text, autojunk=False
        ).ratio()
        one_compact = remove_punc_and_whitespace(one_text)
        two_compact = remove_punc_and_whitespace(two_text)
        substring_ratio = 0.0
        if one_compact and two_compact:
            if len(one_compact) <= len(two_compact):
                if one_compact in two_compact:
                    substring_ratio = 1.0
            elif two_compact in one_compact:
                substring_ratio = 1.0
        return max(full_ratio, substring_ratio)

    def _split_uncovered_multiline_spans(
        self,
        spans: list[_LineSpan],
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
    ) -> list[_LineSpan]:
        """Split unrelated extra lines out of one-to-many changed spans.

        Arguments:
            spans: changed spans
            one_side: first side of the current block
            two_side: second side of the current block
        Returns:
            changed spans with unrelated extra lines separated
        """
        split_spans: list[_LineSpan] = []
        for one_idxs, two_idxs in spans:
            if len(one_idxs) == 1 and len(two_idxs) > 1:
                split_spans.extend(
                    self._split_uncovered_multiline_span(
                        one_side, two_side, one_idxs[0], two_idxs, single_position=0
                    )
                )
            elif len(two_idxs) == 1 and len(one_idxs) > 1:
                split_spans.extend(
                    self._split_uncovered_multiline_span(
                        two_side, one_side, two_idxs[0], one_idxs, single_position=1
                    )
                )
            else:
                split_spans.append((one_idxs, two_idxs))

        return split_spans

    def _split_uncovered_multiline_span(
        self,
        single_side: _SeriesDiffBlockSide,
        multi_side: _SeriesDiffBlockSide,
        single_idx: int,
        multi_idxs: tuple[int, ...],
        *,
        single_position: int,
    ) -> list[_LineSpan]:
        """Split unrelated lines out of a one-to-many changed span.

        Arguments:
            single_side: side containing the single changed line
            multi_side: side containing multiple changed lines
            single_idx: single-side local line index
            multi_idxs: multi-side local line indices
            single_position: position of the single side in returned spans
        Returns:
            one or more changed spans
        """
        target_text = self._join_normlines(single_side, (single_idx,))
        for prefix in (True, False):
            if prefix:
                paired_multi_idx = multi_idxs[0]
                remaining_multi_idxs = multi_idxs[1:]
            else:
                paired_multi_idx = multi_idxs[-1]
                remaining_multi_idxs = multi_idxs[:-1]

            if not self._should_split_uncovered_multiline_span(
                multi_side,
                single_side,
                paired_multi_idx,
                single_idx,
                remaining_multi_idxs,
                target_text,
            ):
                continue

            if single_position == 0:
                paired_span: _LineSpan = ((single_idx,), (paired_multi_idx,))
                remaining_span: _LineSpan = ((), remaining_multi_idxs)
            else:
                paired_span = ((paired_multi_idx,), (single_idx,))
                remaining_span = (remaining_multi_idxs, ())

            paired_spans = [paired_span]
            if (
                single_side.normlines[single_idx]
                == multi_side.normlines[paired_multi_idx]
            ):
                paired_spans = []
            if prefix:
                return [*paired_spans, remaining_span]
            return [remaining_span, *paired_spans]

        if single_position == 0:
            return [((single_idx,), multi_idxs)]
        return [(multi_idxs, (single_idx,))]

    def _claim_temporally_supported_boundary_gaps(
        self,
        spans: list[_LineSpan],
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
    ) -> list[_LineSpan]:
        """Include unclaimed leading lines supported by text and timing.

        Character alignment can omit an unchanged prefix line from a split
        when the separator beside it is part of a larger edit. This expands
        the following span when the single opposite-side line represents both
        the omitted prefix and the already-claimed line.

        Arguments:
            spans: changed spans
            one_side: first side of the current block
            two_side: second side of the current block
        Returns:
            changed spans expanded across supported leading gaps
        """
        claimed: list[_LineSpan] = []
        sides = (one_side, two_side)
        for raw_span, gaps in self._iter_spans_with_leading_gaps(spans):
            span = [*raw_span]
            for single_position, multi_position in ((0, 1), (1, 0)):
                single_idxs = span[single_position]
                if (
                    gaps[single_position]
                    or not gaps[multi_position]
                    or len(single_idxs) != 1
                ):
                    continue
                candidate_multi_idxs = (*gaps[multi_position], *span[multi_position])
                if self._is_temporally_supported_multiline_span(
                    sides[multi_position],
                    sides[single_position],
                    single_idxs[0],
                    candidate_multi_idxs,
                ):
                    span[multi_position] = candidate_multi_idxs

            claimed.append((span[0], span[1]))

        return claimed

    def _unclaim_shifted_boundary_lines(
        self,
        spans: list[_LineSpan],
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
    ) -> list[_LineSpan]:
        """Release span-leading lines that match an opposite-side gap.

        Character alignment can attach a line to a later changed span when an
        earlier subtitle is split on only one side. Releasing matching leading
        lines lets line-level alignment pair them across that shifted boundary.

        Arguments:
            spans: changed spans
            one_side: first side of the current block
            two_side: second side of the current block
        Returns:
            changed spans with shifted boundary lines released
        """
        unclaimed: list[_LineSpan] = []
        sides = (one_side, two_side)
        for raw_span, gaps in self._iter_spans_with_leading_gaps(spans):
            span = [*raw_span]
            for line_position, gap_position in ((0, 1), (1, 0)):
                line_idxs = span[line_position]
                if gaps[line_position] or not gaps[gap_position] or not line_idxs:
                    continue
                released_count = 0
                for line_idx, gap_idx in zip(
                    line_idxs, gaps[gap_position], strict=False
                ):
                    if not self._are_lines_similar(
                        sides[line_position],
                        sides[gap_position],
                        (line_idx,),
                        (gap_idx,),
                    ):
                        break
                    released_count += 1
                span[line_position] = line_idxs[released_count:]

            if span[0] or span[1]:
                unclaimed.append((span[0], span[1]))

        return unclaimed

    @staticmethod
    def _iter_spans_with_leading_gaps(
        spans: list[_LineSpan],
    ) -> Iterator[tuple[_LineSpan, _LineSpan]]:
        """Iterate over changed spans and their unclaimed leading lines.

        Arguments:
            spans: changed spans in block order
        Yields:
            each raw span and its first- and second-side leading gaps
        """
        positions = [0, 0]
        for span in spans:
            starts = []
            for position, line_idxs in enumerate(span):
                if line_idxs:
                    start = line_idxs[0]
                else:
                    start = positions[position]
                starts.append(start)
            gaps: _LineSpan = (
                tuple(range(positions[0], starts[0])),
                tuple(range(positions[1], starts[1])),
            )
            yield span, gaps
            for position, line_idxs in enumerate(span):
                if line_idxs:
                    positions[position] = line_idxs[-1] + 1

    def _is_temporally_supported_multiline_span(
        self,
        multi_side: _SeriesDiffBlockSide,
        single_side: _SeriesDiffBlockSide,
        single_idx: int,
        multi_idxs: tuple[int, ...],
    ) -> bool:
        """Check text and timing support for a weak multiline match.

        Arguments:
            multi_side: side with multiple changed lines
            single_side: side with one changed line
            single_idx: single-side local line index
            multi_idxs: multi-side line indices in the span
        Returns:
            whether each line and the combined span have sufficient evidence
        """
        target_compact = remove_punc_and_whitespace(single_side.normlines[single_idx])
        if not multi_idxs or not target_compact:
            return False

        line_similarity_cutoff = max(0.4, self.similarity_cutoff - 0.2)
        for multi_idx in multi_idxs:
            line_compact = remove_punc_and_whitespace(multi_side.normlines[multi_idx])
            if len(multi_idxs) > 1 and line_compact == target_compact:
                return False
            if (
                self._get_best_substring_similarity(line_compact, target_compact)
                < line_similarity_cutoff
            ):
                return False

        multi_compact = remove_punc_and_whitespace(
            self._join_normlines(multi_side, multi_idxs)
        )
        timing_similarity_cutoff = max(0.5, self.similarity_cutoff - 0.1)
        if (
            self._get_best_substring_similarity(multi_compact, target_compact)
            <= timing_similarity_cutoff
        ):
            return False
        return self._are_lines_temporally_aligned(
            single_side, multi_side, single_idx, multi_idxs
        )

    def _should_split_uncovered_multiline_span(
        self,
        multi_side: _SeriesDiffBlockSide,
        single_side: _SeriesDiffBlockSide,
        paired_multi_idx: int,
        single_idx: int,
        remaining_multi_idxs: tuple[int, ...],
        target_text: str,
    ) -> bool:
        """Check whether extra multiline span lines should be split out.

        Arguments:
            multi_side: side with multiple changed lines
            single_side: side with one changed line
            paired_multi_idx: multi-side line index paired with the single line
            single_idx: single-side line index
            remaining_multi_idxs: other multi-side line indices
            target_text: joined single-side text
        Returns:
            whether to split the remaining multi-side lines out
        """
        if not remaining_multi_idxs:
            return False
        all_multi_idxs = tuple(sorted((paired_multi_idx, *remaining_multi_idxs)))
        if self._are_separator_lines_covered(multi_side, all_multi_idxs, target_text):
            return False
        target_compact = remove_punc_and_whitespace(target_text)
        if not self._are_lines_similar(
            single_side, multi_side, (single_idx,), (paired_multi_idx,)
        ):
            paired_text = remove_punc_and_whitespace(
                multi_side.normlines[paired_multi_idx]
            )
            coverage_cutoff = max(self.similarity_cutoff, 0.75)
            if (
                self._get_best_substring_similarity(paired_text, target_compact)
                < coverage_cutoff
            ):
                return False
        if self._is_temporally_supported_multiline_span(
            multi_side, single_side, single_idx, all_multi_idxs
        ):
            return False
        return not self._are_separator_lines_covered(
            multi_side, remaining_multi_idxs, target_text
        )

    def _merge_adjacent_one_sided_spans(
        self,
        spans: list[_LineSpan],
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
    ) -> list[_LineSpan]:
        """Merge adjacent one-sided spans whose line text is similar.

        Arguments:
            spans: changed spans
            one_side: first side of the current block
            two_side: second side of the current block
        Returns:
            changed spans with similar adjacent one-sided spans paired
        """
        merged: list[_LineSpan] = []
        idx = 0
        while idx < len(spans):
            if idx + 1 >= len(spans):
                merged.append(spans[idx])
                idx += 1
                continue

            one_idxs, two_idxs = spans[idx]
            next_one_idxs, next_two_idxs = spans[idx + 1]
            if self._should_merge_adjacent_one_sided_spans(
                one_side, two_side, one_idxs, two_idxs, next_one_idxs, next_two_idxs
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
    def _fill_changed_span_gaps(spans: list[_LineSpan]) -> list[_LineSpan]:
        """Include implicit line matches enclosed by changed line spans.

        Arguments:
            spans: changed line spans
        Returns:
            changed spans with enclosed local line indices included
        """
        filled: list[_LineSpan] = []
        for one_idxs, two_idxs in spans:
            filled_one_idxs: _LineIndexes
            if one_idxs:
                filled_one_idxs = tuple(range(one_idxs[0], one_idxs[-1] + 1))
            else:
                filled_one_idxs = ()
            filled_two_idxs: _LineIndexes
            if two_idxs:
                filled_two_idxs = tuple(range(two_idxs[0], two_idxs[-1] + 1))
            else:
                filled_two_idxs = ()
            filled.append((filled_one_idxs, filled_two_idxs))
        return filled

    def _should_merge_adjacent_one_sided_spans(
        self,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
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
        should_merge = False
        if one_idxs and two_idxs:
            return should_merge
        if next_one_idxs and next_two_idxs:
            return should_merge
        if bool(one_idxs) == bool(next_one_idxs):
            return should_merge
        if len(one_idxs) + len(next_one_idxs) == 1:
            if len(two_idxs) + len(next_two_idxs) == 1:
                merged_one_idxs = tuple(sorted({*one_idxs, *next_one_idxs}))
                merged_two_idxs = tuple(sorted({*two_idxs, *next_two_idxs}))
                if abs(merged_one_idxs[0] - merged_two_idxs[0]) <= 1:
                    should_merge = self._are_lines_similar(
                        one_side, two_side, merged_one_idxs, merged_two_idxs
                    )

        return should_merge

    @staticmethod
    def _get_block_event_index_pairs_by_pause(
        one: Series, two: Series, pause_length: int = 3000
    ) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
        """Split a pair of series into event-index blocks using pauses.

        This mirrors synchronization block splitting while preserving original
        series indices for diff output.

        Arguments:
            one: first subtitle series
            two: second subtitle series
            pause_length: split whenever a pause of this length is encountered
        Returns:
            pairs of event-index blocks
        """
        blocks = []
        source_one = list(range(len(one.events)))
        source_two = list(range(len(two.events)))

        def get_nascent_block_cutoff() -> int:
            """Get latest acceptable start for the nascent block.

            Returns:
                latest event start time included in the nascent block
            """
            cutoff = 0
            if nascent_block_one:
                cutoff = max(cutoff, one.events[nascent_block_one[-1]].end)
            if nascent_block_two:
                cutoff = max(cutoff, two.events[nascent_block_two[-1]].end)
            return cutoff + pause_length

        while source_one or source_two:
            nascent_block_one: list[int] = []
            nascent_block_two: list[int] = []
            if source_one and source_two:
                if one.events[source_one[0]].start <= two.events[source_two[0]].start:
                    nascent_block_one.append(source_one.pop(0))
                else:
                    nascent_block_two.append(source_two.pop(0))
            elif source_one:
                nascent_block_one.append(source_one.pop(0))
            else:
                nascent_block_two.append(source_two.pop(0))

            changed = True
            while changed:
                changed = False
                while (
                    source_one
                    and one.events[source_one[0]].start < get_nascent_block_cutoff()
                ):
                    nascent_block_one.append(source_one.pop(0))
                    changed = True
                while (
                    source_two
                    and two.events[source_two[0]].start < get_nascent_block_cutoff()
                ):
                    nascent_block_two.append(source_two.pop(0))
                    changed = True

            blocks.append((tuple(nascent_block_one), tuple(nascent_block_two)))

        return blocks

    @staticmethod
    def _get_block_side(
        event_idxs: tuple[int, ...],
        line_records: list[tuple[_SeriesDiffLineRecord, ...]],
    ) -> _SeriesDiffBlockSide:
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
        times = tuple((record.start, record.end) for record in records)

        chunks: list[str] = []
        char_line_idxs: list[tuple[int, ...]] = []
        for local_idx, normline in enumerate(normlines):
            if local_idx > 0:
                chunks.append("\n")
                char_line_idxs.append((local_idx - 1, local_idx))
            chunks.append(normline)
            char_line_idxs.extend((local_idx,) for _ in normline)

        return _SeriesDiffBlockSide(
            line_idxs=line_idxs,
            lines=lines,
            normlines=normlines,
            times=times,
            text="".join(chunks),
            char_line_idxs=tuple(char_line_idxs),
        )

    @staticmethod
    def _get_series_event_line_records(
        series: Series,
    ) -> list[tuple[_SeriesDiffLineRecord, ...]]:
        """Extract text line records grouped by subtitle event.

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
                            norm=SeriesDiff._normalize_line(stripped),
                            start=subtitle.start,
                            end=subtitle.end,
                        )
                    )
                    line_idx += 1
            event_records.append(tuple(records))
        return event_records

    def _get_third_texts(self, message: LineDiff, three: Series) -> tuple[str, ...]:
        """Get third-side texts corresponding to a diff message's first-side events.

        Arguments:
            message: diff message for which to get third-side text
            three: one-to-one third subtitle series
        Returns:
            third-side subtitle texts in first-side event order
        """
        event_idxs = self._get_message_event_indices(
            message.one_idxs, self._one_line_event_idxs
        )

        texts = []
        for event_idx in event_idxs:
            event_texts = []
            for line in three.events[event_idx].text_with_newline.splitlines():
                stripped = line.strip()
                if stripped:
                    event_texts.append(stripped)
            if event_texts:
                texts.extend(event_texts)
            else:
                texts.append("")

        return tuple(texts)

    @staticmethod
    def _get_message_event_indices(
        line_idxs: tuple[int, ...] | None, line_event_idxs: tuple[int, ...]
    ) -> tuple[int, ...]:
        """Map line indices to unique subtitle event indices in order.

        Arguments:
            line_idxs: zero-based flattened line indices
            line_event_idxs: event index corresponding to each flattened line
        Returns:
            unique zero-based subtitle event indices
        """
        event_idxs = []
        for line_idx in line_idxs or ():
            event_idx = line_event_idxs[line_idx]
            if event_idxs and event_idxs[-1] == event_idx:
                continue
            event_idxs.append(event_idx)
        return tuple(event_idxs)

    @staticmethod
    def _join_normlines(side: _SeriesDiffBlockSide, local_idxs: tuple[int, ...]) -> str:
        """Join normalized lines for classification.

        Arguments:
            side: block side containing normalized lines
            local_idxs: local line indices to join
        Returns:
            normalized lines joined with spaces
        """
        return " ".join(side.normlines[idx] for idx in local_idxs)

    @staticmethod
    def _merge_changed_spans(spans: list[_LineSpan]) -> list[_LineSpan]:
        """Merge changed character spans that project to the same line change.

        Arguments:
            spans: raw changed spans from character alignment
        Returns:
            merged line-level changed spans
        """
        merged: list[_LineSpan] = []
        for next_one, next_two in spans:
            merged.append((next_one, next_two))
            while len(merged) >= 2:
                prev_one, prev_two = merged[-2]
                current_one, current_two = merged[-1]
                if not SeriesDiff._should_merge_changed_spans(
                    prev_one, prev_two, current_one, current_two
                ):
                    break
                one_idxs = tuple(sorted({*prev_one, *current_one}))
                two_idxs = tuple(sorted({*prev_two, *current_two}))
                merged[-2:] = [(one_idxs, two_idxs)]
        return merged

    @staticmethod
    def _normalize_line(text: str) -> str:
        """Normalize a subtitle line for approximate matching.

        Arguments:
            text: subtitle line to normalize
        Returns:
            normalized line
        """
        stripped = re.sub(r"(?:^|\s)(?:[-–])\s+", " ", text.strip())
        normalized = re.sub(r"\s+", " ", stripped).strip()
        return normalized

    @staticmethod
    def _get_implicit_candidate_indices(
        spans: list[_LineSpan],
        span_idx: int,
        candidate_side_position: int,
        claimed_candidate_idxs: set[int],
        candidate_line_count: int,
        source_idx: int,
    ) -> tuple[int, ...]:
        """Get nearby unclaimed candidates between surrounding span anchors.

        Arguments:
            spans: changed spans
            span_idx: index of the one-sided span being paired
            candidate_side_position: tuple position of the candidate side
            claimed_candidate_idxs: candidate indices already used by spans
            candidate_line_count: total candidate-side line count
            source_idx: source-side line index used for proximity filtering
        Returns:
            nearby candidate-side line indices
        """
        candidate_start = 0
        for previous_span in reversed(spans[:span_idx]):
            previous_idxs = previous_span[candidate_side_position]
            if previous_idxs:
                candidate_start = previous_idxs[-1] + 1
                break

        candidate_stop = candidate_line_count
        for next_span in spans[span_idx + 1 :]:
            next_idxs = next_span[candidate_side_position]
            if next_idxs:
                candidate_stop = next_idxs[0]
                break

        return tuple(
            candidate_idx
            for candidate_idx in range(candidate_start, candidate_stop)
            if candidate_idx not in claimed_candidate_idxs
            and abs(candidate_idx - source_idx) <= 2
        )

    def _pair_implicit_lines(
        self,
        source_idxs: tuple[int, ...],
        candidate_idxs: tuple[int, ...],
        source_side: _SeriesDiffBlockSide,
        candidate_side: _SeriesDiffBlockSide,
        claimed_candidate_idxs: set[int],
        *,
        source_side_position: int,
    ) -> list[_LineSpan]:
        """Pair one-sided source lines with similar implicit candidates.

        Arguments:
            source_idxs: one-sided source line indices
            candidate_idxs: nearby unclaimed candidate line indices
            source_side: block side containing source lines
            candidate_side: block side containing candidate lines
            claimed_candidate_idxs: candidate indices already used by spans
            source_side_position: tuple position of the source side
        Returns:
            one-sided or paired replacement spans
        """
        paired = []
        previous_match = -1
        for source_idx in source_idxs:
            best_candidate_idx = None
            best_ratio = 0.0
            for candidate_idx in candidate_idxs:
                if candidate_idx <= previous_match:
                    continue
                ratio = self._get_implicit_line_similarity(
                    source_side.normlines[source_idx],
                    candidate_side.normlines[candidate_idx],
                )
                if ratio < self.similarity_cutoff:
                    continue
                if best_candidate_idx is not None and ratio <= best_ratio:
                    continue
                best_candidate_idx = candidate_idx
                best_ratio = ratio

            if source_side_position == 0:
                span = ((source_idx,), ())
                if best_candidate_idx is not None:
                    span = ((source_idx,), (best_candidate_idx,))
            else:
                span = ((), (source_idx,))
                if best_candidate_idx is not None:
                    span = ((best_candidate_idx,), (source_idx,))
            paired.append(span)

            if best_candidate_idx is not None:
                claimed_candidate_idxs.add(best_candidate_idx)
                previous_match = best_candidate_idx
        return paired

    def _pair_one_sided_spans_with_implicit_lines(
        self,
        spans: list[_LineSpan],
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
    ) -> list[_LineSpan]:
        """Pair one-sided spans with similar implicit lines in their interval.

        Arguments:
            spans: changed spans
            one_side: first side of the current block
            two_side: second side of the current block
        Returns:
            changed spans with similar implicit lines paired
        """
        claimed_one_idxs = {one_idx for one_idxs, _ in spans for one_idx in one_idxs}
        claimed_two_idxs = {two_idx for _, two_idxs in spans for two_idx in two_idxs}
        paired: list[_LineSpan] = []
        for idx, (one_idxs, two_idxs) in enumerate(spans):
            if one_idxs and two_idxs:
                paired.append((one_idxs, two_idxs))
                continue
            if two_idxs:
                candidate_one_idxs = self._get_implicit_candidate_indices(
                    spans, idx, 0, claimed_one_idxs, len(one_side.lines), two_idxs[0]
                )
                paired.extend(
                    self._pair_implicit_lines(
                        two_idxs,
                        candidate_one_idxs,
                        two_side,
                        one_side,
                        claimed_one_idxs,
                        source_side_position=1,
                    )
                )
                continue
            candidate_two_idxs = self._get_implicit_candidate_indices(
                spans, idx, 1, claimed_two_idxs, len(two_side.lines), one_idxs[0]
            )
            paired.extend(
                self._pair_implicit_lines(
                    one_idxs,
                    candidate_two_idxs,
                    one_side,
                    two_side,
                    claimed_two_idxs,
                    source_side_position=0,
                )
            )
        return paired

    def _are_lines_similar(
        self,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        one_local_idxs: tuple[int, ...],
        two_local_idxs: tuple[int, ...],
    ) -> bool:
        """Check whether two line spans are similar enough to pair.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            one_local_idxs: local line indices from the first side
            two_local_idxs: local line indices from the second side
        Returns:
            whether line spans are similar enough to pair
        """
        one_text = self._join_normlines(one_side, one_local_idxs)
        two_text = self._join_normlines(two_side, two_local_idxs)
        ratio = difflib.SequenceMatcher(
            None, one_text, two_text, autojunk=False
        ).ratio()
        return ratio >= self.similarity_cutoff

    @staticmethod
    def _are_lines_temporally_aligned(
        single_side: _SeriesDiffBlockSide,
        multi_side: _SeriesDiffBlockSide,
        single_idx: int,
        multi_idxs: tuple[int, ...],
        tolerance: int = 100,
    ) -> bool:
        """Check whether one line overlaps or closely meets opposite-side lines.

        Arguments:
            single_side: side containing one line
            multi_side: side containing multiple lines
            single_idx: single-side local line index
            multi_idxs: multi-side local line indices
            tolerance: allowed boundary separation in milliseconds
        Returns:
            whether the single subtitle aligns temporally with every line
        """
        single_start, single_end = single_side.times[single_idx]
        return all(
            min(single_end, multi_side.times[multi_idx][1]) + tolerance
            >= max(single_start, multi_side.times[multi_idx][0])
            for multi_idx in multi_idxs
        )

    def _validate_message_coverage(self):
        """Validate that complete output represents every input line exactly once.

        Raises:
            RuntimeError: if a line is missing or duplicated
        """
        if any(
            message.kind is LineDiffKind.EQUAL
            and tuple(self._normalize_line(text) for text in message.one_texts or ())
            != tuple(self._normalize_line(text) for text in message.two_texts or ())
            for message in self._stacked_messages
        ):
            raise RuntimeError("Series diff marked unequal subtitle lines as equal")

        one_idxs = sorted(
            idx for message in self._stacked_messages for idx in message.one_idxs or ()
        )
        two_idxs = sorted(
            idx for message in self._stacked_messages for idx in message.two_idxs or ()
        )
        if one_idxs != list(range(len(self._one_line_event_idxs))):
            raise RuntimeError(
                "Series diff failed to represent every first-side subtitle line"
            )
        if two_idxs != list(range(len(self._two_line_event_idxs))):
            raise RuntimeError(
                "Series diff failed to represent every second-side subtitle line"
            )

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
        if set(prev_one) & set(next_one):
            return True
        if set(prev_two) & set(next_two):
            return True
        return False
