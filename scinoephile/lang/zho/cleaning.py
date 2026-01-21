#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to 中文 text."""

from __future__ import annotations

import re
from copy import deepcopy

from scinoephile.core.subtitles import Series
from scinoephile.core.text import half_to_full_punc

__all__ = [
    "get_zho_cleaned",
]


def get_zho_cleaned(series: Series, remove_empty: bool = True) -> Series:
    """Get 中文 series cleaned.

    Arguments:
        series: Series to clean
        remove_empty: whether to remove subtitles with empty text
    Returns:
        Cleaned series
    """
    series = deepcopy(series)
    new_events = []
    for event in series:
        raw_text = (event.text or "").strip()
        text = _get_zho_text_cleaned(raw_text)
        if text or not remove_empty:
            event.text = text if text is not None else ""
            new_events.append(event)
    series.events = new_events
    return series


def _get_zho_text_cleaned(text: str) -> str | None:
    """Get 中文 text cleaned.

    Arguments:
        text: text to clean
    Returns:
        Cleaned text
    """
    line_sep = r"\N"
    cleaned = text.strip()

    cleaned_lines = []
    for raw_line in cleaned.split(line_sep):
        cleaned_line = raw_line.strip()

        # Replace '...' and '…' with '⋯'
        cleaned_line = re.sub(r"[^\S]*\.\.\.[^\S]*", "⋯", cleaned_line)
        cleaned_line = re.sub(r"[^\S]*…[^\S]*", "⋯", cleaned_line)

        # Replace half-width punctuation with full-width punctuation
        for old_punc, new_punc in half_to_full_punc.items():
            cleaned_line = re.sub(
                rf"[^\S]*{re.escape(old_punc)}[^\S]*", new_punc, cleaned_line
            )

        # Clean up double quotes
        cleaned_line = re.sub(r"[“”〞〝\"]", "＂", cleaned_line)
        cleaned_line = _replace_full_width_double_quotes(cleaned_line)

        # Remove whitespace before and after specified characters
        cleaned_line = re.sub(r"[^\S]*([、「」『』《》])[^\S]*", r"\1", cleaned_line)

        cleaned_lines.append(cleaned_line)

    return line_sep.join(cleaned_lines)


def _replace_full_width_double_quotes(text: str) -> str:
    """Replace straight double quotes (＂) with curly quotes (〝/〞).

    Arguments:
        text: text in which to replace quotes
    Returns:
        text with quotes replaced
    """
    count = text.count("＂")
    if count == 0 or count % 2 != 0:
        return text
    result: list[str] = []
    next_quote_should_be_an_open_quote = True

    for character in text:
        if character == "＂":
            if next_quote_should_be_an_open_quote:
                result.append("〝")
            else:
                result.append("〞")
            next_quote_should_be_an_open_quote = not next_quote_should_be_an_open_quote
        else:
            result.append(character)

    return "".join(result)
