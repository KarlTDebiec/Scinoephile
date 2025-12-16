#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code.

Package hierarchy (modules may import from any above):
* exceptions / text
* llms
* fusion / proofreading / review
"""

from __future__ import annotations

from .block import Block
from .exceptions import ScinoephileError
from .series import Series
from .subtitle import Subtitle

__all__ = [
    "Block",
    "ScinoephileError",
    "Series",
    "Subtitle",
    "get_series_with_subs_merged",
    "get_sub_merged",
]


def get_series_with_subs_merged(series: Series, idx: int) -> Series:
    """Get a series with a subtitle at the given index merged with its successor.

    Arguments:
        series: series to modify
        idx: index of subtitle to merge with its successor
    Returns:
        Modified series with merged subtitle
    """
    if idx < 0 or idx >= len(series.events) - 1:
        raise ScinoephileError(
            f"Cannot merge subtitles {idx} and {idx + 1} in series with "
            f"{len(series.events)} subtitles."
        )

    merged_series = Series()
    merged_series.events = (
        series.events[:idx]
        + [get_sub_merged([series.events[idx], series.events[idx + 1]])]
        + series.events[idx + 2 :]
    )
    return merged_series


def get_sub_merged(subs: list[Subtitle], *, text: str | None = None) -> Subtitle:
    """Merge subtitles into a single subtitle.

    Arguments:
        subs: Subtitles to merge
        text: Text to use for the merged subtitle, defaults to simple concatenation
    Returns:
        Merged subtitle
    """
    if text is None:
        text = "".join(sub.text for sub in subs)

    return Subtitle(start=subs[0].start, end=subs[-1].end, text=text)
