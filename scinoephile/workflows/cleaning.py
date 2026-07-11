#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for cleaning subtitles."""

from __future__ import annotations

import re
from copy import deepcopy

from scinoephile.core import Language
from scinoephile.core.subtitles import Series
from scinoephile.core.text import HALF_TO_FULL_PUNC, normalize_text

from .helpers import resolve_language

__all__ = ["clean_series"]


def clean_series(
    series: Series,
    *,
    language: Language | None = None,
    remove_empty: bool = True,
) -> Series:
    """Clean a subtitle series.

    Arguments:
        series: subtitle series to clean
        language: explicit language, or None to detect it
        remove_empty: whether to remove subtitles with empty text
    Returns:
        cleaned subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved
    """
    resolved_language = resolve_language(series, language)
    if resolved_language is Language.eng:
        clean_text = _get_eng_text_cleaned
    else:
        clean_text = _get_zho_text_cleaned

    cleaned = deepcopy(series)
    cleaned_events = []
    for event in cleaned:
        text = clean_text((event.text or "").strip())
        if text or not remove_empty:
            event.text = text if text is not None else ""
            cleaned_events.append(event)
    cleaned.events = cleaned_events
    return cleaned


def _get_eng_text_cleaned(text: str) -> str | None:
    """Get English text cleaned.

    Arguments:
        text: text to clean
    Returns:
        cleaned text, or None if no text remains
    """
    line_sep = "\\N"
    cleaned = normalize_text(text)

    # Remove ASS hard-space \h
    cleaned = re.sub(r"\\h", "", cleaned)

    # Remove extraction markup from EIA-608 captions
    cleaned = re.sub(r"</?font\b[^>]*>", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\{\\an\d+\}", "", cleaned)

    # Remove closed caption annotations ([...])
    cleaned = re.sub(r"\[.*?][^\S\n]*", "", cleaned, flags=re.DOTALL).strip()

    # Replace '...' with '…'
    cleaned = re.sub(r"\.\.\.", "…", cleaned)

    # Clean up double quotes
    cleaned = re.sub(r"[“”＂〞〝]", '"', cleaned)
    cleaned = _replace_half_width_double_quotes(cleaned)

    # Remove lines starting with dashes if they are otherwise empty
    lines = [line.strip() for line in cleaned.split(line_sep)]
    lines = [line for line in lines if not re.fullmatch(r"\s*-\s*", line)]

    # Remove empty lines
    lines = [line for line in lines if line.strip()]
    cleaned = line_sep.join(lines)

    # Replace brackets to avoid problems saving and reloading
    cleaned = cleaned.replace("<", "〈").replace(">", "〉")

    # Remove whitespace around <i> and <\i>
    cleaned = re.sub(r"[^\S]*{\\i1}[^\S]*", r"{\\i1}", cleaned)
    cleaned = re.sub(r"[^\S]*{\\i0}[^\S]*", r"{\\i0}", cleaned)

    # Collapse adjacent <\i><i>
    cleaned = re.sub(r"\{\\i0\}[ \t]*\{\\i1\}", "", cleaned)

    # Check if any substantive text remains
    if not cleaned:
        return None
    if cleaned and all(
        re.fullmatch(r"\s*-?\s*", line) for line in cleaned.split(line_sep)
    ):
        return None

    return cleaned


def _get_zho_text_cleaned(text: str) -> str | None:
    """Get Chinese text cleaned.

    Arguments:
        text: text to clean
    Returns:
        cleaned text
    """
    line_sep = r"\N"
    cleaned = normalize_text(text)

    # Remove extraction markup before punctuation normalization
    cleaned = re.sub(r"</?font\b[^>]*>", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\{\\an\d+\}", "", cleaned)

    cleaned_lines = []
    for raw_line in cleaned.split(line_sep):
        cleaned_line = raw_line.strip()

        # Replace '...' and '…' with '⋯'
        cleaned_line = re.sub(r"[^\S]*\.\.\.[^\S]*", "⋯", cleaned_line)
        cleaned_line = re.sub(r"[^\S]*…[^\S]*", "⋯", cleaned_line)

        # Normalize ambiguous Middle Dot to wide Katakana Middle Dot
        cleaned_line = re.sub(r"[^\S]*·[^\S]*", "・", cleaned_line)

        # Replace half-width punctuation with full-width punctuation
        for old_punc, new_punc in HALF_TO_FULL_PUNC.items():
            cleaned_line = re.sub(
                rf"[^\S]*{re.escape(old_punc)}[^\S]*", new_punc, cleaned_line
            )

        # Clean up double quotes
        cleaned_line = re.sub(r'[“”〞〝"]', "＂", cleaned_line)
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
