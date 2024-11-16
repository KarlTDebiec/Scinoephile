#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to synchronization of subtitles."""
from __future__ import annotations

from copy import deepcopy

import numpy as np

from scinoephile.core.exceptions import ScinoephileException
from scinoephile.core.pairs import get_pair_blocks_by_pause
from scinoephile.core.series import Series
from scinoephile.core.subtitle import Subtitle

SyncGroup = list[list[int], list[int]]
SyncGroupList = list[SyncGroup]


def are_series_one_to_one(one: Series, two: Series) -> bool:
    if len(one.events) != len(two.events):
        return False

    overlap = get_sync_overlap_matrix(one, two)
    if not np.all(overlap == np.diag(np.diag(overlap))):
        return False

    return True


def get_merged_series(blocks: list[Series]) -> Series:
    merged = Series()
    for block in blocks:
        merged.events.extend(block.events)
    merged.events.sort(key=lambda x: x.start)
    return merged


def get_sync_overlap_matrix(one: Series, two: Series) -> np.ndarray:
    """Get a matrix of the overlap between two series, modeled as Gaussians.

    Arguments:
        one: First subtitle series
        two: Second subtitle series
    Returns:
        Two-dimensional array whose rows correspond to subtitle indexes within series
        one, whose columns correspond to subtitle indexes within series two, and whose
        values are the proportion of each subtitle in series two which overlaps with
        each subtitle in series one.
    """
    one_mu = np.array([e.start + (e.end - e.start) / 2 for e in one.events])
    one_sigma = np.array([(e.end - e.start) / 4 for e in one.events])
    two_mu = np.array([e.start + (e.end - e.start) / 2 for e in two.events])
    two_sigma = np.array([(e.end - e.start) / 4 for e in two.events])

    mu_diff_sq = (one_mu[:, np.newaxis] - two_mu[np.newaxis, :]) ** 2
    sigma_sq_sum = one_sigma[:, np.newaxis] ** 2 + two_sigma[np.newaxis, :] ** 2
    overlap = np.exp(-mu_diff_sq / (2 * sigma_sq_sum))

    return overlap


def get_sync_groups(one: Series, two: Series) -> SyncGroupList:
    if len(one.events) == 0:
        return []
    if len(two.events) == 0:
        return [[[i], []] for i in range(len(one.events))]

    def get_groups_for_cutoff(overlap: np.ndarray, cutoff: float) -> SyncGroupList:
        sync_groups = []

        for i in range(len(one.events)):
            scale = np.max(overlap[i])
            for j in range(len(two.events)):
                if overlap[i, j] / scale < cutoff:
                    overlap[i, j] = 0
        for j in range(len(two.events)):
            scale = np.max(overlap[:, j])
            for i in range(len(one.events)):
                if overlap[i, j] / scale < cutoff:
                    overlap[i, j] = 0

        # print()
        # print(get_overlap_string(overlap))

        available_is = set(range(len(one.events)))
        available_js = set(range(len(two.events)))

        nonzero = np.argwhere(overlap)

        js_that_match_each_i = {}
        for i in range(len(one.events)):
            js_that_match_each_i[i] = sorted(nonzero[nonzero[:, 0] == i, 1])

        is_that_match_each_j = {}
        for j in range(len(two.events)):
            is_that_match_each_j[j] = sorted(nonzero[nonzero[:, 1] == j, 0])

        for i, js_that_match_this_i in js_that_match_each_i.items():
            if i not in available_is:
                continue

            # One to zero
            if len(js_that_match_this_i) == 0:
                sync_group = [[i], []]
                available_is.remove(i)
                sync_groups.append(sync_group)
                continue

            if len(js_that_match_this_i) == 1:
                j = js_that_match_this_i[0]
                is_that_match_this_i = is_that_match_each_j[j]

                # One to one
                if len(is_that_match_this_i) == 1:
                    sync_group = [[i], [j]]
                    available_is.remove(i)
                    available_js.remove(j)
                    sync_groups.append(sync_group)
                    continue

                # Many to one
                if len(is_that_match_this_i) > 1:
                    sync_group = [is_that_match_this_i, [j]]
                    for i2 in is_that_match_this_i:
                        available_is.remove(i2)
                    available_js.remove(j)
                    sync_groups.append(sync_group)
                    continue

            # One to many
            if len(js_that_match_this_i) > 1:
                for j in js_that_match_this_i:
                    is_that_match_this_j = is_that_match_each_j[j]
                    if len(is_that_match_this_j) != 1:
                        raise ScinoephileException()
                sync_group = [[i], js_that_match_this_i]
                available_is.remove(i)
                for j in js_that_match_this_i:
                    available_js.remove(j)
                sync_groups.append(sync_group)
                continue

        if len(available_is) > 0:
            raise ScinoephileException()

        return sync_groups

    overlap = get_sync_overlap_matrix(one, two)

    # print()
    # print(get_overlap_string(overlap))

    cutoff = 0.16
    while True:
        try:
            # print(cutoff)
            sync_groups = get_groups_for_cutoff(overlap.copy(), cutoff)
        except:
            cutoff += 0.01
            continue
        break

    # Add 1 to all indexes
    for sync_group in sync_groups:
        sync_group[0] = sorted([i + 1 for i in sync_group[0]])
        sync_group[1] = sorted([j + 1 for j in sync_group[1]])

    return sync_groups


def get_synced_series(one: Series, two: Series) -> Series:
    synced_blocks = []

    pair_blocks = get_pair_blocks_by_pause(one, two)
    for one_block, two_block in pair_blocks:
        groups = get_sync_groups(one_block, two_block)
        synced_block = get_synced_series_from_groups(one_block, two_block, groups)
        synced_blocks.append(synced_block)

    synced = get_merged_series(synced_blocks)
    return synced


def get_synced_series_from_groups(
    one: Series,
    two: Series,
    groups: SyncGroupList,
) -> Series:
    synced = Series()

    for group in groups:
        one_events = [one.events[i - 1] for i in group[0]]
        two_events = [two.events[i - 1] for i in group[1]]

        # One to zero mapping
        if len(one_events) == 1 and len(two_events) == 0:
            synced.events.append(deepcopy(one_events[0]))
            continue

        # One to one mapping
        if len(one_events) == 1 and len(two_events) == 1:
            synced_event = deepcopy(one_events[0])
            synced_event.text = f"{one_events[0].text}\n{two_events[0].text}"
            synced.events.append(synced_event)
            continue

        # Many to one mapping
        if len(one_events) > 1 and len(two_events) == 1:
            two_text = two_events[0].text
            start = one_events[0].start
            end = one_events[-1].end
            edges = np.linspace(start, end, len(one_events) + 1, dtype=int)

            for event, start, end in zip(one_events, edges[:-1], edges[1:]):
                text = f"{event.text}\n{two_text}"
                synced.events.append(Subtitle(start=start, end=end, text=text))
            continue

        # One to many mapping
        if len(one_events) == 1 and len(two_events) > 1:
            one_text = one_events[0].text
            start = two_events[0].start
            end = two_events[-1].end
            edges = np.linspace(start, end, len(two_events) + 1, dtype=int)

            for event, start, end in zip(two_events, edges[:-1], edges[1:]):
                text = f"{one_text}\n{event.text}"
                synced.events.append(Subtitle(start=start, end=end, text=text))
            continue

        # Anything else is unsupported
        raise ScinoephileException()

    return synced


def get_overlap_string(overlap):
    return np.array2string(
        overlap, precision=2, suppress_small=True, max_line_width=160
    ).replace("0.  ", "____")
