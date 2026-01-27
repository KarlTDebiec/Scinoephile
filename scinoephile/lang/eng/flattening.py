#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to English text."""

from __future__ import annotations

import re
from collections.abc import Iterable
from copy import deepcopy
from logging import info

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series

__all__ = [
    "get_eng_flattened",
]


def get_eng_flattened(
    series: Series, exclusions: Iterable[int] | None = None
) -> Series:
    """Get multi-line English series flattened to single lines.

    Arguments:
        series: Series to flatten
        exclusions: list of subtitle indexes to exclude from flattening
    Returns:
        flattened Series
    """
    exclusion_set = set(exclusions or [])
    if any(idx < 1 for idx in exclusion_set):
        raise ScinoephileError("Exclusion indexes must be positive (1-based).")
    series = deepcopy(series)
    for i, event in enumerate(series, 1):
        if i in exclusion_set:
            info(f"Skipping flattening of subtitle {i}, with text:\n{event.text}")
            continue
        event.text = _get_eng_text_flattened(event.text.strip())
    return series


def _get_eng_text_flattened(text: str) -> str:
    """Get multi-line English text flattened to a single line.

    Accounts for dashes ('-') used for dialogue from multiple sources.

    Arguments:
        text: text to flatten
    Returns:
        Flattened text
    """
    line_sep = "\\N"
    flattened = text.replace("\r\n", "\n").replace("\n", line_sep)

    # Merge conversations
    lines = flattened.split(line_sep)
    if len(lines) == 2:
        first = re.match(r"^\s*[–-]\s*(.+)\s*$", lines[0])
        second = re.match(r"^\s*[–-]\s*(.+)\s*$", lines[1])
        if first and second:
            return f"- {first.group(1).strip()}    - {second.group(1).strip()}"

    # Merge italics
    flattened = re.sub(r"{\\i0}\s*\\N\s*{\\i1}", " ", flattened)

    # Merge lines
    if line_sep in flattened:
        parts = [part.strip() for part in flattened.split(line_sep) if part.strip()]
        flattened = " ".join(parts)
    if line_sep in flattened:
        raise ScinoephileError(
            f"English text flattening did not produce a single line: {flattened!r}"
        )
    return flattened
