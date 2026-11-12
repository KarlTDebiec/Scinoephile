#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Search syntax for subtitle blocks."""

from __future__ import annotations

from re import IGNORECASE, fullmatch

__all__ = ["parse_block_query"]


def parse_block_query(query: str) -> int | None:
    """Parse an exact block query such as `block 12`, `block:12`, or `block #12`.

    Arguments:
        query: subtitle search query
    Returns:
        requested block number, or None for a text search
    """
    match = fullmatch(r"block\s*[:#]?\s*(\d+)", query.strip(), IGNORECASE)
    if match is not None:
        return int(match[1])
    return None
