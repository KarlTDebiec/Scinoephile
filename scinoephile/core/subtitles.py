#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to subtitles."""
from __future__ import annotations

from copy import deepcopy
from itertools import chain

from scinoephile.core.exceptions import ScinoephileException
from scinoephile.core.subtitle_series import SubtitleSeries


def check_if_pair_is_cleanly_mapped(
    subtitles_one: SubtitleSeries,
    subtitles_two: SubtitleSeries,
) -> bool:
    """Check if a pair of subtitles have clean 1:1 mapping with no other overlap.

    Arguments:
        subtitles_one: first subtitle series
        subtitles_two: second subtitle series
    Returns:
        True if subtitles are cleanly mapped, False otherwise
    """
    if len(subtitles_one.events) != len(subtitles_two.events):
        return False

    for i, (event_one, event_two) in enumerate(
        zip(subtitles_one.events, subtitles_two.events)
    ):
        # Ensure event_one overlaps event_two
        if not (event_one.start <= event_two.end and event_two.start <= event_one.end):
            return False

        # Ensure event_two overlaps with event_one
        if not (event_two.start <= event_one.end and event_one.start <= event_two.end):
            return False

        # Ensure event_one does not overlap with any other event in subtitles_two
        for j, other_event_two in enumerate(subtitles_two.events):
            if i == j:
                continue
            if (
                event_one.start <= other_event_two.end
                and other_event_two.start <= event_one.end
            ):
                return False

        # Ensure event_two does not overlap with any other event in subtitles_one
        for j, other_event_one in enumerate(subtitles_one.events):
            if i == j:
                continue
            if (
                event_two.start <= other_event_one.end
                and other_event_one.start <= event_two.end
            ):
                return False

    return True


def get_merged_from_blocks(blocks: list[SubtitleSeries]) -> SubtitleSeries:
    merged = SubtitleSeries()
    merged.events = list(chain.from_iterable([b.events for b in blocks]))
    return merged


def get_pair_blocks_by_pause(
    subtitles_one: SubtitleSeries,
    subtitles_two: SubtitleSeries,
    pause_length: int = 3000,
) -> list[tuple[SubtitleSeries, SubtitleSeries]]:
    """Split a pair of subtitles into blocks using pauses without text in either.

    Arguments:
        subtitles_one: first subtitle series
        subtitles_two: second subtitle series
        pause_length: split whenever a pause of this length is encountered
    Returns:
        pairs of subtitles split into blocks
    """
    blocks = []
    source_one = deepcopy(subtitles_one.events)
    source_two = deepcopy(subtitles_two.events)

    def get_nascent_block_cutoff():
        """Get latest acceptable start for an event to be added to the nascent block"""
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
        if source_one and source_one[0].start <= source_two[0].start:
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
        block_one = SubtitleSeries()
        block_two = SubtitleSeries()
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


def get_pair_with_zero_start(
    subtitles_one: SubtitleSeries,
    subtitles_two: SubtitleSeries,
) -> tuple[SubtitleSeries, SubtitleSeries]:
    """Shift a pair of subtitles' start times to zero.

    If the two subtitles have the same start time, both will be shifted to zero. If they
    have different start times, the earlier start time will be shifted to zero, and the
    later will be shifted by the same amount.

    Arguments:
        subtitles_one: first subtitle series
        subtitles_two: second subtitle series
    Returns:
        pair with their start times shifted to zero
    """
    start_time = min(subtitles_one.events[0].start, subtitles_two.events[0].start)

    subtitles_one_shifted = deepcopy(subtitles_one)
    subtitles_two_shifted = deepcopy(subtitles_two)
    subtitles_one_shifted.shift(ms=-start_time)
    subtitles_two_shifted.shift(ms=-start_time)

    return subtitles_one_shifted, subtitles_two_shifted


def get_pair_strings_with_relative_time(
    subtitles_one: SubtitleSeries,
    subtitles_two: SubtitleSeries,
) -> tuple[str, str]:
    """Get SRT-style string representations of two series, but with proportional timings.

    Arguments:
        subtitles_one: first subtitle series
        subtitles_two: second subtitle series
    Returns:
        SRT-style strings of each series, but with proportional timings
    """
    subtitles_one, subtitles_two = get_pair_with_zero_start(
        subtitles_one, subtitles_two
    )
    start = min(subtitles_one.events[0].start, subtitles_two.events[0].start)
    duration = max(subtitles_one.events[-1].end, subtitles_two.events[-1].end) - start
    str_one = ""
    for i, event in enumerate(subtitles_one.events, 1):
        str_one += (
            f"{i}\n"
            f"{round(100 * (event.start - start) / duration)} "
            f"--> "
            f"{round(100 * (event.end - start) / duration)}\n"
            f"{event.text}\n\n"
        )
    str_one = str_one.strip()

    str_two = ""
    for i, event in enumerate(subtitles_two.events, 1):
        str_two += (
            f"{i}\n"
            f"{round(100 * (event.start - start) / duration)} "
            f"--> "
            f"{round(100 * (event.end - start) / duration)}\n"
            f"{event.text}\n\n"
        )
    str_two = str_two.strip()

    return str_one, str_two


def get_series_pair_strings(
    series_one: SubtitleSeries,
    series_two: SubtitleSeries,
) -> tuple[str, str]:
    """Get string representations of two series.

    Arguments:
        series_one: first subtitle series
        series_two: second subtitle series
    Returns:
        strings of each series
    """
    series_one, series_two = get_pair_with_zero_start(series_one, series_two)
    start = min(series_one.events[0].start, series_two.events[0].start)
    duration = max(series_one.events[-1].end, series_two.events[-1].end) - start

    def get_string(subitles):
        string = ""
        for i, event in enumerate(subitles.events, 1):
            string += (
                f"{i:2d} |"
                f"{round(100 * (event.start - start) / duration):4d} |"
                f"{round(100 * (event.end - start) / duration):4d} | "
                f"{event.text}\n"
            )
        return string.rstrip()

    return get_string(series_one), get_string(series_two)


def get_synced_from_cleanly_mapped_pair(
    subtitles_one: SubtitleSeries,
    subtitles_two: SubtitleSeries,
) -> SubtitleSeries:
    """Get synchronized subtitles from a cleanly mapped pair.

    Arguments:
        subtitles_one: first subtitle series
        subtitles_two: second subtitle series
    Returns:
        synchronized subtitles
    """
    synced_subtitles = SubtitleSeries()
    synced_subtitles.events = []
    for event_one, event_two in zip(subtitles_one.events, subtitles_two.events):
        synced_event = deepcopy(event_one)
        synced_event.text = f"{event_one.text}\n{event_two.text}"
        synced_subtitles.events.append(synced_event)

    return synced_subtitles


def get_subtitle_blocks_for_synchronization(
    authoritative_subtitles: SubtitleSeries,
    adjustable_subtitles: SubtitleSeries,
    block_size: int = 16,
    overlap: int = 8,
) -> list[tuple[SubtitleSeries, SubtitleSeries]]:
    """Get subtitle blocks for synchronization.

    Arguments:
        authoritative_subtitles: subtitles to which to synchronize
        adjustable_subtitles: subtitles to synchronize
        block_size: size of each block in seconds
        overlap: overlap between blocks in seconds
    Returns:
        subtitle block pairs for each round of synchronization
    """
    start_index = 0
    end_index = 0

    print(
        f"Synchronizing {len(authoritative_subtitles.events)} authoritative "
        f"and {len(adjustable_subtitles.events)} english subtitles"
    )
    blocks = []
    while end_index < len(authoritative_subtitles.events):
        end_index = min(start_index + block_size, len(authoritative_subtitles.events))
        print(f"Processing subtitles {start_index}-{end_index}")
        authoritative_block = get_subtitles_block_by_index(
            authoritative_subtitles, start_index, end_index
        )
        start_time = authoritative_block.events[0].start
        end_time = authoritative_block.events[-1].end
        adjustable_block = get_subtitles_block_by_time(
            adjustable_subtitles, start_time, end_time
        )
        print(
            f"Authoritative block has {len(authoritative_block.events)} subtitles, "
            f"and adjustable block has {len(adjustable_block.events)} subtitles"
        )
        blocks.append((authoritative_block, adjustable_block))

        start_index += block_size - overlap
    return blocks


def get_subtitles_block_by_index(
    subtitles: SubtitleSeries, start_index: int, end_index: int
) -> SubtitleSeries:
    """Get a block of subtitles from a subtitle series by index.

    Arguments:
        subtitles: SubtitleSeries from which to extract block
        start_index: start index of block
        end_index: end index of block
    Returns:
        SubtitleSeries containing only subtitles that fall within the
        specified index range
    """
    if start_index < 0 or start_index > len(subtitles.events) - 1:
        raise ScinoephileException(
            f"Invalid start_index: {start_index}, must be in range "
            f"0 <= start_index <= {len(subtitles.events) - 1}"
        )
    if end_index <= start_index or end_index > len(subtitles.events):
        raise ScinoephileException(
            f"Invalid end index: {end_index}, must be in range "
            f"{start_index} <= end_index <= {len(subtitles.events)}"
        )
    block = SubtitleSeries()
    block.events = deepcopy(subtitles.events[start_index:end_index])
    return block


def get_subtitles_block_by_time(
    subtitles: SubtitleSeries, start_time: float, end_time: float
) -> SubtitleSeries:
    """Get a block of subtitles from a subtitle series by time.

    Arguments:
        subtitles: SubtitleSeries from which to extract block
        start_time: start time of block
        end_time: end time of block
    Returns:
        SubtitleSeries containing only subtitles that fall within the
        specified time range
    """
    block = SubtitleSeries()
    block.events = [
        event for event in subtitles.events if start_time <= event.start <= end_time
    ]
    return block
