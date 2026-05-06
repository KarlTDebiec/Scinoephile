#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Duration parsing for cache maintenance operations."""

from __future__ import annotations

import re
from datetime import timedelta

__all__ = ["parse_duration"]


_DURATION_PATTERN = re.compile(
    r"^\s*(?P<value>\d+)\s*(?P<unit>seconds?|secs?|s|minutes?|mins?|m|hours?|hrs?|h|days?|d|weeks?|w)\s*$",
    re.IGNORECASE,
)


def parse_duration(value: str) -> timedelta:
    """Parse a human-friendly duration string.

    Arguments:
        value: duration such as 12h, 7d, or 30 days
    Returns:
        parsed duration
    Raises:
        ValueError: if the duration cannot be parsed
    """
    match = _DURATION_PATTERN.match(value)
    if match is None:
        raise ValueError(f"Invalid duration {value!r}")

    amount = int(match.group("value"))
    unit = match.group("unit").casefold()
    if unit.startswith("s"):
        return timedelta(seconds=amount)
    if unit.startswith("m"):
        return timedelta(minutes=amount)
    if unit.startswith("h"):
        return timedelta(hours=amount)
    if unit.startswith("d"):
        return timedelta(days=amount)
    if unit.startswith("w"):
        return timedelta(weeks=amount)
    raise ValueError(f"Invalid duration unit {unit!r}")
