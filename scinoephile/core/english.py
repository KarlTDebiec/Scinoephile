#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to English text."""
from __future__ import annotations

import re
from copy import deepcopy
from logging import info

import nltk

from scinoephile.core.series import Series


def get_english_cleaned(series: Series) -> Series:
    """Get English series cleaned.

    Arguments
        series: series to clean
    Returns:
        cleaned series
    """
    series = deepcopy(series)
    new_events = []
    for event in series.events:
        text = _get_english_text_cleaned(event.text.strip())
        if text:
            event.text = text
            new_events.append(event)
    series.events = new_events
    return series


def get_english_flattened(series: Series) -> Series:
    """Get multi-line English series flattened to single lines.

    Arguments:
        series: series to flatten
    Returns:
        flattened series
    """
    series = deepcopy(series)
    for event in series:
        event.text = _get_english_text_flattened(event.text.strip())
    return series


def get_english_truecased(series: Series) -> Series:
    """Get all-caps English series truecased.

    Arguments:
        series: series to truecase
    Returns:
        truecased series
    """
    series = deepcopy(series)
    for event in series:
        event.text = _get_english_text_truecased(event.text.strip())
    return series


def _get_english_text_cleaned(text: str) -> str | None:
    """Get English text cleaned.

    Arguments:
        text: text to clean
    Returns:
        cleaned text, or None if no text remains
    """
    # Revert strange substitution in pysubs2/subrip.py:66
    cleaned = re.sub(r"\\N", r"\n", text).strip()

    # Remove closed caption annotations ([...])
    cleaned = re.sub(r"\[.*?][^\S\n]*", "", cleaned, flags=re.DOTALL).strip()

    # Remove lines starting with dashes if they are otherwise empty
    cleaned = re.sub(r"^\s*-\s*$", "", cleaned, flags=re.M)

    # Remove leading dash if there is now only one line
    cleaned = re.sub(r"^\s*-\s*(.+)\s*$", lambda m: m.group(1).strip(), cleaned)

    # Remove empty lines
    cleaned = re.sub(r"\s*\n\s*", "\n", cleaned)

    # Remove whitespace around <i> and <\i>
    cleaned = re.sub(r"[^\S\n]*{\\i1}[^\S\n]*", r"{\\i1}", cleaned)
    cleaned = re.sub(r"[^\S\n]*{\\i0}[^\S\n]*", r"{\\i0}", cleaned)

    # Check if any substantive text remains
    if not cleaned:
        return None
    if re.fullmatch(r"^\s*-?\s*\n\s*-?\s*", cleaned):
        return None

    return cleaned


def _get_english_text_flattened(text: str) -> str:
    """Get multi-line English text flattened to a single line.

    Accounts for dashes ('-') used for dialogue from multiple sources.

    Arguments:
        text: text to flatten
    Returns:
        flattened text
    """
    # Revert strange substitution in pysubs2/subrip.py:66
    flattened = re.sub(r"\\N", r"\n", text)

    # Merge conversations
    flattened = re.sub(
        r"^\s*-\s*(.+)\n-\s*(.+)\s*$",
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


def _get_english_text_truecased(text: str) -> str:
    """Get all-caps English text truecased.

    Arguments:
        text: text for which to get truecase
    Returns:
        truecased text
    """

    try:
        tagged = nltk.pos_tag([word.lower() for word in nltk.word_tokenize(text)])
    except LookupError:
        info("Downloading NLTK data")
        nltk.download("punkt")
        tagged = nltk.pos_tag([word.lower() for word in nltk.word_tokenize(text)])

    normalized = [w.capitalize() if t in ["NN", "NNS"] else w for (w, t) in tagged]
    normalized[0] = normalized[0].capitalize()

    truecased = re.sub(r" (?=[.,'!?:;])", "", " ".join(normalized))
    truecased = truecased.replace(" n't", "n't")
    truecased = truecased.replace(" i ", " I ")
    truecased = truecased.replace("``", '"')
    truecased = truecased.replace("''", '"')
    truecased = re.sub(
        r"(\A\w)|(?<!\.\w)([.?!] )\w|\w(?:\.\w)|(?<=\w\.)\w",
        lambda s: s.group().upper(),
        truecased,
    )

    return truecased


__all__ = [
    "get_english_cleaned",
    "get_english_flattened",
    "get_english_truecased",
]
