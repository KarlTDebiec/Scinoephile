#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to synchronization of subtitles."""
from __future__ import annotations

from copy import deepcopy
from logging import debug
from pprint import pformat

import numpy as np

from scinoephile.core.exceptions import ScinoephileException
from scinoephile.core.pairs import get_pair_blocks_by_pause, get_pair_strings
from scinoephile.core.series import Series
from scinoephile.core.subtitle import Subtitle

SyncGroup = list[list[int], list[int]]


def are_series_one_to_one(one: Series, two: Series) -> bool:
    """Check whether two series are one-to-one matched.

    Arguments:
        one: first series to compare
        two: second series to compare
    Returns:
        Whether all subtitles are one-to-one matches between the two series
    """
    if len(one.events) != len(two.events):
        return False

    overlap = get_sync_overlap_matrix(one, two)
    if not np.all(overlap == np.diag(np.diag(overlap))):
        return False

    return True


def get_concatenated_series(blocks: list[Series]) -> Series:
    """Contatenate a list of sequential series blocks into a single series.

    Arguments:
        blocks: series to merge
    Returns:
        Merged series
    """
    merged = Series()
    for block in blocks:
        merged.events.extend(block.events)
    merged.events.sort(key=lambda x: x.start)
    return merged


def get_sync_overlap_matrix(one: Series, two: Series) -> np.ndarray:
    """Quantify the overlap between two series and compile the results in a matrix.

    Arguments:
        one: first series
        two: second series
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


def _get_sync_groups(
    one: Series, two: Series, overlap: np.ndarray, cutoff: float
) -> list[SyncGroup]:
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

    print(f"OVERLAP ({cutoff:.2f}):\n{get_overlap_string(overlap, 1000)}")

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
            is_that_match_this_j = is_that_match_each_j[j]

            # One to one
            if len(is_that_match_this_j) == 1:
                sync_group = [[i], [j]]
                available_is.remove(i)
                available_js.remove(j)
                sync_groups.append(sync_group)
                continue

            # Many to one
            if len(is_that_match_this_j) > 1:
                if not all(i2 in available_is for i2 in is_that_match_this_j):
                    raise ScinoephileException()
                sync_group = [is_that_match_this_j, [j]]
                for i2 in is_that_match_this_j:
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


def get_sync_groups(one: Series, two: Series, cutoff: float = 0.16) -> list[SyncGroup]:
    """Distribute subtitles from two series into sync groups based on their overlap.

    Subtitles are grouped based on the overlap between them. Subtitles are treated as
    Gaussians whose centers are the midpoints of their start and end times and whose
    standard deviations are one quarter of their duration. The overlaps between all
    subtitles in the two series are calculated and stored in a matrix whose rows are
    subtitles in the first series and whose columns are subtitles in the second series.
    The matrix is then iteratively pruned using an increasing cutoff value. Within each
    row, each value is divided by the max value in that row, and if that is less than
    the cutoff, it is set to zero. The same process is then repeated for columns. The
    process repeats with an increasing cutoff until each non-zero value in the
    matrix is either the only value in its row, the only value in its column, or both,
    which provides a clean assignment of subtitles to sync groups.

    The cutoff starts at a minimum value, which defaults to 0.16. This serves as a lower
    bound; if a subtitle in series two overlaps less than this amount with a subtitle
    in series one, it is simply dropped.

    Arguments:
        one: first series
        two: second series
        cutoff: initial overlap cutoff used to adjust overlap matrix
    Returns:
        List of sync groups, each of which is a list of two lists of subtitle indexes,
        the first list corresponding to subtitles in series one and the second list
        corresponding to subtitles in series two.
    """
    if len(one.events) == 0:
        return []
    if len(two.events) == 0:
        return [[[i], []] for i in range(len(one.events))]

    overlap = get_sync_overlap_matrix(one, two)
    print(f"OVERLAP:\n{get_overlap_string(overlap,1000)}")

    while True:
        try:
            sync_groups = _get_sync_groups(one, two, overlap.copy(), cutoff)
        except ScinoephileException:
            cutoff += 0.01
            continue
        break

    # Add 1 to all indexes
    for sync_group in sync_groups:
        sync_group[0] = sorted([i + 1 for i in sync_group[0]])
        sync_group[1] = sorted([j + 1 for j in sync_group[1]])

    return sync_groups


def get_synced_series(one: Series, two: Series) -> Series:
    """Compile synchonized subtitles from two series.

    Arguments:
        one: first Series
        two: second Series
    Returns:
        Synchonized subtitles
    """
    synced_blocks = []

    pair_blocks = get_pair_blocks_by_pause(one, two)
    for one_block, two_block in pair_blocks:
        hanzi_str, english_str = get_pair_strings(one_block, two_block)
        debug(f"ONE:\n{hanzi_str}")
        debug(f"TWO:\n{english_str}")

        groups = get_sync_groups(one_block, two_block)
        debug(f"SYNC GROUPS:\n{pformat(groups, width=1000)}")

        synced_block = get_synced_series_from_groups(one_block, two_block, groups)
        debug(f"SYNCED SUBTITLES:\n{synced_block.to_simple_string()}")
        synced_blocks.append(synced_block)

    synced = get_concatenated_series(synced_blocks)
    return synced


def get_synced_series_from_groups(
    one: Series,
    two: Series,
    groups: list[SyncGroup],
) -> Series:
    """Compile synchronized subtitles from two series based on sync groups.

    Arguments:
        one: first series
        two: second series
        groups: sync groups including the indexes of subtitles in each series
    Returns:
        Series whose subtitles are composed of the text of the subtitles from the two
        input series as indicated by the sync groups
    """
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


def get_overlap_string(overlap: np.ndarray, max_line_width: int = 160) -> str:
    """Get a string representation of the overlap matrix between two series.

    Arguments:
        overlap: overlap matrix
        max_line_width: Maximum width of the returned string
    Returns:
        string representation of the overlap matrix
    """
    return np.array2string(
        overlap,
        precision=2,
        suppress_small=True,
        max_line_width=max_line_width,
        threshold=np.inf,
        edgeitems=np.inf,
    ).replace("0.  ", "____")
