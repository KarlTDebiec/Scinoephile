#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable for getting sync groups between source and transcribed series."""

from __future__ import annotations

from logging import warning
from pprint import pformat, pprint

import numpy as np

from scinoephile.audio import AudioSeries
from scinoephile.audio.testing import SplitTestCase
from scinoephile.audio.transcription import CantoneseSplitter
from scinoephile.core.pairs import get_pair_strings
from scinoephile.core.synchronization import (
    SyncGroup,
    get_overlap_string,
    get_sync_overlap_matrix,
)


class CantoneseSyncGrouper:
    """Runnable for getting sync groups between source and transcribed series."""

    def __init__(self, splitter: CantoneseSplitter) -> None:
        """Initialize.

        Arguments:
            splitter: Cantonese splitter.
        """
        self.splitter = splitter

    def group(self, zhongwen_subs: AudioSeries, yuewen_subs: AudioSeries) -> None:
        sync_groups, ambiguous = self._group(zhongwen_subs, yuewen_subs)
        print(f"\nSYNC GROUPS:\n{pformat(sync_groups, width=120)}")
        print(f"\nAMBIGUOUS:\n{ambiguous}")

    def _group(
        self, zhongwen_subs: AudioSeries, yuewen_subs: AudioSeries
    ) -> tuple[list[SyncGroup], list[int]]:
        zhongwen_str, yuewen_str = get_pair_strings(zhongwen_subs, yuewen_subs)
        print(f"\nMANDARIN:\n{zhongwen_str}")
        print(f"\nCANTONESE:\n{yuewen_str}")

        overlap = get_sync_overlap_matrix(zhongwen_subs, yuewen_subs)
        print("\nOVERLAP:")
        print(get_overlap_string(overlap))

        nascent_sync_groups = [([zw_i + 1], []) for zw_i in range(overlap.shape[0])]
        overlap_threshold = 0.33

        ambiguous = []

        for yw_i in range(overlap.shape[1]):
            column = overlap[:, yw_i]
            rank = np.argsort(column)[::-1]

            if column[rank[0]] != 0:
                column = column / column[rank[0]]
            indexes_over_threshold = np.where(column > overlap_threshold)[0]

            if len(indexes_over_threshold) == 1:
                zw_i = indexes_over_threshold[0]
                nascent_sync_groups[zw_i][1].append(yw_i + 1)
                continue
            ambiguous.append(yw_i)

        for yw_i in ambiguous:
            column = overlap[:, yw_i]
            rank = np.argsort(column)[::-1]

            if column[rank[0]] != 0:
                column = column / column[rank[0]]
            indexes_over_threshold = np.where(column > overlap_threshold)[0]

            if len(indexes_over_threshold) == 2:
                zw_one_idx, zw_two_idx = indexes_over_threshold
                yw_one_idxs = [i - 1 for i in nascent_sync_groups[zw_one_idx][1]]
                yw_two_idxs = [i - 1 for i in nascent_sync_groups[zw_two_idx][1]]
                zhongwen_one_input = zhongwen_subs.events[zw_one_idx].text
                yuewen_one_input = "".join(
                    [yuewen_subs.events[i].text for i in yw_one_idxs]
                )
                yuewen_one_overlap = round(float(column[zw_one_idx]), 2)
                zhongwen_two_input = zhongwen_subs.events[zw_two_idx].text
                yuewen_two_input = "".join(
                    [yuewen_subs.events[i].text for i in yw_two_idxs]
                )
                yuewen_two_overlap = round(float(column[zw_two_idx]), 2)
                yuewen_ambiguous_input = yuewen_subs.events[yw_i].text
                test_case = SplitTestCase(
                    zhongwen_one_input=zhongwen_one_input,
                    yuewen_one_input=yuewen_one_input,
                    yuewen_one_overlap=yuewen_one_overlap,
                    zhongwen_two_input=zhongwen_two_input,
                    yuewen_two_input=yuewen_two_input,
                    yuewen_two_overlap=yuewen_two_overlap,
                    yuewen_ambiguous_input=yuewen_ambiguous_input,
                    yuewen_one_output="",
                    yuewen_two_output="",
                )
                pprint(test_case)
            else:
                warning(
                    f"Unexpected number of indexes over threshold for yw_i={yw_i}: "
                    f"{len(indexes_over_threshold)}"
                )
                print()

        return nascent_sync_groups, [i + 1 for i in ambiguous]
