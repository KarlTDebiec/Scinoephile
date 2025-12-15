#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to English text."""

from __future__ import annotations

import re
from copy import deepcopy
from logging import info

from scinoephile.core.series import Series

from .prompt import EngPrompt

__all__ = [
    "EngPrompt",
    "get_eng_cleaned",
    "get_eng_flattened",
]


def get_eng_cleaned(series: Series, remove_empty: bool = True) -> Series:
    """Get English series cleaned.

    Arguments:
        series: Series to clean
        remove_empty: whether to remove subtitles with empty text
    Returns:
        cleaned Series
    """
    series = deepcopy(series)
    new_events = []
    for event in series:
        text = _get_english_text_cleaned(event.text.strip())
        if text or not remove_empty:
            event.text = text
            new_events.append(event)
    series.events = new_events
    return series


def get_eng_flattened(series: Series, exclusions: list[int] = None) -> Series:
    """Get multi-line English series flattened to single lines.

    Arguments:
        series: Series to flatten
        exclusions: list of subtitle indexes to exclude from flattening
    Returns:
        flattened Series
    """
    if not exclusions:
        exclusions = []
    series = deepcopy(series)
    for i, event in enumerate(series, 1):
        if i in exclusions:
            info(f"Skipping flattening of subtitle {i}, with text:\n{event.text}")
            continue
        event.text = _get_eng_text_flattened(event.text.strip())
    return series


def _get_english_text_cleaned(text: str) -> str | None:
    """Get English text cleaned.

    Arguments:
        text: Text to clean
    Returns:
        Cleaned text, or None if no text remains
    """
    # Revert strange substitution in pysubs2/subrip.py:66
    cleaned = re.sub(r"\\N", r"\n", text).strip()

    # Remove ASS hard-space \h
    cleaned = re.sub(r"\\h", "", cleaned)

    # Remove closed caption annotations ([...])
    cleaned = re.sub(r"\[.*?][^\S\n]*", "", cleaned, flags=re.DOTALL).strip()

    # Replace '...' with '…'
    cleaned = re.sub(r"\.\.\.", "…", cleaned)

    cleaned = _replace_half_width_double_quotes(cleaned)

    # Remove lines starting with dashes if they are otherwise empty
    cleaned = re.sub(r"^\s*-\s*$", "", cleaned, flags=re.M)

    # Remove leading dash if there is now only one line
    cleaned = re.sub(
        r"^(?!.*\s{4}-\s).?\s*-\s*(.+)\s*$", lambda m: m.group(1).strip(), cleaned
    )

    # Remove empty lines
    cleaned = re.sub(r"\s*\n\s*", "\n", cleaned)

    # Remove whitespace around <i> and <\i>
    cleaned = re.sub(r"[^\S\n]*{\\i1}[^\S\n]*", r"{\\i1}", cleaned)
    cleaned = re.sub(r"[^\S\n]*{\\i0}[^\S\n]*", r"{\\i0}", cleaned)

    # Collapse adjacent <\i><i>
    cleaned = re.sub(r"\{\\i0\}[ \t]*\{\\i1\}", "", cleaned)

    # Check if any substantive text remains
    if not cleaned:
        return None
    if re.fullmatch(r"^\s*-?\s*\n\s*-?\s*", cleaned):
        return None

    return cleaned


def _get_eng_text_flattened(text: str) -> str:
    """Get multi-line English text flattened to a single line.

    Accounts for dashes ('-') used for dialogue from multiple sources.

    Arguments:
        text: Text to flatten
    Returns:
        Flattened text
    """
    # Revert strange substitution in pysubs2/subrip.py:66
    flattened = re.sub(r"\\N", r"\n", text)

    # Merge conversations
    flattened = re.sub(
        r"^\s*[–-]\s*(.+)\n[–-]\s*(.+)\s*$",
        lambda m: f"- {m.group(1).strip()}    - {m.group(2).strip()}",
        flattened,
        flags=re.M,
    )

    # Merge italics
    flattened = re.sub(
        r"{\\i0}[^\S\n]*\n[^\S\n]*{\\i1}[^\S\n]*",
        " ",
        flattened,
    )

    # Merge lines
    flattened = re.sub(
        r"\s*(.+)\s*\n\s*(.+)\s*",
        lambda m: f"{m.group(1).strip()} {m.group(2).strip()}",
        flattened,
        flags=re.M,
    )
    return flattened


def _replace_half_width_double_quotes(text: str) -> str:
    """Replace straight double quotes (") with curly quotes (“/”).

    Arguments:
        text: text in which to replace quotes
    Returns:
        text with quotes replaced
    """
    count = text.count('"')
    if count == 0 or count % 2 != 0:
        return text
    result: list[str] = []
    next_quote_should_be_an_open_quote = True

    for character in text:
        if character == '"':
            if next_quote_should_be_an_open_quote:
                result.append("“")
            else:
                result.append("”")
            next_quote_should_be_an_open_quote = not next_quote_should_be_an_open_quote
        else:
            result.append(character)

    return "".join(result)
