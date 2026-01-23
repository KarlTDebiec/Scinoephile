#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core subtitle data structures and helpers."""

from __future__ import annotations

from scinoephile.core.exceptions import ScinoephileError

from .block import Block
from .series import Series
from .subtitle import Subtitle

__all__ = [
    "Block",
    "Series",
    "Subtitle",
    "get_concatenated_series",
    "get_series_with_subs_merged",
    "get_sub_merged",
]


def get_series_with_subs_merged(series: Series, idx: int) -> Series:
    """Get a series with a subtitle at the given index merged with its successor.

    Arguments:
        series: Series to modify
        idx: Index of subtitle to merge with its successor
    Returns:
        Modified series with merged subtitle
    """
    if idx < 0 or idx >= len(series.events) - 1:
        raise ScinoephileError(
            f"Cannot merge subtitles {idx} and {idx + 1} in series with "
            f"{len(series.events)} subtitles."
        )

    return type(series)(
        events=series.events[:idx]
        + [get_sub_merged([series.events[idx], series.events[idx + 1]])]
        + series.events[idx + 2 :]
    )


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

    subtitle_cls = type(subs[0])
    return subtitle_cls(start=subs[0].start, end=subs[-1].end, text=text)


def get_concatenated_series(blocks: list[Series]) -> Series:
    """Concatenate a list of sequential series blocks into a single series.

    Arguments:
        blocks: Series to concatenate
    Returns:
        Concatenated series
    """
    if len(blocks) == 0:
        raise ScinoephileError("No blocks to concatenate")
    all_events = []
    for block in blocks:
        all_events.extend(block.events)
    all_events.sort(key=lambda x: x.start)
    return type(blocks[0])(events=all_events)
