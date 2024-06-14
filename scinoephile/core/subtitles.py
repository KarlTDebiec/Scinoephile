#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to subtitles."""
from copy import deepcopy

from scinoephile.core.exceptions import ScinoephileException
from scinoephile.core.subtitle_series import SubtitleSeries


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
        list of tuples of subtitle blocks for each round of synchronization
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
    """
    Get block from subtitle."""
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
    """Get block from subtitle."""
    block = SubtitleSeries()
    block.events = [
        event for event in subtitles.events if start_time <= event.start <= end_time
    ]
    return block
