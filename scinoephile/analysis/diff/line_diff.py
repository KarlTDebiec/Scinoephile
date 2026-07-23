#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Line-level diff records."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.analysis.line_alignment import LineAlignment, LineAlignmentOperation
from scinoephile.core.text import (
    AnsiColor,
    colorize,
    is_full_width_char,
    join_text_lines,
)

from .line_diff_kind import LineDiffKind

__all__ = ["LineDiff"]


@dataclass(frozen=True)
class LineDiff:
    """Represents a line-level difference."""

    kind: LineDiffKind
    """Kind of difference represented by this record."""

    one_lbl: str | None = None
    """Display label for the first side of the diff."""

    two_lbl: str | None = None
    """Display label for the second side of the diff."""

    one_idxs: tuple[int, ...] | None = None
    """Zero-based line indices from the first side of the diff."""

    two_idxs: tuple[int, ...] | None = None
    """Zero-based line indices from the second side of the diff."""

    one_texts: tuple[str, ...] | None = None
    """Text lines from the first side of the diff."""

    two_texts: tuple[str, ...] | None = None
    """Text lines from the second side of the diff."""

    def __str__(self) -> str:
        """Format the diff as a display string.

        Returns:
            formatted diff string
        """
        if self.one_idxs and self.one_texts and self.two_idxs is None:
            missing_idx = self.one_idxs[0]
            missing_text = self.one_texts[0]
            return (
                f"{self.kind.value}: "
                f"{self.one_lbl}[{missing_idx + 1}] "
                f"{missing_text!r} not present in {self.two_lbl}"
            )
        if self.two_idxs and self.two_texts and self.one_idxs is None:
            missing_idx = self.two_idxs[0]
            missing_text = self.two_texts[0]
            return (
                f"{self.kind.value}: "
                f"{self.two_lbl}[{missing_idx + 1}] "
                f"{missing_text!r} not present in {self.one_lbl}"
            )
        one_idxs = self.one_idxs or ()
        two_idxs = self.two_idxs or ()
        one_texts = self.one_texts or ()
        two_texts = self.two_texts or ()
        if (
            len(one_idxs) == 1
            and len(two_idxs) == 1
            and len(one_texts) == 1
            and len(two_texts) == 1
        ):
            one_text_repr = self._format_texts(one_texts)
            two_text_repr = self._format_texts(two_texts)
        else:
            one_text_repr = repr(list(one_texts))
            two_text_repr = repr(list(two_texts))
        return (
            f"{self.kind.value}: "
            f"{self.one_lbl}[{self._format_idxs(one_idxs)}] -> "
            f"{self.two_lbl}[{self._format_idxs(two_idxs)}]: "
            f"{one_text_repr} -> {two_text_repr}"
        )

    def get_aligned_texts(self) -> tuple[str, str]:
        """Get the two character-aligned text rows without display markup.

        Returns:
            first- and second-side aligned text
        """
        if self.kind == LineDiffKind.DELETE:
            return join_text_lines(self.one_texts or ()), ""
        if self.kind == LineDiffKind.INSERT:
            return "", join_text_lines(self.two_texts or ())
        if self.kind == LineDiffKind.EQUAL:
            one_text = join_text_lines(self.one_texts or ())
            two_text = join_text_lines(self.two_texts or ())
            return one_text, two_text
        return self._get_edit_aligned_texts(color=False)

    def get_stacked_str(
        self, *, color: bool = True, three_texts: tuple[str, ...] | None = None
    ) -> str:
        """Format the diff as a stacked, character-aligned display.

        Arguments:
            color: whether to emit ANSI color escapes
            three_texts: optional unaligned third-side text lines
        Returns:
            formatted, multi-line diff chunk
        """
        one_range = self._format_idxs_or_empty(self.one_idxs)
        two_range = self._format_idxs_or_empty(self.two_idxs)

        if self.kind == LineDiffKind.EQUAL:
            return self._get_equal_stacked_str(
                one_range=one_range,
                two_range=two_range,
                one_texts=self.one_texts or (),
                two_texts=self.two_texts or (),
                color=color,
                three_texts=three_texts,
            )

        if self.kind == LineDiffKind.DELETE:
            return self._get_delete_stacked_str(
                one_range=one_range,
                one_texts=self.one_texts or (),
                color=color,
                three_texts=three_texts,
            )

        if self.kind == LineDiffKind.INSERT:
            return self._get_insert_stacked_str(
                insert_idxs=self.two_idxs or (),
                insert_texts=self.two_texts or (),
                color=color,
                three_texts=three_texts,
            )

        header = f"{one_range} {two_range}".rstrip()
        one_text, two_text = self._get_edit_aligned_texts(color=color)
        if three_texts is None:
            return f"{header}\n{one_text}\n{two_text}\n"
        three_text = join_text_lines(three_texts)
        return f"{header}\n{one_text}\n{two_text}\n{three_text}\n"

    def _get_edit_aligned_texts(self, *, color: bool) -> tuple[str, str]:
        """Character-align text for an edit-like diff.

        Arguments:
            color: whether to emit ANSI color escapes
        Returns:
            first- and second-side aligned text
        """
        one_text = join_text_lines(self.one_texts or ())
        two_text = join_text_lines(self.two_texts or ())
        alignment = LineAlignment(one_text, two_text).alignment_pairs

        one_out: list[str] = []
        two_out: list[str] = []
        for column in alignment:
            if column.operation == LineAlignmentOperation.MATCH:
                one_char = column.one or ""
                two_char = column.two or ""
                if color:
                    one_char = colorize(one_char, AnsiColor.GREEN)
                    two_char = colorize(two_char, AnsiColor.GREEN)
                one_out.append(one_char)
                two_out.append(two_char)
                continue

            if column.operation == LineAlignmentOperation.SUBSTITUTE:
                one_char = column.one or ""
                two_char = column.two or ""
                if color:
                    one_char = colorize(one_char, AnsiColor.PURPLE)
                    two_char = colorize(two_char, AnsiColor.PURPLE)
                one_out.append(one_char)
                two_out.append(two_char)
                continue

            if column.operation == LineAlignmentOperation.DELETE:
                assert column.one is not None
                one_char = column.one
                if color:
                    one_char = colorize(one_char, AnsiColor.RED)
                one_out.append(one_char)
                two_out.append(self._get_placeholder(column.one))
                continue

            assert column.two is not None
            one_out.append(self._get_placeholder(column.two))
            two_char = column.two
            if color:
                two_char = colorize(two_char, AnsiColor.BLUE)
            two_out.append(two_char)

        return "".join(one_out), "".join(two_out)

    @staticmethod
    def _format_idxs(idxs: tuple[int, ...]) -> str:
        """Format indices for display.

        Arguments:
            idxs: indices to format
        Returns:
            formatted index range
        """
        if len(idxs) == 1:
            return str(idxs[0] + 1)
        return f"{idxs[0] + 1}-{idxs[-1] + 1}"

    @staticmethod
    def _format_idxs_or_empty(idxs: tuple[int, ...] | None) -> str:
        """Format indices for display or return an empty string.

        Arguments:
            idxs: indices to format
        Returns:
            formatted index range or empty string
        """
        if not idxs:
            return ""
        return LineDiff._format_idxs(idxs)

    @staticmethod
    def _format_texts(texts: tuple[str, ...]) -> str:
        """Format text values for single-line or multi-line display.

        Arguments:
            texts: text lines to format
        Returns:
            representation of one text line or the whole text tuple
        """
        match texts:
            case (text,):
                return repr(text)
            case _:
                return repr(texts)

    @staticmethod
    def _get_delete_stacked_str(
        *,
        one_range: str,
        one_texts: tuple[str, ...],
        color: bool,
        three_texts: tuple[str, ...] | None,
    ) -> str:
        """Format a delete diff as stacked output.

        Arguments:
            one_range: formatted index range for the first side
            one_texts: deleted text lines
            color: whether to emit ANSI color escapes
            three_texts: optional unaligned third-side text lines
        Returns:
            formatted delete diff chunk
        """
        header = f"{one_range} |"
        one_text = join_text_lines(one_texts)
        if color:
            one_text = colorize(one_text, AnsiColor.RED)
        if three_texts is None:
            return f"{header}\n{one_text}\n\n"
        three_text = join_text_lines(three_texts)
        return f"{header}\n{one_text}\n\n{three_text}\n"

    @staticmethod
    def _get_equal_stacked_str(
        *,
        one_range: str,
        two_range: str,
        one_texts: tuple[str, ...],
        two_texts: tuple[str, ...],
        color: bool,
        three_texts: tuple[str, ...] | None,
    ) -> str:
        """Format an equal diff as stacked output.

        Arguments:
            one_range: formatted index range for the first side
            two_range: formatted index range for the second side
            one_texts: first-side text lines
            two_texts: second-side text lines
            color: whether to emit ANSI color escapes
            three_texts: optional unaligned third-side text lines
        Returns:
            formatted equal diff chunk
        """
        one_text = join_text_lines(one_texts)
        two_text = join_text_lines(two_texts)
        if color:
            one_text = colorize(one_text, AnsiColor.GREEN)
            two_text = colorize(two_text, AnsiColor.GREEN)
        header = f"{one_range} {two_range}".rstrip()
        if three_texts is None:
            return f"{header}\n{one_text}\n{two_text}\n"
        three_text = join_text_lines(three_texts)
        return f"{header}\n{one_text}\n{two_text}\n{three_text}\n"

    @staticmethod
    def _get_insert_stacked_str(
        *,
        insert_idxs: tuple[int, ...],
        insert_texts: tuple[str, ...],
        color: bool,
        three_texts: tuple[str, ...] | None,
    ) -> str:
        """Format an insert diff as stacked output.

        Arguments:
            insert_idxs: inserted line indices
            insert_texts: inserted text lines
            color: whether to emit ANSI color escapes
            three_texts: optional unaligned third-side text lines
        Returns:
            formatted insert diff chunk
        """
        header = f"| {LineDiff._format_idxs_or_empty(insert_idxs)}"
        two_text = join_text_lines(insert_texts)
        if color:
            two_text = colorize(two_text, AnsiColor.BLUE)
        if three_texts is None:
            return f"{header}\n\n{two_text}\n"
        three_text = join_text_lines(three_texts)
        return f"{header}\n\n{two_text}\n{three_text}\n"

    @staticmethod
    def _get_placeholder(char: str) -> str:
        """Get placeholder for a missing character.

        Arguments:
            char: present character whose width class determines placeholder
        Returns:
            ASCII or ideographic space placeholder
        """
        if is_full_width_char(char):
            return "\u3000"
        return " "
