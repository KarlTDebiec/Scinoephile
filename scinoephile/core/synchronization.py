#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from copy import deepcopy

import numpy as np

from scinoephile.core import ScinoephileException, Subtitle
from scinoephile.core.subtitle_series import SubtitleSeries

SyncGroup = list[list[int], list[int]]
SyncGroupList = list[SyncGroup]


def are_series_one_to_one(one: SubtitleSeries, two: SubtitleSeries) -> bool:
    if len(one.events) != len(two.events):
        return False

    one_to_two_overlap = get_sync_overlap_matrix(one, two)
    if not np.all(one_to_two_overlap == np.diag(np.diag(one_to_two_overlap))):
        return False

    two_to_one_overlap = get_sync_overlap_matrix(two, one)
    if not np.all(two_to_one_overlap == np.diag(np.diag(two_to_one_overlap))):
        return False

    return True


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


def get_sync_overlap_matrix_gaussian(
    one: SubtitleSeries, two: SubtitleSeries
) -> np.ndarray:
    one_mu = np.array([e.start + (e.end - e.start) / 2 for e in one.events])
    one_sigma = np.array([(e.end - e.start) / 4 for e in one.events])
    two_mu = np.array([e.start + (e.end - e.start) / 2 for e in two.events])
    two_sigma = np.array([(e.end - e.start) / 4 for e in two.events])

    mu_diff_sq = (one_mu[:, np.newaxis] - two_mu[np.newaxis, :]) ** 2
    sigma_sq_sum = one_sigma[:, np.newaxis] ** 2 + two_sigma[np.newaxis, :] ** 2
    overlap = np.exp(-mu_diff_sq / (2 * sigma_sq_sum))

    return overlap


def get_sync_groups_gaussian(one: SubtitleSeries, two: SubtitleSeries) -> SyncGroupList:
    sync_groups = []

    if len(one.events) == 0:
        return []
    if len(two.events) == 0:
        return [[[i], []] for i in range(len(one.events))]

    overlap = get_sync_overlap_matrix_gaussian(one, two)

    # print()
    # print(get_overlap_string(overlap))

    cutoff = 0.16
    for i in range(len(one.events)):
        scale = np.max(overlap[i])
        for j in range(len(two.events)):
            if overlap[i, j] / scale < cutoff:
                overlap[i, j] = 0

    # print()
    # print(get_overlap_string(overlap))

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

    # Add 1 to all indexes
    for sync_group in sync_groups:
        sync_group[0] = sorted([i + 1 for i in sync_group[0]])
        sync_group[1] = sorted([j + 1 for j in sync_group[1]])

    return sync_groups


def get_sync_groups(one: SubtitleSeries, two: SubtitleSeries) -> SyncGroupList:
    sync_groups = []

    if len(one.events) == 0:
        return []
    if len(two.events) == 0:
        return [[[i], []] for i in range(len(one.events))]

    one_to_two_overlap = get_sync_overlap_matrix(one, two)
    two_to_one_overlap = get_sync_overlap_matrix(two, one)

    # print()
    # print(get_overlap_string(one_to_two_overlap))
    # print(get_overlap_string(two_to_one_overlap.transpose()))

    # one_to_two_overlap[one_to_two_overlap < 0.07] = 0
    # two_to_one_overlap[two_to_one_overlap < 0.07] = 0
    cutoff = 0.30
    for i, row in enumerate(one_to_two_overlap):
        scale = np.max(row)
        for j, value in enumerate(row):
            if value == 0:
                continue
            if value / scale < cutoff:
                one_to_two_overlap[i, j] = 0
                two_to_one_overlap[j, i] = 0
    for j, row in enumerate(two_to_one_overlap):
        scale = np.max(row)
        for i, value in enumerate(row):
            if value == 0:
                continue
            if value / scale < cutoff:
                one_to_two_overlap[i, j] = 0
                two_to_one_overlap[j, i] = 0

    # print()
    # print(get_overlap_string(one_to_two_overlap))
    # print(get_overlap_string(two_to_one_overlap.transpose()))

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


def get_synced_subtitles(
    one: SubtitleSeries,
    two: SubtitleSeries,
    groups: SyncGroupList,
) -> SubtitleSeries:
    synced = SubtitleSeries()

    for group in groups:
        one_events = [one.events[i - 1] for i in group[0]]
        two_events = [two.events[i - 1] for i in group[1]]

        # One-to-zero mapping
        if len(one_events) == 1 and len(two_events) == 0:
            synced.events.append(deepcopy(one_events[0]))
            continue

        # One-to-one mapping
        if len(one_events) == 1 and len(two_events) == 1:
            synced_event = deepcopy(one_events[0])
            synced_event.text = f"{one_events[0].text}\n{two_events[0].text}"
            synced.events.append(synced_event)
            continue

        # Multiple one to one two
        if len(one_events) > 1 and len(two_events) == 1:
            two_text = two_events[0].text
            start = one_events[0].start
            end = one_events[-1].end
            edges = np.linspace(start, end, len(one_events) + 1, dtype=int)

            for event, start, end in zip(one_events, edges[:-1], edges[1:]):
                text = f"{event.text}\n{two_text}"
                synced.events.append(Subtitle(start=start, end=end, text=text))
            continue

        # One one to multiple two
        if len(one_events) == 1 and len(two_events) > 1:
            one_text = one_events[0].text
            start = two_events[0].start
            end = two_events[-1].end
            edges = np.linspace(start, end, len(two_events) + 1, dtype=int)

            for event, start, end in zip(two_events, edges[:-1], edges[1:]):
                text = f"{one_text}\n{event.text}"
                synced.events.append(Subtitle(start=start, end=end, text=text))
            continue

        raise ScinoephileException()

    return synced


def get_overlap_string(overlap):
    return np.array2string(
        overlap, precision=2, suppress_small=True, max_line_width=160
    ).replace("0.  ", "____")
