#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Line-level diff records."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.analysis.line_alignment import LineAlignment, LineAlignmentOperation
from scinoephile.core.text import AnsiColor, colorize, is_full_width_char

from .line_diff_kind import LineDiffKind

__all__ = ["LineDiff"]


@dataclass(frozen=True)
class LineDiff:
    """Represents a line-level difference."""

    kind: LineDiffKind
    one_lbl: str | None = None
    two_lbl: str | None = None
    one_idxs: list[int] | None = None
    two_idxs: list[int] | None = None
    one_texts: list[str] | None = None
    two_texts: list[str] | None = None

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
        one_idxs = self.one_idxs or []
        two_idxs = self.two_idxs or []
        one_texts = self.one_texts or []
        two_texts = self.two_texts or []
        use_list_repr = len(one_idxs) != 1 or len(two_idxs) != 1
        if use_list_repr:
            one_text_repr = repr(one_texts)
            two_text_repr = repr(two_texts)
        else:
            one_text_repr = repr(one_texts[0])
            two_text_repr = repr(two_texts[0])
        return (
            f"{self.kind.value}: "
            f"{self.one_lbl}[{self._format_idxs(one_idxs)}] -> "
            f"{self.two_lbl}[{self._format_idxs(two_idxs)}]: "
            f"{one_text_repr} -> {two_text_repr}"
        )

    def get_stacked_str(self, *, color: bool = True) -> str:
        """Format the diff as a stacked, character-aligned display.

        Arguments:
            color: whether to emit ANSI color escapes
        Returns:
            formatted, multi-line diff chunk
        """
        one_range = self._format_idxs_or_empty(self.one_idxs)
        two_range = self._format_idxs_or_empty(self.two_idxs)

        if self.kind == LineDiffKind.DELETE:
            return self._get_delete_stacked_str(
                one_range=one_range,
                one_texts=self.one_texts or [],
                color=color,
            )

        if self.kind == LineDiffKind.INSERT:
            insert_idxs, insert_texts = self._get_insert_side()
            return self._get_insert_stacked_str(
                insert_idxs=insert_idxs,
                insert_texts=insert_texts,
                color=color,
            )

        return self._get_edit_stacked_str(
            one_range=one_range,
            two_range=two_range,
            one_texts=self.one_texts or [],
            two_texts=self.two_texts or [],
            color=color,
        )

    def _get_insert_side(self) -> tuple[list[int], list[str]]:
        """Return the inserted indices and texts for an insert diff.

        Returns:
            inserted indices and texts
        """
        if self.two_idxs or self.two_texts:
            return self.two_idxs or [], self.two_texts or []
        return self.one_idxs or [], self.one_texts or []

    @staticmethod
    def _format_idxs(idxs: list[int]) -> str:
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
    def _format_idxs_or_empty(idxs: list[int] | None) -> str:
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
    def _get_delete_stacked_str(
        *, one_range: str, one_texts: list[str], color: bool
    ) -> str:
        """Format a delete diff as stacked output.

        Arguments:
            one_range: formatted index range for the first side
            one_texts: deleted text lines
            color: whether to emit ANSI color escapes
        Returns:
            formatted delete diff chunk
        """
        header = f"{one_range} |"
        one_text = LineDiff._join_texts(one_texts)
        if color:
            one_text = colorize(one_text, AnsiColor.RED)
        return f"{header}\n{one_text}\n\n"

    @staticmethod
    def _get_edit_stacked_str(
        *,
        one_range: str,
        two_range: str,
        one_texts: list[str],
        two_texts: list[str],
        color: bool,
    ) -> str:
        """Format an edit-like diff as stacked output.

        Arguments:
            one_range: formatted index range for the first side
            two_range: formatted index range for the second side
            one_texts: first-side text lines
            two_texts: second-side text lines
            color: whether to emit ANSI color escapes
        Returns:
            formatted edit diff chunk
        """
        one_text = LineDiff._join_texts(one_texts)
        two_text = LineDiff._join_texts(two_texts)
        header = f"{one_range} {two_range}".rstrip()
        alignment = LineAlignment(one_text, two_text).alignment_pairs

        one_out: list[str] = []
        two_out: list[str] = []
        for column in alignment:
            if column.operation == LineAlignmentOperation.MATCH:
                one_text = column.one or ""
                two_text = column.two or ""
                if color:
                    one_text = colorize(one_text, AnsiColor.GREEN)
                    two_text = colorize(two_text, AnsiColor.GREEN)
                one_out.append(one_text)
                two_out.append(two_text)
                continue

            if column.operation == LineAlignmentOperation.SUBSTITUTE:
                one_text = column.one or ""
                two_text = column.two or ""
                if color:
                    one_text = colorize(one_text, AnsiColor.PURPLE)
                    two_text = colorize(two_text, AnsiColor.PURPLE)
                one_out.append(one_text)
                two_out.append(two_text)
                continue

            if column.operation == LineAlignmentOperation.DELETE:
                assert column.one is not None
                one_text = column.one
                if color:
                    one_text = colorize(one_text, AnsiColor.RED)
                one_out.append(one_text)
                two_out.append(LineDiff._get_placeholder(column.one))
                continue

            assert column.two is not None
            one_out.append(LineDiff._get_placeholder(column.two))
            two_text = column.two
            if color:
                two_text = colorize(two_text, AnsiColor.BLUE)
            two_out.append(two_text)

        return f"{header}\n{''.join(one_out)}\n{''.join(two_out)}\n"

    @staticmethod
    def _get_insert_stacked_str(
        *, insert_idxs: list[int], insert_texts: list[str], color: bool
    ) -> str:
        """Format an insert diff as stacked output.

        Arguments:
            insert_idxs: inserted line indices
            insert_texts: inserted text lines
            color: whether to emit ANSI color escapes
        Returns:
            formatted insert diff chunk
        """
        header = f"| {LineDiff._format_idxs_or_empty(insert_idxs)}"
        two_text = LineDiff._join_texts(insert_texts)
        if color:
            two_text = colorize(two_text, AnsiColor.BLUE)
        return f"{header}\n\n{two_text}\n"

    @staticmethod
    def _get_joiner(prev_char: str | None, next_char: str | None) -> str:
        """Get joiner for concatenating lines.

        Arguments:
            prev_char: trailing character of previous chunk
            next_char: leading character of next chunk
        Returns:
            ASCII or ideographic space joiner
        """
        if prev_char is not None and is_full_width_char(prev_char):
            return "\u3000"
        if next_char is not None and is_full_width_char(next_char):
            return "\u3000"
        return " "

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

    @staticmethod
    def _join_texts(texts: list[str]) -> str:
        """Join a list of subtitle lines into a single string.

        Arguments:
            texts: text lines to join
        Returns:
            joined text
        """
        if not texts:
            return ""
        if len(texts) == 1:
            return texts[0]
        chunks: list[str] = [texts[0]]
        for next_text in texts[1:]:
            previous_text = chunks[-1]
            previous_char = None
            if previous_text:
                previous_char = previous_text[-1]
            next_char = None
            if next_text:
                next_char = next_text[0]
            chunks.append(LineDiff._get_joiner(previous_char, next_char))
            chunks.append(next_text)
        return "".join(chunks)
