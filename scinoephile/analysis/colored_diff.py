#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Color-coded, character-level diff rendering for series diffs."""

from __future__ import annotations

from enum import Enum

from scinoephile.core.text import full_punc_chars, get_char_type

from .alignment import AlignmentOp, AlignmentPolicy, align_chars
from .line_diff import LineDiff
from .line_diff_kind import LineDiffKind
from .series_diff import SeriesDiff

__all__ = [
    "format_colored_line_diff",
    "format_colored_series_diff",
]


class _Ansi(Enum):
    """ANSI escape codes used by the colored diff renderer."""

    RESET = "\x1b[0m"
    GREEN = "\x1b[32m"
    RED = "\x1b[31m"
    BLUE = "\x1b[34m"
    PURPLE = "\x1b[35m"


def _colorize(text: str, color: _Ansi, *, use_color: bool) -> str:
    """Colorize text with an ANSI escape.

    Arguments:
        text: input text
        color: ANSI color escape
        use_color: whether to emit ANSI escapes
    Returns:
        colorized or raw text
    """
    if not use_color:
        return text
    return f"{color.value}{text}{_Ansi.RESET.value}"


def _placeholder_for(char: str) -> str:
    """Return placeholder for a missing character.

    Arguments:
        char: present character whose width class determines placeholder
    Returns:
        ASCII or ideographic space placeholder
    """
    # get_char_type returns "full", "half", or "punc"
    return "\u3000" if _is_full_width_char(char) else " "


def _is_full_width_char(char: str) -> bool:
    """Return whether a character should occupy a full-width column.

    Arguments:
        char: character to classify
    Returns:
        whether the character should use full-width spacing
    """
    return char in full_punc_chars or get_char_type(char) == "full"


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
    for nxt in texts[1:]:
        prev = chunks[-1]
        prev_char = prev[-1] if prev else None
        next_char = nxt[0] if nxt else None
        chunks.append(_choose_joiner(prev_char, next_char))
        chunks.append(nxt)
    return "".join(chunks)


def _format_range(idxs: list[int] | None) -> str:
    """Format a 0-based index list as a 1-based range string.

    Arguments:
        idxs: indices to format
    Returns:
        formatted index/range string
    """
    if not idxs:
        return ""
    if len(idxs) == 1:
        return str(idxs[0] + 1)
    return f"{idxs[0] + 1}-{idxs[-1] + 1}"


def _get_insert_side(message: LineDiff) -> tuple[list[int], list[str]]:
    """Return the inserted indices and texts for an insert diff.

    Arguments:
        message: line-level diff message
    Returns:
        inserted indices and texts
    """
    if message.two_idxs or message.two_texts:
        return message.two_idxs or [], message.two_texts or []
    return message.one_idxs or [], message.one_texts or []


def format_colored_line_diff(message: LineDiff, *, use_color: bool = True) -> str:
    """Format a `LineDiff` as a colored, character-aligned diff.

    Arguments:
        message: line-level diff message
        use_color: whether to output ANSI color escapes
    Returns:
        formatted, multi-line diff chunk
    """
    one_range = _format_range(message.one_idxs)
    two_range = _format_range(message.two_idxs)

    if message.kind == LineDiffKind.DELETE:
        header = f"{one_range} |"
        one_text = _join_texts(message.one_texts or [])
        two_text = ""
        colored_one = _colorize(one_text, _Ansi.RED, use_color=use_color)
        return f"{header}\n{colored_one}\n{two_text}\n"

    if message.kind == LineDiffKind.INSERT:
        insert_idxs, insert_texts = _get_insert_side(message)
        header = f"| {_format_range(insert_idxs)}"
        one_text = ""
        two_text = _join_texts(insert_texts)
        colored_two = _colorize(two_text, _Ansi.BLUE, use_color=use_color)
        return f"{header}\n{one_text}\n{colored_two}\n"

    one_text = _join_texts(message.one_texts or [])
    two_text = _join_texts(message.two_texts or [])
    header = f"{one_range} {two_range}".rstrip()

    alignment = align_chars(one_text, two_text, policy=AlignmentPolicy.HUMAN)

    one_out: list[str] = []
    two_out: list[str] = []
    for col in alignment:
        if col.op == AlignmentOp.MATCH:
            one_out.append(_colorize(col.one or "", _Ansi.GREEN, use_color=use_color))
            two_out.append(_colorize(col.two or "", _Ansi.GREEN, use_color=use_color))
            continue

        if col.op == AlignmentOp.SUBSTITUTE:
            one_out.append(_colorize(col.one or "", _Ansi.PURPLE, use_color=use_color))
            two_out.append(_colorize(col.two or "", _Ansi.PURPLE, use_color=use_color))
            continue

        if col.op == AlignmentOp.DELETE:
            assert col.one is not None
            one_out.append(_colorize(col.one, _Ansi.RED, use_color=use_color))
            two_out.append(_placeholder_for(col.one))
            continue

        assert col.two is not None
        one_out.append(_placeholder_for(col.two))
        two_out.append(_colorize(col.two, _Ansi.BLUE, use_color=use_color))

    return f"{header}\n{''.join(one_out)}\n{''.join(two_out)}\n"


def format_colored_series_diff(diff: SeriesDiff, *, use_color: bool = True) -> str:
    """Format a `SeriesDiff` as a colored, character-aligned diff.

    Arguments:
        diff: series diff
        use_color: whether to output ANSI color escapes
    Returns:
        formatted multi-line diff string
    """
    return "\n".join(format_colored_line_diff(m, use_color=use_color) for m in diff)
