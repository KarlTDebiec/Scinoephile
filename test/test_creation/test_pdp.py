#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test for creating tests for PDP."""

from __future__ import annotations

from scinoephile.core import Series
from scinoephile.core.pairs import get_pair_blocks_by_pause, get_pair_strings
from scinoephile.core.synchronization import (
    are_series_one_to_one,
    get_overlap_string,
    get_sync_groups,
    get_sync_groups_string,
    get_sync_overlap_matrix,
    get_synced_series_from_groups,
)
from scinoephile.testing import SyncTestCase


# Remove underscore to test
def _test_get_test_cases_pdp(pdp_yue_hant_simplify: Series, pdp_eng_clean: Series):
    """Test for creating tests for PDP.

    Arguments:
        pdp_yue_hant_simplify: PDP 粤语繁体简体 series with which to create tests
        pdp_eng_clean: PDP English clean series with which to create tests
    """
    pair_blocks = get_pair_blocks_by_pause(pdp_yue_hant_simplify, pdp_eng_clean)
    bilingual_blocks = []

    hanzi_start = 0
    english_start = 0

    for hanzi_block, english_block in pair_blocks:
        hanzi_end = hanzi_start + len(hanzi_block)
        english_end = english_start + len(english_block)

        if are_series_one_to_one(hanzi_block, english_block):
            hanzi_start = hanzi_end
            english_start = english_end
            continue

        # if max(len(hanzi_block), len(english_block)) <= 10:
        #     hanzi_start = hanzi_end
        #     english_start = english_end
        #     continue

        # if hanzi_start < 559:
        #     hanzi_start = hanzi_end
        #     english_start = english_end
        #     continue

        # print(f"\n{'=' * 80}")
        # print((hanzi_start, hanzi_end, english_start, english_end))

        hanzi_str, english_str = get_pair_strings(hanzi_block, english_block)
        print(f"\nCHINESE:\n{hanzi_str}")
        print(f"\nENGLISH:\n{english_str}")

        overlap = get_sync_overlap_matrix(hanzi_block, english_block)
        print("\nOVERLAP:")
        print(get_overlap_string(overlap))

        sync_groups = get_sync_groups(hanzi_block, english_block)
        print(f"\nSYNC GROUPS:\n{get_sync_groups_string(sync_groups)}")

        sync_series = get_synced_series_from_groups(
            hanzi_block, english_block, sync_groups
        )
        print(f"\nSYNCED SUBTITLES:\n{sync_series.to_simple_string()}")

        bilingual_blocks.append(sync_series)

        test_case = SyncTestCase(
            hanzi_start=hanzi_start,
            hanzi_end=hanzi_end,
            english_start=english_start,
            english_end=english_end,
            sync_groups=sync_groups,
        )
        print(f"\nTEST CASE:\n{test_case}")
        print(f"{test_case},")

        hanzi_start = hanzi_end
        english_start = english_end
