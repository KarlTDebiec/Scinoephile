#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to pairs of series."""

from __future__ import annotations

from copy import deepcopy

from .exceptions import ScinoephileError
from .subtitles import Series

__all__ = [
    "get_block_pair_indexes_by_pause",
    "get_block_pairs_by_pause",
    "get_pair_with_zero_start",
    "get_pair_strings",
]


def get_block_pair_indexes_by_pause(
    one: Series,
    two: Series,
    pause_length: int = 3000,
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Get indexes of paired blocks split by pauses without text in either series.

    Arguments:
        one: first series
        two: second series
        pause_length: split whenever a pause of this length is encountered
    Returns:
        start and end indexes of each paired block in both series
    """
    block_indexes = []
    one_idx = 0
    two_idx = 0

    while one_idx < len(one) or two_idx < len(two):
        one_start_idx = one_idx
        two_start_idx = two_idx

        def get_cutoff() -> int:
            """Get the latest event end plus the selected pause length."""
            cutoff = 0
            if one_idx > one_start_idx:
                cutoff = max(cutoff, one[one_idx - 1].end)
            if two_idx > two_start_idx:
                cutoff = max(cutoff, two[two_idx - 1].end)
            return cutoff + pause_length

        # Start a new block with the earlier event
        if one_idx < len(one) and two_idx < len(two):
            if one[one_idx].start <= two[two_idx].start:
                one_idx += 1
            else:
                two_idx += 1
        elif one_idx < len(one):
            one_idx += 1
        else:
            two_idx += 1

        # Extend the block until both series reach a long enough pause
        changed = True
        while changed:
            changed = False
            while one_idx < len(one) and one[one_idx].start < get_cutoff():
                one_idx += 1
                changed = True
            while two_idx < len(two) and two[two_idx].start < get_cutoff():
                two_idx += 1
                changed = True

        block_indexes.append(((one_start_idx, one_idx), (two_start_idx, two_idx)))

    return block_indexes


def get_block_pairs_by_pause(
    one: Series,
    two: Series,
    pause_length: int = 3000,
) -> list[tuple[Series, Series]]:
    """Split a pair of series into blocks using pauses without text in either.

    Arguments:
        one: first series
        two: second series
        pause_length: split whenever a pause of this length is encountered
    Returns:
        pairs of series split into blocks
    """
    blocks = []
    for one_indexes, two_indexes in get_block_pair_indexes_by_pause(
        one,
        two,
        pause_length,
    ):
        block_one = one.__class__()
        block_two = two.__class__()
        block_one.events = deepcopy(one.events[slice(*one_indexes)])
        block_two.events = deepcopy(two.events[slice(*two_indexes)])
        blocks.append((block_one, block_two))

    return blocks


def get_pair_with_zero_start(one: Series, two: Series) -> tuple[Series, Series]:
    """Shift a pair of series' start times to zero.

    If the two series have the same start time, both will be shifted to zero. If they
    have different start times, the earlier start time will be shifted to zero, and the
    later will be shifted by the same amount.

    Arguments:
        one: first series
        two: second series
    Returns:
        pair with their start times shifted to zero
    """
    if one.events and two.events:
        start_time = min(one.events[0].start, two.events[0].start)
    elif one.events:
        start_time = one.events[0].start
    elif two.events:
        start_time = two.events[0].start
    else:
        raise ScinoephileError("Both subtitle series are empty")

    one_shifted = deepcopy(one)
    two_shifted = deepcopy(two)
    one_shifted.shift(ms=-start_time)
    two_shifted.shift(ms=-start_time)

    return one_shifted, two_shifted


def get_pair_strings(one: Series, two: Series) -> tuple[str, str]:
    """Get string representations of two series.

    Arguments:
        one: first series
        two: second series
    Returns:
        strings of each series
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
        raise ScinoephileError("Both subtitle series are empty")

    one_string = one.to_simple_string(start=start, duration=duration)
    two_string = two.to_simple_string(start=start, duration=duration)
    return one_string, two_string
