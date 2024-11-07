#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

import numpy as np

from scinoephile.core import ScinoephileException
from scinoephile.core.subtitle_series import SubtitleSeries

SyncGroup = list[list[int], list[int]]
SyncGroupList = list[SyncGroup]


def get_sync_overlap_matrix(one: SubtitleSeries, two: SubtitleSeries) -> np.ndarray:
    """Get a matrix of the proprtions of each subtitle in one series with another.

    Arguments:
        one: First subtitle series
        two: Second subtitle series
    Returns:
        Two-dimensional array whose rows correspond to subtitle indexes within series
        one, whose columns correspond to subtitle indexes within series two, and whose
        values are the proportion of each subtitle in series two which overlaps with
        each subtitle in series one.
    """
    overlap_matrix = np.zeros((len(one.events), len(two.events)), dtype=float)

    for i, one_event in enumerate(one.events):
        one_duration = one_event.end - one_event.start

        for j, two_event in enumerate(two.events):
            overlap_start = max(one_event.start, two_event.start)
            overlap_end = min(one_event.end, two_event.end)
            overlap_duration = max(0, overlap_end - overlap_start)

            if overlap_duration > 0:
                overlap_matrix[i, j] = overlap_duration / one_duration

    return overlap_matrix


def get_sync_groups(one: SubtitleSeries, two: SubtitleSeries) -> SyncGroupList:
    sync_groups = []

    one_to_two_overlap = get_sync_overlap_matrix(one, two)
    two_to_one_overlap = get_sync_overlap_matrix(two, one)

    one_to_two_overlap[one_to_two_overlap < 0.07] = 0
    two_to_one_overlap[two_to_one_overlap < 0.07] = 0

    one_available = set(range(len(one_to_two_overlap)))
    two_available = set(range(len(two_to_one_overlap)))

    for i in range(len(one_to_two_overlap)):
        if i not in one_available:
            continue
        one_row_i = one_to_two_overlap[i]

        # one[i] overlaps with no twos
        if sum(one_row_i != 0) == 0:
            one_available.remove(i)
            sync_groups.append([[i], []])
            continue

        # one[i] overlaps with only two[j]
        if sum(one_row_i != 0) == 1:
            j = one_row_i.argmax()

            if j not in two_available:
                raise ScinoephileException()

            # two[j] also overlaps only with one[i]
            if sum(two_to_one_overlap[j] != 0) == 1:
                if two_to_one_overlap[j].argmax() == i:
                    one_available.remove(i)
                    two_available.remove(j)
                    sync_groups.append([[i], [j]])
                    continue

            # [two[j]] overlaps with both one[i] and another one
            if sum(two_to_one_overlap[j] != 0) == 2:
                i2 = (set(np.argsort(two_to_one_overlap[j])[-2:]) - {i}).pop()
                if sum(one_to_two_overlap[i2] != 0) == 1:
                    if one_to_two_overlap[i2].argmax() == j:
                        one_available.remove(i)
                        one_available.remove(i2)
                        two_available.remove(j)
                        sync_groups.append([[i, i2], [j]])
                        continue

            # [two[j]] overlaps with both one[i] and two other ones
            if sum(two_to_one_overlap[j] != 0) == 3:
                i2, i3 = set(np.argsort(two_to_one_overlap[j])[-3:]) - {i}
                if sum(one_to_two_overlap[i2] != 0) == 1:
                    if one_to_two_overlap[i2].argmax() == j:
                        if sum(one_to_two_overlap[i3] != 0) == 1:
                            if one_to_two_overlap[i3].argmax() == j:
                                one_available.remove(i)
                                one_available.remove(i2)
                                one_available.remove(i3)
                                two_available.remove(j)
                                sync_groups.append([[i, i2, i3], [j]])
                                continue

        raise ScinoephileException()

    if len(one_available) > 0:
        raise ScinoephileException()

    # Add 1 to all indexes
    for sync_group in sync_groups:
        sync_group[0] = [i + 1 for i in sync_group[0]]
        sync_group[1] = [j + 1 for j in sync_group[1]]

    return sync_groups
