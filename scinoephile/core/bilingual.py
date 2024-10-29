#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to bilingual text."""
from __future__ import annotations

from scinoephile.core import ScinoephileException, SubtitleSeries
from scinoephile.core.openai import get_synced_subtitles
from scinoephile.core.openai.openai_service import OpenAiService
from scinoephile.core.subtitles import (
    check_if_pair_is_cleanly_mapped,
    get_merged_from_blocks,
    get_pair_blocks_by_pause,
    get_pair_with_zero_start,
    get_synced_from_cleanly_mapped_pair,
)


def get_bilingual_subtitles(
    hanzi: SubtitleSeries,
    english: SubtitleSeries,
) -> SubtitleSeries:
    openai_service = OpenAiService()
    blocks = get_pair_blocks_by_pause(hanzi, english)
    bilingual_blocks = []

    hanzi_index = 0
    english_index = 0
    request_count = 0

    for hanzi_block, english_block in blocks:
        if check_if_pair_is_cleanly_mapped(hanzi_block, english_block):
            bilingual_block = get_synced_from_cleanly_mapped_pair(
                hanzi_block, english_block
            )
        else:
            length = max(len(hanzi_block.events), len(english_block.events))
            if length <= 10:
                request_count += 1
                if request_count == 20:
                    break

                hanzi_block_shifted, english_block_shifted = get_pair_with_zero_start(
                    hanzi_block, english_block
                )
                synchronization = openai_service.get_synchronization(
                    hanzi_block_shifted, english_block_shifted
                )
                try:
                    bilingual_block = get_synced_subtitles(
                        hanzi_block, english_block, synchronization
                    )
                    print(
                        f"CHINESE:\n{hanzi_block_shifted.to_string('srt')}\n\n"
                        f"ENGLISH:\n{english_block_shifted.to_string('srt')}\n\n"
                        f"({hanzi_index}, {hanzi_index + len(hanzi_block)}, "
                        f"{english_index}, {english_index + len(english_block)}, "
                        f"SubtitleSeriesResponse("
                        f"explanation={synchronization.explanation},"
                        f"synchronization={synchronization.synchronization}))"
                    )
                except ScinoephileException as e:
                    raise ScinoephileException(
                        f"Inappropriate synchronization received for :\n\n"
                        f"CHINESE:\n{hanzi_block_shifted.to_string('srt')}\n\n"
                        f"ENGLISH:\n{english_block_shifted.to_string('srt')}\n\n"
                        f"SYNCHRONIZATION:\n{synchronization.model_dump_json(indent=4)}"
                    ) from e

            else:
                bilingual_block = []
                # Split into blocks of BLOCK_LENGTH, with OVERLAP_LENGTH overlap
                # For each block
                #   Shift time to 0:00:00 using get_pair_with_zero_start
                #   Ask OpenAI service to synchronize
                # For each block after the first, shift indexes to match
                # Compare overlapping sections of blocks
                # If there is a mismatch, ask OpenAI service to resolvez
                # Build bilingual block from OpenAI response

        bilingual_blocks.append(bilingual_block)
        hanzi_index += len(hanzi_block)
        english_index += len(english_block)

    print("")

    bilingual = get_merged_from_blocks(bilingual_blocks)
