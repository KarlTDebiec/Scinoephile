#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Line-level diff records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from scinoephile.analysis.line_alignment import LineAlignment, LineAlignmentOperation
from scinoephile.core.text import full_punc_chars, get_char_type

from .line_diff_kind import LineDiffKind

__all__ = ["LineDiff"]


class _Ansi(Enum):
    """ANSI escape codes used by stacked diff rendering."""

    RESET = "\x1b[0m"
    GREEN = "\x1b[32m"
    RED = "\x1b[31m"
    BLUE = "\x1b[34m"
    PURPLE = "\x1b[35m"


def _colorize(text: str, color: _Ansi, *, color_enabled: bool) -> str:
    """Colorize text with an ANSI escape.

    Arguments:
        text: input text
        color: ANSI color escape
        color_enabled: whether to emit ANSI escapes
    Returns:
        colorized or raw text
    """
    if not color_enabled:
        return text
    return f"{color.value}{text}{_Ansi.RESET.value}"


def _is_full_width_char(char: str) -> bool:
    """Return whether a character should occupy a full-width column.

    Arguments:
        char: character to classify
    Returns:
        whether the character should use full-width spacing
    """
    return char in full_punc_chars or get_char_type(char) == "full"


def _placeholder_for(char: str) -> str:
    """Return placeholder for a missing character.

    Arguments:
        char: present character whose width class determines placeholder
    Returns:
        ASCII or ideographic space placeholder
    """
    return "\u3000" if _is_full_width_char(char) else " "


def _choose_joiner(prev_char: str | None, next_char: str | None) -> str:
    """Choose a joiner for concatenating lines.

    Arguments:
        prev_char: trailing character of previous chunk
        next_char: leading character of next chunk
    Returns:
        ASCII or ideographic space joiner
    """
    if prev_char is not None and _is_full_width_char(prev_char):
        return "\u3000"
    if next_char is not None and _is_full_width_char(next_char):
        return "\u3000"
    return " "


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
        previous_char = previous_text[-1] if previous_text else None
        next_char = next_text[0] if next_text else None
        chunks.append(_choose_joiner(previous_char, next_char))
        chunks.append(next_text)
    return "".join(chunks)


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

        Arguments:
            None.
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
        one_text_repr = repr(one_texts) if use_list_repr else repr(one_texts[0])
        two_text_repr = repr(two_texts) if use_list_repr else repr(two_texts[0])
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
            header = f"{one_range} |"
            one_text = _join_texts(self.one_texts or [])
            colored_one = _colorize(one_text, _Ansi.RED, color_enabled=color)
            return f"{header}\n{colored_one}\n\n"

        if self.kind == LineDiffKind.INSERT:
            insert_idxs, insert_texts = self._get_insert_side()
            header = f"| {self._format_idxs_or_empty(insert_idxs)}"
            two_text = _join_texts(insert_texts)
            colored_two = _colorize(two_text, _Ansi.BLUE, color_enabled=color)
            return f"{header}\n\n{colored_two}\n"

        one_text = _join_texts(self.one_texts or [])
        two_text = _join_texts(self.two_texts or [])
        header = f"{one_range} {two_range}".rstrip()
        alignment = LineAlignment(one_text, two_text).alignment_pairs

        one_out: list[str] = []
        two_out: list[str] = []
        for column in alignment:
            if column.operation == LineAlignmentOperation.MATCH:
                one_out.append(
                    _colorize(column.one or "", _Ansi.GREEN, color_enabled=color)
                )
                two_out.append(
                    _colorize(column.two or "", _Ansi.GREEN, color_enabled=color)
                )
                continue

            if column.operation == LineAlignmentOperation.SUBSTITUTE:
                one_out.append(
                    _colorize(column.one or "", _Ansi.PURPLE, color_enabled=color)
                )
                two_out.append(
                    _colorize(column.two or "", _Ansi.PURPLE, color_enabled=color)
                )
                continue

            if column.operation == LineAlignmentOperation.DELETE:
                assert column.one is not None
                one_out.append(_colorize(column.one, _Ansi.RED, color_enabled=color))
                two_out.append(_placeholder_for(column.one))
                continue

            assert column.two is not None
            one_out.append(_placeholder_for(column.two))
            two_out.append(_colorize(column.two, _Ansi.BLUE, color_enabled=color))

        return f"{header}\n{''.join(one_out)}\n{''.join(two_out)}\n"

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

    @classmethod
    def _format_idxs_or_empty(cls, idxs: list[int] | None) -> str:
        """Format indices for display or return an empty string.

        Arguments:
            idxs: indices to format
        Returns:
            formatted index range or empty string
        """
        if not idxs:
            return ""
        return cls._format_idxs(idxs)

    def _get_insert_side(self) -> tuple[list[int], list[str]]:
        """Return the inserted indices and texts for an insert diff.

        Arguments:
            None.
        Returns:
            inserted indices and texts
        """
        if self.two_idxs or self.two_texts:
            return self.two_idxs or [], self.two_texts or []
        return self.one_idxs or [], self.one_texts or []
