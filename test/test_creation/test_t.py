#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for creatings tests for t."""
from __future__ import annotations

from pprint import pformat

from scinoephile.core import SubtitleSeries
from scinoephile.core.pairs import get_pair_blocks_by_pause, get_pair_strings
from scinoephile.core.synchronization import (
    are_series_one_to_one,
    get_overlap_string,
    get_sync_groups,
    get_sync_overlap_matrix,
    get_synced_subtitles_from_groups,
)
from scinoephile.testing import SyncTestCase
from ..data.t import t_input_english, t_input_hanzi


def test_get_test_cases_t(
    t_input_hanzi: SubtitleSeries,
    t_input_english: SubtitleSeries,
) -> None:
    pair_blocks = get_pair_blocks_by_pause(t_input_hanzi, t_input_english)
    bilingual_blocks = []

    hanzi_start = 0
    english_start = 0

    for hanzi_block, english_block in pair_blocks:
        hanzi_end = hanzi_start + len(hanzi_block.events)
        english_end = english_start + len(english_block.events)

        if are_series_one_to_one(hanzi_block, english_block):
            hanzi_start = hanzi_end
            english_start = english_end
            continue

        # if max(len(hanzi_block.events), len(english_block.events)) <= 10:
        #     hanzi_start = hanzi_end
        #     english_start = english_end
        #     continue

        # if hanzi_start < 559:
        #     hanzi_start = hanzi_end
        #     english_start = english_end
        #     continue

        print((hanzi_start, hanzi_end, english_start, english_end))

        hanzi_str, english_str = get_pair_strings(hanzi_block, english_block)
        print(f"\nCHINESE:\n{hanzi_str}")
        print(f"\nENGLISH:\n{english_str}")

        overlap = get_sync_overlap_matrix(hanzi_block, english_block)
        print("\nOVERLAP:")
        print(get_overlap_string(overlap))

        sync_groups = get_sync_groups(hanzi_block, english_block)
        print(f"\nSYNC GROUPS:\n{pformat(sync_groups, width=120)}")

        sync_subtitles = get_synced_subtitles_from_groups(
            hanzi_block, english_block, sync_groups
        )
        print(f"\nSYNCED SUBTITLES:\n{sync_subtitles.to_simple_string()}")

        bilingual_blocks.append(sync_subtitles)

        test_case = SyncTestCase(
            hanzi_start=hanzi_start,
            hanzi_end=hanzi_end,
            english_start=english_start,
            english_end=english_end,
            sync_groups=sync_groups,
        )
        print(test_case)

        hanzi_start = hanzi_end
        english_start = english_end
