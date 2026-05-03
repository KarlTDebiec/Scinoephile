#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Duration string parsing for cache operations."""

from __future__ import annotations

import re
from datetime import timedelta

__all__ = ["parse_duration"]

_UNIT_SECONDS: dict[str, float] = {
    "w": 7 * 24 * 3600,
    "d": 24 * 3600,
    "h": 3600,
    "m": 60,
    "s": 1,
}

_DURATION_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)\s*([wdhms])$")


def parse_duration(value: str) -> timedelta:
    """Parse a duration string into a timedelta.

    Supported units: w (weeks), d (days), h (hours), m (minutes), s (seconds).
    Examples: "7d", "12h", "30m", "1w", "90s".

    Arguments:
        value: duration string
    Returns:
        parsed timedelta
    Raises:
        ValueError: if the string cannot be parsed
    """
    match = _DURATION_PATTERN.match(value.strip().lower())
    if not match:
        raise ValueError(
            f"Invalid duration {value!r}. "
            "Expected a number followed by a unit (w, d, h, m, s), e.g. '7d' or '12h'."
        )
    quantity = float(match.group(1))
    unit = match.group(2)
    return timedelta(seconds=quantity * _UNIT_SECONDS[unit])
