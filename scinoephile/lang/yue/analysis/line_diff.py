#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Line-level diff records for written Cantonese subtitles."""

from __future__ import annotations

from scinoephile.analysis.diff import LineDiff, LineDiffKind
from scinoephile.analysis.line_alignment import (
    LineAlignment,
    LineAlignmentOperation,
    LineAlignmentPair,
)
from scinoephile.core.text import AnsiColor, colorize

from .character_equivalence import (
    are_yue_diff_display_chars_equal,
    is_yue_diff_display_ignorable_char,
)

__all__ = ["YueLineDiff"]

_YUE_IGNORED_DIFF_COLOR = "\x1b[33m"


class YueLineDiff(LineDiff):
    """Line-level diff record with Yue-aware stacked rendering."""

    def get_stacked_str(
        self,
        *,
        color: bool = True,
        three_texts: tuple[str, ...] | None = None,
    ) -> str:
        """Format the diff as a Yue-aware stacked display.

        Arguments:
            color: whether to emit ANSI color escapes
            three_texts: optional unaligned third-side text lines
        Returns:
            formatted, multi-line diff chunk
        """
        if self.kind in {LineDiffKind.DELETE, LineDiffKind.INSERT}:
            return super().get_stacked_str(color=color, three_texts=three_texts)

        return self._get_yue_edit_stacked_str(
            one_range=self._format_idxs_or_empty(self.one_idxs),
            two_range=self._format_idxs_or_empty(self.two_idxs),
            one_texts=self.one_texts or (),
            two_texts=self.two_texts or (),
            color=color,
            three_texts=three_texts,
        )

    @classmethod
    def from_line_diff(cls, line_diff: LineDiff) -> YueLineDiff:
        """Create a Yue line diff from a generic line diff.

        Arguments:
            line_diff: generic line diff to convert
        Returns:
            Yue line diff with the same fields
        """
        return cls(
            kind=line_diff.kind,
            one_lbl=line_diff.one_lbl,
            two_lbl=line_diff.two_lbl,
            one_idxs=line_diff.one_idxs,
            two_idxs=line_diff.two_idxs,
            one_texts=line_diff.one_texts,
            two_texts=line_diff.two_texts,
        )

    @staticmethod
    def _colorize_ignored_diff(text: str) -> str:
        """Colorize a visible but ignored diff.

        Arguments:
            text: input text
        Returns:
            colorized text
        """
        return f"{_YUE_IGNORED_DIFF_COLOR}{text}{AnsiColor.RESET.value}"

    @staticmethod
    def _get_yue_delete_chars(
        column: LineAlignmentPair,
        *,
        one_text: str,
        one_pos: int,
        color: bool,
    ) -> tuple[str, str]:
        """Get output characters for a deleted alignment column.

        Arguments:
            column: alignment column to render
            one_text: first text containing the deleted character
            one_pos: first-side character position
            color: whether to emit ANSI color escapes
        Returns:
            first- and second-side output characters
        """
        assert column.one is not None
        one_char = column.one
        if color:
            if is_yue_diff_display_ignorable_char(
                column.one,
                text=one_text,
                char_pos=one_pos,
            ):
                one_char = YueLineDiff._colorize_ignored_diff(one_char)
            else:
                one_char = colorize(one_char, AnsiColor.RED)
        return one_char, LineDiff._get_placeholder(column.one)

    @staticmethod
    def _get_yue_edit_stacked_str(
        *,
        one_range: str,
        two_range: str,
        one_texts: tuple[str, ...],
        two_texts: tuple[str, ...],
        color: bool,
        three_texts: tuple[str, ...] | None,
    ) -> str:
        """Format an edit-like diff as stacked Yue-aware output.

        Arguments:
            one_range: formatted index range for the first side
            two_range: formatted index range for the second side
            one_texts: first-side text lines
            two_texts: second-side text lines
            color: whether to emit ANSI color escapes
            three_texts: optional unaligned third-side text lines
        Returns:
            formatted edit diff chunk
        """
        one_text = LineDiff._join_texts(one_texts)
        two_text = LineDiff._join_texts(two_texts)
        header = f"{one_range} {two_range}".rstrip()
        alignment = LineAlignment(one_text, two_text).alignment_pairs

        one_out: list[str] = []
        two_out: list[str] = []
        one_pos = 0
        two_pos = 0
        for column in alignment:
            if column.operation == LineAlignmentOperation.MATCH:
                one_char, two_char = YueLineDiff._get_yue_match_chars(
                    column,
                    color=color,
                )
            elif column.operation == LineAlignmentOperation.SUBSTITUTE:
                one_char, two_char = YueLineDiff._get_yue_substitute_chars(
                    column,
                    one_text=one_text,
                    two_text=two_text,
                    one_pos=one_pos,
                    two_pos=two_pos,
                    color=color,
                )
            elif column.operation == LineAlignmentOperation.DELETE:
                one_char, two_char = YueLineDiff._get_yue_delete_chars(
                    column,
                    one_text=one_text,
                    one_pos=one_pos,
                    color=color,
                )
            else:
                one_char, two_char = YueLineDiff._get_yue_insert_chars(
                    column,
                    two_text=two_text,
                    two_pos=two_pos,
                    color=color,
                )
            one_out.append(one_char)
            two_out.append(two_char)

            if column.one is not None:
                one_pos += 1
            if column.two is not None:
                two_pos += 1

        if three_texts is None:
            return f"{header}\n{''.join(one_out)}\n{''.join(two_out)}\n"
        three_text = LineDiff._join_texts(three_texts)
        return f"{header}\n{''.join(one_out)}\n{''.join(two_out)}\n{three_text}\n"

    @staticmethod
    def _get_yue_insert_chars(
        column: LineAlignmentPair,
        *,
        two_text: str,
        two_pos: int,
        color: bool,
    ) -> tuple[str, str]:
        """Get output characters for an inserted alignment column.

        Arguments:
            column: alignment column to render
            two_text: second text containing the inserted character
            two_pos: second-side character position
            color: whether to emit ANSI color escapes
        Returns:
            first- and second-side output characters
        """
        assert column.two is not None
        two_char = column.two
        if color:
            if is_yue_diff_display_ignorable_char(
                column.two,
                text=two_text,
                char_pos=two_pos,
            ):
                two_char = YueLineDiff._colorize_ignored_diff(two_char)
            else:
                two_char = colorize(two_char, AnsiColor.BLUE)
        return LineDiff._get_placeholder(column.two), two_char

    @staticmethod
    def _get_yue_match_chars(
        column: LineAlignmentPair,
        *,
        color: bool,
    ) -> tuple[str, str]:
        """Get output characters for a matched alignment column.

        Arguments:
            column: alignment column to render
            color: whether to emit ANSI color escapes
        Returns:
            first- and second-side output characters
        """
        one_char = column.one or ""
        two_char = column.two or ""
        if color:
            one_char = colorize(one_char, AnsiColor.GREEN)
            two_char = colorize(two_char, AnsiColor.GREEN)
        return one_char, two_char

    @staticmethod
    def _get_yue_substitute_chars(
        column: LineAlignmentPair,
        *,
        one_text: str,
        two_text: str,
        one_pos: int,
        two_pos: int,
        color: bool,
    ) -> tuple[str, str]:
        """Get output characters for a substituted alignment column.

        Arguments:
            column: alignment column to render
            one_text: first text containing the substituted character
            two_text: second text containing the substituted character
            one_pos: first-side character position
            two_pos: second-side character position
            color: whether to emit ANSI color escapes
        Returns:
            first- and second-side output characters
        """
        one_char = column.one or ""
        two_char = column.two or ""
        if not color:
            return one_char, two_char

        assert column.one is not None
        assert column.two is not None
        if are_yue_diff_display_chars_equal(
            column.one,
            column.two,
            one_text=one_text,
            two_text=two_text,
            one_pos=one_pos,
            two_pos=two_pos,
        ):
            return (
                YueLineDiff._colorize_ignored_diff(one_char),
                YueLineDiff._colorize_ignored_diff(two_char),
            )
        return (
            colorize(one_char, AnsiColor.PURPLE),
            colorize(two_char, AnsiColor.PURPLE),
        )
