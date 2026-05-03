#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series-level line diffing."""

from __future__ import annotations

import difflib
import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import TypedDict

from scinoephile.analysis.line_alignment import LineAlignment, LineAlignmentOperation
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import are_series_one_to_one

from .line_diff import LineDiff
from .line_diff_kind import LineDiffKind

__all__ = [
    "SeriesDiff",
    "SeriesDiffKwargs",
]


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


@dataclass(frozen=True)
class _SeriesDiffBlockSide:
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
            similarity_cutoff: similarity cutoff for many-to-many shifted text
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
        messages = self._stacked_messages if include_equal else self.messages
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
                color=color,
                three_texts=self._get_third_texts(message, three),
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
        while one_line_pos < one_line_stop and two_line_pos < two_line_stop:
            self._add_equal_message(
                one_side=one_side,
                two_side=two_side,
                one_local_idxs=(one_line_pos,),
                two_local_idxs=(two_line_pos,),
            )
            one_line_pos += 1
            two_line_pos += 1

        return one_line_pos, two_line_pos

    def _add_delete_messages(
        self,
        one_side: _SeriesDiffBlockSide,
        one_local_idxs: tuple[int, ...],
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
        self,
        two_side: _SeriesDiffBlockSide,
        two_local_idxs: tuple[int, ...],
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
        block_pairs = self._get_block_event_index_pairs_by_pause(one, two)
        for one_event_idxs, two_event_idxs in block_pairs:
            one_side = self._get_block_side(one_event_idxs, one_line_records)
            two_side = self._get_block_side(two_event_idxs, two_line_records)
            self._diff_block(one_side, two_side)
        return self.messages

    def _diff_block(
        self,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
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
        changed_columns: list[tuple[LineAlignmentOperation, int, int]] = []
        spans: list[tuple[tuple[int, ...], tuple[int, ...]]] = []

        def flush_changed():
            """Record the current changed span."""
            if not one_changed and not two_changed:
                return
            separator_span = self._get_separator_only_changed_span(
                one_side,
                two_side,
                changed_columns,
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

        for column in LineAlignment(one_side.text, two_side.text).alignment_pairs:
            if column.operation == LineAlignmentOperation.MATCH:
                flush_changed()
            else:
                changed_columns.append((column.operation, one_pos, two_pos))
                if column.one is not None:
                    one_changed.update(
                        self._get_changed_line_idxs(
                            one_side,
                            one_pos,
                            column.operation,
                        )
                    )
                if column.two is not None:
                    two_changed.update(
                        self._get_changed_line_idxs(
                            two_side,
                            two_pos,
                            column.operation,
                        )
                    )
                if column.operation == LineAlignmentOperation.DELETE:
                    two_changed.update(
                        self._get_context_line_idxs(
                            source_side=one_side,
                            target_side=two_side,
                            source_pos=one_pos,
                            target_pos=two_pos,
                        )
                    )
                if column.operation == LineAlignmentOperation.INSERT:
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
        spans = self._merge_adjacent_one_sided_spans(
            spans,
            one_side,
            two_side,
        )
        spans = self._pair_bracketed_one_sided_spans(spans, one_side, two_side)
        spans = self._split_uncovered_multiline_spans(spans, one_side, two_side)
        self._add_block_messages(one_side, two_side, spans)

    def _add_block_messages(
        self,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        spans: list[tuple[tuple[int, ...], tuple[int, ...]]],
    ):
        """Add equal and changed messages for a diffed block.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            spans: changed spans in block order
        """
        one_line_pos = 0
        two_line_pos = 0
        for one_local_idxs, two_local_idxs in spans:
            one_line_stop = one_line_pos
            if one_local_idxs:
                one_line_stop = one_local_idxs[0]
            two_line_stop = two_line_pos
            if two_local_idxs:
                two_line_stop = two_local_idxs[0]
            one_line_pos, two_line_pos = self._add_equal_messages_until(
                one_side=one_side,
                two_side=two_side,
                one_line_pos=one_line_pos,
                two_line_pos=two_line_pos,
                one_line_stop=one_line_stop,
                two_line_stop=two_line_stop,
            )
            self._add_changed_span(
                one_side,
                two_side,
                one_local_idxs,
                two_local_idxs,
            )
            if one_local_idxs:
                one_line_pos = one_local_idxs[-1] + 1
            if two_local_idxs:
                two_line_pos = two_local_idxs[-1] + 1
        self._add_equal_messages_until(
            one_side=one_side,
            two_side=two_side,
            one_line_pos=one_line_pos,
            two_line_pos=two_line_pos,
            one_line_stop=len(one_side.lines),
            two_line_stop=len(two_side.lines),
        )

    def _diff_block_by_lines(
        self,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
    ):
        """Compare a large subtitle block using line-level fallback alignment.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
        """
        spans: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
        matcher = difflib.SequenceMatcher(
            None,
            one_side.normlines,
            two_side.normlines,
            autojunk=False,
        )
        for tag, one_start, one_end, two_start, two_end in matcher.get_opcodes():
            if tag == "equal":
                continue
            spans.append(
                (
                    tuple(range(one_start, one_end)),
                    tuple(range(two_start, two_end)),
                )
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
                None,
                source_text,
                candidate_text,
                autojunk=False,
            ).ratio()
            if ratio >= self.similarity_cutoff:
                context_idxs.append(candidate_idx)

        return tuple(context_idxs)

    @staticmethod
    def _get_changed_line_idxs(
        side: _SeriesDiffBlockSide,
        char_pos: int,
        operation: LineAlignmentOperation,
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
            LineAlignmentOperation.DELETE,
            LineAlignmentOperation.INSERT,
        }:
            return (line_idxs[-1],)
        return line_idxs

    def _get_separator_only_changed_span(
        self,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        changed_columns: list[tuple[LineAlignmentOperation, int, int]],
    ) -> tuple[tuple[int, ...], tuple[int, ...]] | None:
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
            one_side,
            two_side,
            one_local_idxs,
            two_local_idxs,
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
            one_side,
            two_side,
            one_local_idxs,
            two_local_idxs,
        ):
            return False
        if len(one_local_idxs) > len(two_local_idxs):
            target_text = SeriesDiff._join_normlines(two_side, two_local_idxs)
            if not self._are_separator_lines_covered(
                one_side,
                one_local_idxs,
                target_text,
            ):
                return False
        elif len(two_local_idxs) > len(one_local_idxs):
            target_text = SeriesDiff._join_normlines(one_side, one_local_idxs)
            if not self._are_separator_lines_covered(
                two_side,
                two_local_idxs,
                target_text,
            ):
                return False

        return True

    @staticmethod
    def _get_separator_span(
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        changed_column: tuple[LineAlignmentOperation, int, int],
    ) -> tuple[tuple[int, ...], tuple[int, ...]] | None:
        """Get line spans for one changed separator column.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            changed_column: changed alignment column
        Returns:
            line spans if the column is an inserted/deleted separator newline
        """
        operation, one_pos, two_pos = changed_column
        if operation == LineAlignmentOperation.DELETE:
            return SeriesDiff._get_separator_delete_span(
                one_side,
                two_side,
                one_pos,
                two_pos,
            )
        if operation == LineAlignmentOperation.INSERT:
            return SeriesDiff._get_separator_insert_span(
                one_side,
                two_side,
                one_pos,
                two_pos,
            )
        return None

    @staticmethod
    def _get_separator_delete_span(
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        one_pos: int,
        two_pos: int,
    ) -> tuple[tuple[int, ...], tuple[int, ...]] | None:
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
        two_local_idxs = SeriesDiff._get_separator_target_line_idxs(
            two_side,
            two_pos,
        )
        return (one_local_idxs, two_local_idxs)

    @staticmethod
    def _get_separator_insert_span(
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        one_pos: int,
        two_pos: int,
    ) -> tuple[tuple[int, ...], tuple[int, ...]] | None:
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
        one_local_idxs = SeriesDiff._get_separator_target_line_idxs(
            one_side,
            one_pos,
        )
        two_local_idxs = two_side.char_line_idxs[two_pos]
        if len(two_local_idxs) != 2:
            return None
        return (one_local_idxs, two_local_idxs)

    @staticmethod
    def _get_separator_target_line_idxs(
        side: _SeriesDiffBlockSide,
        target_pos: int,
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
        self,
        side: _SeriesDiffBlockSide,
        local_idxs: tuple[int, ...],
        target_text: str,
    ) -> bool:
        """Check whether each separator-side line is covered by target text.

        Arguments:
            side: side containing the inserted or deleted separator
            local_idxs: local line indices touched by the separator
            target_text: joined text on the opposite side
        Returns:
            whether every touched line is mostly represented in target text
        """
        target_compact = re.sub(r"\s+", "", target_text)
        coverage_cutoff = max(self.similarity_cutoff, 0.75)
        for local_idx in local_idxs:
            line_compact = re.sub(r"\s+", "", side.normlines[local_idx])
            if not line_compact:
                continue
            best_ratio = self._get_best_substring_similarity(
                line_compact,
                target_compact,
            )
            if best_ratio < coverage_cutoff:
                return False

        return True

    @staticmethod
    def _get_best_substring_similarity(needle: str, haystack: str) -> float:
        """Get the best same-length substring similarity for a text span.

        Arguments:
            needle: text to search for
            haystack: text that may contain the needle text
        Returns:
            best similarity against a same-length haystack substring
        """
        if not needle or not haystack:
            return 0.0

        if len(haystack) <= len(needle):
            return difflib.SequenceMatcher(
                None,
                needle,
                haystack,
                autojunk=False,
            ).ratio()

        best_ratio = 0.0
        for start_idx in range(len(haystack) - len(needle) + 1):
            candidate = haystack[start_idx : start_idx + len(needle)]
            ratio = difflib.SequenceMatcher(
                None,
                needle,
                candidate,
                autojunk=False,
            ).ratio()
            best_ratio = max(best_ratio, ratio)

        return best_ratio

    def _split_uncovered_multiline_spans(
        self,
        spans: list[tuple[tuple[int, ...], tuple[int, ...]]],
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
    ) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
        """Split unrelated extra lines out of one-to-many changed spans.

        Arguments:
            spans: changed spans
            one_side: first side of the current block
            two_side: second side of the current block
        Returns:
            changed spans with unrelated extra lines separated
        """
        split_spans: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
        for one_idxs, two_idxs in spans:
            if len(one_idxs) == 1 and len(two_idxs) > 1:
                split_spans.extend(
                    self._split_uncovered_one_to_many_span(
                        one_side,
                        two_side,
                        one_idxs[0],
                        two_idxs,
                    )
                )
            elif len(two_idxs) == 1 and len(one_idxs) > 1:
                split_spans.extend(
                    self._split_uncovered_many_to_one_span(
                        one_side,
                        two_side,
                        one_idxs,
                        two_idxs[0],
                    )
                )
            else:
                split_spans.append((one_idxs, two_idxs))

        return split_spans

    def _split_uncovered_many_to_one_span(
        self,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        one_idxs: tuple[int, ...],
        two_idx: int,
    ) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
        """Split unrelated first-side lines out of a many-to-one span.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            one_idxs: first-side local line indices in the current span
            two_idx: second-side local line index in the current span
        Returns:
            one or more changed spans
        """
        target_text = SeriesDiff._join_normlines(two_side, (two_idx,))
        first_one_idx = one_idxs[0]
        remaining_one_idxs = one_idxs[1:]
        if self._should_split_uncovered_multiline_span(
            one_side,
            two_side,
            first_one_idx,
            two_idx,
            remaining_one_idxs,
            target_text,
        ):
            return self._get_split_many_to_one_spans(
                one_side,
                two_side,
                first_one_idx,
                two_idx,
                remaining_one_idxs,
                prefix=True,
            )

        last_one_idx = one_idxs[-1]
        remaining_one_idxs = one_idxs[:-1]
        if self._should_split_uncovered_multiline_span(
            one_side,
            two_side,
            last_one_idx,
            two_idx,
            remaining_one_idxs,
            target_text,
        ):
            return self._get_split_many_to_one_spans(
                one_side,
                two_side,
                last_one_idx,
                two_idx,
                remaining_one_idxs,
                prefix=False,
            )

        return [(one_idxs, (two_idx,))]

    def _split_uncovered_one_to_many_span(
        self,
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        one_idx: int,
        two_idxs: tuple[int, ...],
    ) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
        """Split unrelated second-side lines out of a one-to-many span.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            one_idx: first-side local line index in the current span
            two_idxs: second-side local line indices in the current span
        Returns:
            one or more changed spans
        """
        target_text = SeriesDiff._join_normlines(one_side, (one_idx,))
        first_two_idx = two_idxs[0]
        remaining_two_idxs = two_idxs[1:]
        if self._should_split_uncovered_multiline_span(
            two_side,
            one_side,
            first_two_idx,
            one_idx,
            remaining_two_idxs,
            target_text,
        ):
            return self._get_split_one_to_many_spans(
                one_side,
                two_side,
                one_idx,
                first_two_idx,
                remaining_two_idxs,
                prefix=True,
            )

        last_two_idx = two_idxs[-1]
        remaining_two_idxs = two_idxs[:-1]
        if self._should_split_uncovered_multiline_span(
            two_side,
            one_side,
            last_two_idx,
            one_idx,
            remaining_two_idxs,
            target_text,
        ):
            return self._get_split_one_to_many_spans(
                one_side,
                two_side,
                one_idx,
                last_two_idx,
                remaining_two_idxs,
                prefix=False,
            )

        return [((one_idx,), two_idxs)]

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
        if not self._are_lines_similar(
            single_side,
            multi_side,
            (single_idx,),
            (paired_multi_idx,),
        ):
            return False
        return not self._are_separator_lines_covered(
            multi_side,
            remaining_multi_idxs,
            target_text,
        )

    @staticmethod
    def _get_split_many_to_one_spans(
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        paired_one_idx: int,
        two_idx: int,
        remaining_one_idxs: tuple[int, ...],
        *,
        prefix: bool,
    ) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
        """Build split spans for a many-to-one span with unrelated lines.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            paired_one_idx: first-side line paired with the second-side line
            two_idx: second-side local line index
            remaining_one_idxs: unrelated first-side local line indices
            prefix: whether the paired line is before the unrelated lines
        Returns:
            changed spans
        """
        paired_span = ((paired_one_idx,), (two_idx,))
        if one_side.normlines[paired_one_idx] == two_side.normlines[two_idx]:
            paired_spans: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
        else:
            paired_spans = [paired_span]
        remaining_span = (remaining_one_idxs, ())
        if prefix:
            return [*paired_spans, remaining_span]
        return [remaining_span, *paired_spans]

    @staticmethod
    def _get_split_one_to_many_spans(
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
        one_idx: int,
        paired_two_idx: int,
        remaining_two_idxs: tuple[int, ...],
        *,
        prefix: bool,
    ) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
        """Build split spans for a one-to-many span with unrelated lines.

        Arguments:
            one_side: first side of the current block
            two_side: second side of the current block
            one_idx: first-side local line index
            paired_two_idx: second-side line paired with the first-side line
            remaining_two_idxs: unrelated second-side local line indices
            prefix: whether the paired line is before the unrelated lines
        Returns:
            changed spans
        """
        paired_span = ((one_idx,), (paired_two_idx,))
        if one_side.normlines[one_idx] == two_side.normlines[paired_two_idx]:
            paired_spans: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
        else:
            paired_spans = [paired_span]
        remaining_span = ((), remaining_two_idxs)
        if prefix:
            return [*paired_spans, remaining_span]
        return [remaining_span, *paired_spans]

    def _merge_adjacent_one_sided_spans(
        self,
        spans: list[tuple[tuple[int, ...], tuple[int, ...]]],
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
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
                        one_side,
                        two_side,
                        merged_one_idxs,
                        merged_two_idxs,
                    )

        return should_merge

    @staticmethod
    def _get_block_event_index_pairs_by_pause(
        one: Series,
        two: Series,
        pause_length: int = 3000,
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
            """Get latest acceptable start for the nascent block."""
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
        if not message.one_idxs:
            return ()

        event_idxs = []
        for line_idx in message.one_idxs:
            event_idx = self._one_line_event_idxs[line_idx]
            if event_idxs and event_idxs[-1] == event_idx:
                continue
            event_idxs.append(event_idx)

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
    def _join_normlines(
        side: _SeriesDiffBlockSide,
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
            if SeriesDiff._should_merge_changed_spans(
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

    def _pair_bracketed_one_sided_spans(
        self,
        spans: list[tuple[tuple[int, ...], tuple[int, ...]]],
        one_side: _SeriesDiffBlockSide,
        two_side: _SeriesDiffBlockSide,
    ) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
        """Pair one-sided spans bracketed by line-aligned spans.

        Arguments:
            spans: changed spans
            one_side: first side of the current block
            two_side: second side of the current block
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
                if len(missing_one_idxs) == 1 and self._are_lines_similar(
                    one_side,
                    two_side,
                    missing_one_idxs,
                    two_idxs,
                ):
                    paired.append((missing_one_idxs, two_idxs))
                    continue
            if not two_idxs and len(one_idxs) == 1:
                missing_two_idxs = tuple(range(prev_two_idxs[-1] + 1, next_two_idxs[0]))
                if len(missing_two_idxs) == 1 and self._are_lines_similar(
                    one_side,
                    two_side,
                    one_idxs,
                    missing_two_idxs,
                ):
                    paired.append((one_idxs, missing_two_idxs))
                    continue

            paired.append((one_idxs, two_idxs))
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
        if set(prev_one) & set(next_one):
            return True
        if set(prev_two) & set(next_two):
            return True
        return False
