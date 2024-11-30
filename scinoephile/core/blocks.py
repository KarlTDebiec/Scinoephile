#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to the management of series as blocks of smaller series."""
from __future__ import annotations

from copy import deepcopy

from scinoephile.core import Series


def get_blocks_by_pause(series: Series, pause_length: int = 3000) -> list[Series]:
    """Split a Series into blocks using pauses without text.

    Arguments:
        series: Series to split
        pause_length: split whenever a pause of this length is encountered
    Returns:
        Series split into blocks
    """
    blocks = []

    source = deepcopy(series.events)

    def get_nascent_block_cutoff():
        """Get latest acceptable start for an event to be added to the nascent block"""
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


def get_concatenated_blocks(blocks: list[Series]) -> Series:
    """Contatenate a list of sequential series blocks into a single series.

    Arguments:
        blocks: series to concatenate
    Returns:
        Concatenated series
    """
    cls = blocks[0].__class__ if blocks else Series
    concatenated = cls()
    for block in blocks:
        concatenated.events.extend(block.events)
    concatenated.events.sort(key=lambda x: x.start)
    return concatenated
