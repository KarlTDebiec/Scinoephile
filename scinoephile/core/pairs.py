#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to pairs of series."""

from __future__ import annotations

from copy import deepcopy

from scinoephile.core import ScinoephileException
from scinoephile.core.series import Series


def get_pair_blocks_by_pause(
    one: Series,
    two: Series,
    pause_length: int = 3000,
) -> list[tuple[Series, Series]]:
    """Split a pair of series into blocks using pauses without text in either.

    Arguments:
        one: First series
        two: Second series
        pause_length: Split whenever a pause of this length is encountered
    Returns:
        Pairs of series split into blocks
    """
    blocks = []
    source_one = deepcopy(one.events)
    source_two = deepcopy(two.events)

    def get_nascent_block_cutoff():
        """Get latest acceptable start for an event to be added to the nascent block."""
        cutoff = 0
        if nascent_block_one:
            cutoff = max(cutoff, nascent_block_one[-1].end)
        if nascent_block_two:
            cutoff = max(cutoff, nascent_block_two[-1].end)
        cutoff += pause_length

        return cutoff

    # Split into blocks
    while source_one or source_two:
        # Start a new block, with one event from the earlier of the two sources
        nascent_block_one = []
        nascent_block_two = []
        if source_one and source_two:
            if source_one[0].start <= source_two[0].start:
                nascent_block_one.append(source_one.pop(0))
            else:
                nascent_block_two.append(source_two.pop(0))
        elif source_one:
            nascent_block_one.append(source_one.pop(0))
        else:
            nascent_block_two.append(source_two.pop(0))

        # Extend block until a long enough pause is hit or sources are empty
        changed = True
        while changed:
            changed = False
            # Extend nascent_block_one until a pause is encountered in source_one
            while source_one and source_one[0].start < get_nascent_block_cutoff():
                nascent_block_one.append(source_one.pop(0))
                changed = True
            # Extend nascent_block_two until a pause is encountered in source_two
            while source_two and source_two[0].start < get_nascent_block_cutoff():
                nascent_block_two.append(source_two.pop(0))
                changed = True

        # Store block
        block_one = one.__class__()
        block_two = two.__class__()
        block_one.events = nascent_block_one
        block_two.events = nascent_block_two
        blocks.append((block_one, block_two))

    # end = 0
    # for i, (block_one, block_two) in enumerate(blocks):
    #     start = 10000000
    #     if block_one.events:
    #         start = min(start, block_one.events[0].start)
    #     if block_two.events:
    #         start = min(start, block_two.events[0].start)
    #     diff = start - end
    #     if block_one.events:
    #         end = max(end, block_one.events[-1].end)
    #     if block_two.events:
    #         end = max(end, block_two.events[-1].end)
    #     print(
    #         f"{i:3d} "
    #         f"{len(block_one.events):3} "
    #         f"{len(block_two.events):3} "
    #         f"{start:8d} "
    #         f"{end:8d} "
    #         f"{diff:8d}"
    #     )

    return blocks


def get_pair_with_zero_start(one: Series, two: Series) -> tuple[Series, Series]:
    """Shift a pair of series' start times to zero.

    If the two series have the same start time, both will be shifted to zero. If they
    have different start times, the earlier start time will be shifted to zero, and the
    later will be shifted by the same amount.

    Arguments:
        one: First series
        two: Second series
    Returns:
        Pair with their start times shifted to zero
    """
    if one.events and two.events:
        start_time = min(one.events[0].start, two.events[0].start)
    elif one.events:
        start_time = one.events[0].start
    elif two.events:
        start_time = two.events[0].start
    else:
        raise ScinoephileException("Both subtitle series are empty")

    one_shifted = deepcopy(one)
    two_shifted = deepcopy(two)
    one_shifted.shift(ms=-start_time)
    two_shifted.shift(ms=-start_time)

    return one_shifted, two_shifted


def get_pair_strings(one: Series, two: Series) -> tuple[str, str]:
    """Get string representations of two series.

    Arguments:
        one: First series
        two: Second series
    Returns:
        Strings of each series
    """
    one, two = get_pair_with_zero_start(one, two)
    if one.events and two.events:
        start = min(one.events[0].start, two.events[0].start)
        duration = max(one.events[-1].end, two.events[-1].end) - start
    elif one.events:
        start = one.events[0].start
        duration = one.events[-1].end - start
    elif two.events:
        start = two.events[0].start
        duration = two.events[-1].end - start
    else:
        raise ScinoephileException("Both subtitle series are empty")

    one_string = one.to_simple_string(start=start, duration=duration)
    two_string = two.to_simple_string(start=start, duration=duration)
    return one_string, two_string
