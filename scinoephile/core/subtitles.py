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


def get_subtitles_pair_with_start_shifted_to_zero(
    subtitles_one: SubtitleSeries,
    subtitles_two: SubtitleSeries,
) -> tuple[SubtitleSeries, SubtitleSeries]:
    """Shift the start time of two subtitle sets to zero.

    Arguments:
        subtitles_one: first subtitle series
        subtitles_two: second subtitle series
    Returns:
        tuple containing the two subtitle series with their start times
        shifted to zero
    """
    subtitles_one_shifted = deepcopy(subtitles_one)
    subtitles_two_shifted = deepcopy(subtitles_two)
    start_time = min(
        subtitles_one_shifted.events[0].start, subtitles_two_shifted.events[0].start
    )
    subtitles_one_shifted.shift(ms=-start_time)
    subtitles_two_shifted.shift(ms=-start_time)
    return subtitles_one_shifted, subtitles_two_shifted


def get_subtitles_pair_split_into_natural_blocks(
    subtitles_one: SubtitleSeries,
    subtitles_two: SubtitleSeries,
    gap_length: int = 3000,
) -> list[tuple[SubtitleSeries, SubtitleSeries]]:
    """Split a pair of subtitles into natural blocks using gaps without text in either.

    Arguments:
        subtitles_one: first subtitle series
        subtitles_two: second subtitle series
        gap_length: split whenever a gap of this length is encountered
    Returns:
        pairs of subtitles split into natural blocks
    """
    blocks = []
    source_one = deepcopy(subtitles_one.events)
    source_two = deepcopy(subtitles_two.events)

    def get_nascent_block_cutoff():
        return (
            max(
                nascent_block_one[-1].end if nascent_block_one else 0,
                nascent_block_two[-1].end if nascent_block_two else 0,
            )
            + gap_length
        )

    # Split into blocks
    while source_one or source_two:
        # Start a new block
        nascent_block_one = []
        nascent_block_two = []
        if source_one and source_one[0].start <= source_two[0].start:
            nascent_block_one.append(source_one.pop(0))
        else:
            nascent_block_two.append(source_two.pop(0))

        # Extend block until a long enough gat is hit or sources are empty
        changed = True
        while changed:
            changed = False
            while source_one and source_one[0].start < get_nascent_block_cutoff():
                nascent_block_one.append(source_one.pop(0))
                changed = True
            while source_two and source_two[0].start < get_nascent_block_cutoff():
                nascent_block_two.append(source_two.pop(0))
                changed = True

        # Store blocks
        block_one = SubtitleSeries()
        block_two = SubtitleSeries()
        block_one.events = nascent_block_one
        block_two.events = nascent_block_two
        blocks.append((block_one, block_two))

    end = 0
    for i, (block_one, block_two) in enumerate(blocks):
        start = 10000000
        if block_one.events:
            start = min(start, block_one.events[0].start)
        if block_two.events:
            start = min(start, block_two.events[0].start)
        diff = start - end
        if block_one.events:
            end = max(end, block_one.events[-1].end)
        if block_two.events:
            end = max(end, block_two.events[-1].end)
        print(
            f"{i:3d} "
            f"{len(block_one.events):3} "
            f"{len(block_two.events):3} "
            f"{start:8d} "
            f"{end:8d} "
            f"{diff:8d}"
        )

    return blocks
