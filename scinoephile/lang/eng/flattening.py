#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to English text."""

from __future__ import annotations

import re
from copy import deepcopy
from logging import info

from scinoephile.core.series import Series

__all__ = [
    "get_eng_flattened",
]


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
