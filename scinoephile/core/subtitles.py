#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to subtitles."""
from copy import deepcopy
from pprint import pformat

from scinoephile.core.exceptions import ScinoephileException
from scinoephile.core.subtitle_series import SubtitleSeries


def get_synchronized_bilingual_subtitles(
    self,
    hanzi: SubtitleSeries,
    english: SubtitleSeries,
) -> SubtitleSeries:
    # 1
    #   Get subtitles 0-15 from hanzi, and the amount of time that they cover
    #   Get the corresponding subtitles from english
    #   Prompt LLM to synchronize the subtitles
    #   Ensure that the output can be parsed into a SubtitleSeries

    # 2
    #   Get subtitles 11-25 from hanzi, and the amount of time that they cover
    #   Get the corresponding subtitles from english
    #   Prompt LLM to synchronize the subtitles
    #   Ensure that the output can be parsed into a SubtitleSeries

    # 3
    #   Validate that subtitles 11-14 are the same from both queries
    #   If not, prompt LLM to reconcile the two

    # 4
    #   Get subtitles 21-35 from hanzi, and the amount of time that they cover
    #   Get the corresponding subtitles from english
    #   Prompt LLM to synchronize the subtitles
    #   Ensure that the output can be parsed into a SubtitleSeries

    # 5
    #   Validate that subtitles 21-24 are the same from both queries
    #   If not, prompt LLM to reconcile the two

    block_size = 16
    overlap = 12

    start_index = 0
    end_index = 0

    bilingual = SubtitleSeries()
    blocks = get_subtitle_blocks_for_synchronization(
        hanzi, english, block_size, overlap
    )
    last_bilingual_block = None
    for i, (hanzi_block, english_block) in enumerate(blocks):
        print(f"Processing block {i + 1}/{len(blocks)}")
        bilingual_block = self.get_synchronization(hanzi_block, english_block)

        if last_bilingual_block:
            overlap_previous_events = last_bilingual_block.events[-overlap:]
            overlap_current_events = bilingual_block.events[:overlap]
            if overlap_previous_events != overlap_current_events:
                print(
                    f"Mismatch between last and current block:\n\n",
                    f"{pformat(overlap_previous_events)}\n\n",
                    f"{pformat(overlap_current_events)}",
                )

        bilingual.events.extend(bilingual_block.events[: (block_size - overlap)])

        last_bilingual_block = bilingual_block

    return bilingual


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
    """Get a block from a subtitle series by time.

    Arguments:
        subtitles: SubtitleSeries from which to extract block
        start_time: Start time of block
        end_time: End time of block
    Returns:
        SubtitleSeries containing only subtitles that fall within the
        specified time range
    """
    block = SubtitleSeries()
    block.events = [
        event for event in subtitles.events if start_time <= event.start <= end_time
    ]
    return block
