#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to stacking subtitle series."""

from __future__ import annotations

from enum import StrEnum
from logging import getLogger
from pprint import pformat

import numpy as np

from .exceptions import ScinoephileError
from .pairs import get_block_pairs_by_pause, get_pair_strings
from .subtitles import Series, Subtitle, get_concatenated_series
from .synchronization import SyncGroup, get_sync_groups

__all__ = [
    "StackTimingMode",
    "get_stacked_series",
    "get_stacked_series_from_groups",
]

logger = getLogger(__name__)


class StackTimingMode(StrEnum):
    """Timing modes for stacked subtitles."""

    TOP = "top"
    """Use top subtitle timing where available."""
    BOTTOM = "bottom"
    """Use bottom subtitle timing where available."""
    OUTER = "outer"
    """Use the full outer timing span of paired subtitles."""


def get_stacked_series(
    one: Series,
    two: Series,
    sync_cutoff: float = 0.16,
    pause_length: int = 3000,
    timing_mode: StackTimingMode = StackTimingMode.OUTER,
) -> Series:
    """Compile stacked subtitles from two series.

    Arguments:
        one: First Series
        two: Second Series
        sync_cutoff: Initial overlap cutoff used to form sync groups
        pause_length: Pause length in milliseconds used to split subtitle blocks
        timing_mode: Timing mode used for stacked subtitles
    Returns:
        Stacked subtitles
    """
    stacked_blocks = []

    logger.info(
        f"Stacking series with sync_cutoff={sync_cutoff} "
        f"and pause_length={pause_length}"
    )

    block_pairs = get_block_pairs_by_pause(one, two, pause_length=pause_length)
    for one_block, two_block in block_pairs:
        one_str, two_str = get_pair_strings(one_block, two_block)
        logger.debug(f"ONE:\n{one_str}")
        logger.debug(f"TWO:\n{two_str}")

        groups = get_sync_groups(one_block, two_block, cutoff=sync_cutoff)
        logger.info(f"SYNC GROUPS:\n{pformat(groups, width=1000)}")

        stacked_block = get_stacked_series_from_groups(
            one_block, two_block, groups, timing_mode=timing_mode
        )
        logger.info(f"STACKED SUBTITLES:\n{stacked_block.to_simple_string()}")
        stacked_blocks.append(stacked_block)

    stacked = get_concatenated_series(stacked_blocks)
    return _get_series_without_overlaps(stacked)


def get_stacked_series_from_groups(
    one: Series,
    two: Series,
    groups: list[SyncGroup],
    timing_mode: StackTimingMode = StackTimingMode.OUTER,
) -> Series:
    """Compile stacked subtitles from two series based on sync groups.

    Arguments:
        one: First series
        two: Second series
        groups: Sync groups including the indexes of subtitles in each series
        timing_mode: Timing mode used for stacked subtitles
    Returns:
        Series whose subtitles are composed of the text of the subtitles from the two
        input series as indicated by the sync groups
    """
    stacked = Series()

    for group in groups:
        one_subs = [one.events[i] for i in group[0]]
        two_subs = [two.events[i] for i in group[1]]

        # Zero to one mapping
        if len(one_subs) == 0 and len(two_subs) == 1:
            stacked.events.append(two_subs[0])
            continue

        # One to zero mapping
        if len(one_subs) == 1 and len(two_subs) == 0:
            stacked.events.append(one_subs[0])
            continue

        # One to one mapping
        if len(one_subs) == 1 and len(two_subs) == 1:
            one_text = one_subs[0].text
            two_text = two_subs[0].text
            start, end = _get_stack_group_timings(one_subs, two_subs, 1, timing_mode)[0]
            stacked.events.append(
                Subtitle(
                    start=start,
                    end=end,
                    text=(
                        f"{one_text}\\N{two_text}"
                        if one_text and two_text
                        else one_text or two_text
                    ),
                )
            )
            continue

        # Many to one mapping
        if len(one_subs) > 1 and len(two_subs) == 1:
            two_sub = two_subs[0]
            timings = _get_stack_group_timings(
                one_subs, two_subs, len(one_subs), timing_mode
            )

            for one_sub, (start, end) in zip(one_subs, timings):
                one_text = one_sub.text
                two_text = two_sub.text
                stacked.events.append(
                    Subtitle(
                        start=start,
                        end=end,
                        text=(
                            f"{one_text}\\N{two_text}"
                            if one_text and two_text
                            else one_text or two_text
                        ),
                    )
                )
            continue

        # One to many mapping
        if len(one_subs) == 1 and len(two_subs) > 1:
            one_sub = one_subs[0]
            timings = _get_stack_group_timings(
                one_subs, two_subs, len(two_subs), timing_mode
            )

            for two_sub, (start, end) in zip(two_subs, timings):
                one_text = one_sub.text
                two_text = two_sub.text
                stacked.events.append(
                    Subtitle(
                        start=start,
                        end=end,
                        text=(
                            f"{one_text}\\N{two_text}"
                            if one_text and two_text
                            else one_text or two_text
                        ),
                    )
                )
            continue

        # Anything else is unsupported
        raise ScinoephileError(
            f"Unsupported sync group with {len(one_subs)} subtitles from series one "
            f"and {len(two_subs)} subtitles from series two."
        )

    return _get_series_without_overlaps(stacked)


def _get_series_without_overlaps(series: Series) -> Series:
    """Get a copy of a subtitle series with adjacent timing overlaps removed.

    Arguments:
        series: subtitle series whose events should be made non-overlapping
    Returns:
        Copy of the subtitle series with adjacent overlaps split at their midpoint
    Raises:
        ScinoephileError: if overlap removal would make a subtitle non-positive
    """
    output = type(series)(
        events=[type(event)(**event.as_dict()) for event in series.events]
    )

    for idx, (previous, current) in enumerate(
        zip(output.events, output.events[1:]), start=1
    ):
        if current.start >= previous.end:
            continue

        minimum_boundary = previous.start + 1
        maximum_boundary = current.end - 1
        if minimum_boundary > maximum_boundary:
            raise ScinoephileError(
                f"Cannot remove subtitle timing overlap between events {idx} "
                f"and {idx + 1} without creating a non-positive duration "
                f"subtitle: previous={previous.start}-{previous.end}, "
                f"current={current.start}-{current.end}."
            )

        boundary = (previous.end + current.start) // 2
        boundary = max(boundary, minimum_boundary)
        boundary = min(boundary, maximum_boundary)

        previous.end = boundary
        current.start = boundary

    return output


def _get_stack_group_interval(
    one_subs: list[Subtitle],
    two_subs: list[Subtitle],
    timing_mode: StackTimingMode,
) -> tuple[int, int]:
    """Get the selected timing interval for a stack group.

    Arguments:
        one_subs: subtitles from the first series
        two_subs: subtitles from the second series
        timing_mode: timing mode used for stacked subtitles
    Returns:
        Start and end times for the stack group
    """
    if timing_mode == StackTimingMode.TOP and one_subs:
        return one_subs[0].start, one_subs[-1].end
    if timing_mode == StackTimingMode.BOTTOM and two_subs:
        return two_subs[0].start, two_subs[-1].end

    starts = [sub.start for sub in one_subs + two_subs]
    ends = [sub.end for sub in one_subs + two_subs]
    return min(starts), max(ends)


def _get_stack_group_timings(
    one_subs: list[Subtitle],
    two_subs: list[Subtitle],
    count: int,
    timing_mode: StackTimingMode,
) -> list[tuple[int, int]]:
    """Get generated subtitle timings for a stack group.

    Arguments:
        one_subs: subtitles from the first series
        two_subs: subtitles from the second series
        count: number of generated subtitles
        timing_mode: timing mode used for stacked subtitles
    Returns:
        Start and end times for each generated subtitle
    """
    if timing_mode == StackTimingMode.TOP and len(one_subs) == count:
        return [(sub.start, sub.end) for sub in one_subs]
    if timing_mode == StackTimingMode.BOTTOM and len(two_subs) == count:
        return [(sub.start, sub.end) for sub in two_subs]

    # Split StackTimingMode.OUTER, or top/bottom groups with mismatched output counts
    group_start, group_end = _get_stack_group_interval(one_subs, two_subs, timing_mode)
    edges = np.linspace(group_start, group_end, count + 1, dtype=int)
    return [(int(start), int(end)) for start, end in zip(edges[:-1], edges[1:])]
