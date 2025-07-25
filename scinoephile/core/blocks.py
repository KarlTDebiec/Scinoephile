#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to the management of series as blocks of smaller series."""

from __future__ import annotations

import warnings
from copy import deepcopy
from typing import TYPE_CHECKING

from scinoephile.core import ScinoephileError

if TYPE_CHECKING:
    from scinoephile.core.series import Series


def get_blocks_by_pause(series: Series, pause_length: int = 3000) -> list[Series]:
    """Split a Series into blocks using pauses without text.

    Arguments:
        series: Series to split into blocks
        pause_length: Split whenever a pause of this length is encountered
    Returns:
        Series split into blocks
    """
    warnings.warn(
        "get_blocks_by_pause() is deprecated and will be removed in a future version. "
        "Use get_block_indexes_by_pause() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    blocks = []

    source = deepcopy(series.events)

    def get_nascent_block_cutoff():
        """Get latest acceptable start for an event to be added to the nascent block."""
        cutoff = 0
        if nascent_block:
            cutoff = max(cutoff, nascent_block[-1].end)
        cutoff += pause_length

        return cutoff

    # Split into blocks
    while source:
        # Start a new block, with one event from the earlier of the two sources
        nascent_block = [source.pop(0)]

        # Extend block until a long enough pause is hit or sources are empty
        changed = True
        while changed:
            changed = False
            # Extend nascent_block until a pause is encountered in source
            for event in source:
                if event.start >= get_nascent_block_cutoff():
                    break
                nascent_block.append(source.pop(0))
                changed = True

        block = series.__class__()
        block.events = nascent_block
        blocks.append(block)

    return blocks


def get_block_indexes_by_pause(
    series: Series, pause_length: int = 3000
) -> list[tuple[int, int]]:
    """Get indexes of blocks in a Series split by pauses without text.

    Blocks are 1-indexed and the start and end indexes are inclusive.

    Arguments:
        series: Series to split into blocks
        pause_length: Split whenever a pause of this length is encountered
    Returns:
        Start and end indexes of each block
    """
    if not series.events:
        return []
    block_indexes = []
    start = 0
    prev_end = None

    for i, event in enumerate(series):
        if prev_end is not None and event.start - prev_end >= pause_length:
            block_indexes.append((start, i))
            start = i
        prev_end = event.end
    block_indexes.append((start, len(series)))

    return block_indexes


def get_concatenated_series(blocks: list[Series]) -> Series:
    """Contatenate a list of sequential series blocks into a single series.

    Arguments:
        blocks: Series to concatenate
    Returns:
        Concatenated series
    """
    if len(blocks) == 0:
        raise ScinoephileError("No blocks to concatenate")
    concatenated = type(blocks[0])()
    for block in blocks:
        concatenated.events.extend(block.events)
    concatenated.events.sort(key=lambda x: x.start)
    return concatenated


__all__ = [
    "get_blocks_by_pause",
    "get_block_indexes_by_pause",
    "get_concatenated_series",
]
