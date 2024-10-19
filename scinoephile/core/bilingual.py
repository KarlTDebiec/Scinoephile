#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to bilingual text."""
from __future__ import annotations

from scinoephile.core import SubtitleSeries
from scinoephile.core.subtitles import (
    check_if_pair_is_cleanly_mapped,
    get_merged_from_blocks,
    get_pair_blocks_by_pause,
    get_synced_from_cleanly_mapped_pair,
)


def get_bilingual_subtitles(
    hanzi: SubtitleSeries,
    english: SubtitleSeries,
) -> SubtitleSeries:
    blocks = get_pair_blocks_by_pause(hanzi, english)
    bilingual_blocks = []

    for hanzi_block, english_block in blocks:
        if check_if_pair_is_cleanly_mapped(hanzi_block, english_block):
            bilingual_block = get_synced_from_cleanly_mapped_pair(
                hanzi_block, english_block
            )
        else:
            # TODO: Use OpenAI API to synchronize subtitles
            bilingual_block = []

            # If LENGTH is less than MAX_LENGTH
            #   Shift time to 0:00:00 using get_pair_with_zero_start
            #   Ask OpenAI service to synchronize
            #   Build bilingual block from OpenAI response
            # If LENGTH is greater than MAX_LENGTH
            #   Split into blocks of BLOCK_LENGTH, with OVERLAP_LENGTH overlap
            #   For each block
            #       Shift time to 0:00:00 using get_pair_with_zero_start
            #       Ask OpenAI service to synchronize
            #   For each block after the first, shift indexes to match
            #   Compare overlapping sections of blocks
            #   If there is a mismatch, ask OpenAI service to resolvez
            #   Build bilingual block from OpenAI response

        bilingual_blocks.append(bilingual_block)

    print("")

    bilingual = get_merged_from_blocks(bilingual_blocks)

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

    # block_size = 16
    # overlap = 12
    #
    # start_index = 0
    # end_index = 0
    #
    # bilingual = SubtitleSeries()
    # blocks = get_subtitle_blocks_for_synchronization(
    #     hanzi, english, block_size, overlap
    # )
    # last_bilingual_block = None
    # for i, (hanzi_block, english_block) in enumerate(blocks):
    #     print(f"Processing block {i + 1}/{len(blocks)}")
    #     bilingual_block = self.get_synchronization(hanzi_block, english_block)
    #
    #     if last_bilingual_block:
    #         overlap_previous_events = last_bilingual_block.events[-overlap:]
    #         overlap_current_events = bilingual_block.events[:overlap]
    #         if overlap_previous_events != overlap_current_events:
    #             print(
    #                 f"Mismatch between last and current block:\n\n",
    #                 f"{pformat(overlap_previous_events)}\n\n",
    #                 f"{pformat(overlap_current_events)}",
    #             )
    #
    #     bilingual.events.extend(bilingual_block.events[: (block_size - overlap)])
    #
    #     last_bilingual_block = bilingual_block
    #
    # return bilingual
