#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to 中文 text."""

from __future__ import annotations

import re
from copy import deepcopy

from scinoephile.core.subtitles import Series

__all__ = [
    "get_zho_flattened",
]


def get_zho_flattened(series: Series) -> Series:
    """Get multi-line 中文 series flattened to single lines.

    Arguments:
        series: Series to flatten
    Returns:
        Flattened series
    """
    series = deepcopy(series)
    for event in series:
        event.text = _get_zho_text_flattened(event.text)
    return series


def _get_zho_text_flattened(text: str) -> str:
    """Get multi-line 中文 text flattened to a single line.

    Accounts for dashes ('﹣') used for dialogue from multiple sources.

    # TODO: Consider replacing two western spaces with one eastern space

    Arguments:
        text: text to flatten
    Returns:
        Flattened text
    """
    line_sep = r"\\N"
    flattened = text

    # Merge lines
    if line_sep in flattened:
        parts = [part.strip() for part in flattened.split(line_sep) if part.strip()]
        flattened = "　".join(parts)

    # Merge conversations
    conversation = re.match(
        r"^[-－﹣]?\s*(?P<first>.+)\s+[-－﹣]\s*(?P<second>.+)$",
        flattened,
    )
    if conversation is not None:
        flattened = (
            f"﹣{conversation['first'].strip()}　　﹣{conversation['second'].strip()}"
        )

    return flattened
