#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable for getting sync groups between source and transcribed series."""

from __future__ import annotations

from pprint import pformat, pprint

import numpy as np

from scinoephile.audio import AudioSeries
from scinoephile.core import ScinoephileError
from scinoephile.core.pairs import get_pair_strings
from scinoephile.core.synchronization import (
    get_overlap_string,
    get_sync_groups,
    get_sync_overlap_matrix,
)


class CantoneseSyncGrouper:
    """Runnable for getting sync groups between source and transcribed series."""

    def group(
        self,
        zhongwen_subs: AudioSeries,
        yuewen_subs: AudioSeries,
    ) -> None:
        zhongwen_str, yuewen_str = get_pair_strings(zhongwen_subs, yuewen_subs)
        print(f"\nMANDARIN:\n{zhongwen_str}")
        print(f"\nCANTONESE:\n{yuewen_str}")

        overlap = get_sync_overlap_matrix(zhongwen_subs, yuewen_subs)
        print("\nOVERLAP:")
        print(get_overlap_string(overlap))

        from collections import defaultdict, deque

        nascent_sync_groups = [([zw_i + 1], []) for zw_i in range(overlap.shape[0])]
        overlap_threshold = 0.33

        queue = deque(range(overlap.shape[1]))
        retry_counts = defaultdict(int)
        max_retries = 2  # Avoid infinite loops

        while queue:
            yw_i = queue.popleft()
            retry_counts[yw_i] += 1

            column = overlap[:, yw_i]
            rank = np.argsort(column)[::-1]

            if column[rank[0]] == 0:
                # Avoid divide-by-zero
                normalized_column = column
            else:
                normalized_column = column / column[rank[0]]

            indexes_over_threshold = np.where(normalized_column > overlap_threshold)[0]

            if len(indexes_over_threshold) == 0:
                if retry_counts[yw_i] >= max_retries:
                    raise ScinoephileError(
                        "Unsupported scenario:\n"
                        "No Mandarin subtitles\n"
                        "overlap with Cantonese subtitle\n"
                        f"{yw_i + 1:2d}: {yuewen_subs.events[yw_i].text}."
                    )
                queue.append(yw_i)
                continue

            if len(indexes_over_threshold) == 1:
                zw_i = indexes_over_threshold[0]
                nascent_sync_groups[zw_i][1].append(yw_i + 1)
                continue

            # More than one — ambiguous, try again later
            if retry_counts[yw_i] >= max_retries:
                pprint(nascent_sync_groups)
                raise ScinoephileError(
                    "Unsupported scenario:\n"
                    "Multiple Mandarin subtitles\n"
                    + "\n".join(
                        f"{zw_i + 1:2d}: {zhongwen_subs.events[zw_i].text}"
                        for zw_i in indexes_over_threshold
                    )
                    + "\noverlap with Cantonese subtitle\n"
                    f"{yw_i + 1:2d}: {yuewen_subs.events[yw_i].text}."
                )
            # When a Cantonese subtitle overlaps with multiple Mandarin subtitles,
            # It may be assigned to either one of them. If this is the case, we should
            # be able to continue processing within this call of this function.
            # However, it is also possible that the Cantonese subtitle needs to be split
            # into two separate subtitles. If that is the case, we must do some fairly
            # complex operations in order to split the Cantonese subtitle into two.
            # It should be possible to do those updates from within the loop, modifying
            # yuewen_subs, nascent_sync_groups (add one to later indexes), and the
            # queue (add one to later indexes).
            # Alternatively, we may just want to have a step before that catalogs the
            # splits that are needed, and then a separate function for actually grouping
            # later. Or maybe one function we call multiple times.

            # Split out into a function that takes the two subtitle series and returns
            # The assignments, as well as the ambiguous sets.
            # Try to fix the ambiguous sets, and then rerun
            # Continue until things make sense

            queue.append(yw_i)

        print("\nOVERLAP:")
        print(get_overlap_string(overlap))

        sync_groups = get_sync_groups(zhongwen_subs, yuewen_subs)
        print(f"\nSYNC GROUPS:\n{pformat(sync_groups, width=120)}")
