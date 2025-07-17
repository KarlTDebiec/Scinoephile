#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to synchronization of subtitles."""

from __future__ import annotations

from copy import deepcopy
from logging import debug
from pprint import pformat

import numpy as np

from scinoephile.core.blocks import get_concatenated_series
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.pairs import get_pair_blocks_by_pause, get_pair_strings
from scinoephile.core.series import Series
from scinoephile.core.subtitle import Subtitle

type SyncGroup = tuple[list[int], list[int]]
"""Group of subtitles; items are indexes in first and second series, respectively."""


def are_series_one_to_one(one: Series, two: Series) -> bool:
    """Check whether two series are one-to-one matched.

    This is useful for preparing test cases, specifically for excluding one-to-one
    mappings, which are simple and not of interest for testing.

    Arguments:
        one: First series to compare
        two: Second series to compare
    Returns:
        Whether all subtitles are one-to-one matches between the two series
    """
    if len(one) != len(two):
        return False

    overlap = get_sync_overlap_matrix(one, two)
    if not np.all(overlap == np.diag(np.diag(overlap))):
        return False

    return True


def get_overlap_string(overlap: np.ndarray) -> str:
    """Get string representation of overlap matrix between two series.

    1-indexed to match SRT.

    Arguments:
        overlap: Overlap matrix
    Returns:
        String representation of overlap matrix
    """
    matrix = np.array2string(
        overlap,
        precision=2,
        suppress_small=True,
        max_line_width=np.inf,
        threshold=np.inf,
        edgeitems=np.inf,
    )
    matrix = matrix.replace("0.  ", "____").replace("[", " ").replace("]", " ")
    columns = [f"{j:>5}" for j in range(1, overlap.shape[1] + 1)]
    lines = ["  " + "".join(columns)]
    for i, row in enumerate(matrix.split("\n")):
        lines += [f"{i + 1:>2}" + row]
    return "\n".join(lines)


def get_sync_groups_string(sync_groups: list[SyncGroup]) -> str:
    """Get a string representation of sync groups.

    Arguments:
        sync_groups: Sync groups to represent
    Returns:
        String representation of the sync groups
    """
    one_indexed_sync_groups = []
    for sync_group in sync_groups:
        one_indexed_group = (
            [i + 1 for i in sync_group[0]],
            [j + 1 for j in sync_group[1]],
        )
        one_indexed_sync_groups.append(one_indexed_group)
    return pformat(one_indexed_sync_groups, width=120, indent=2)


def get_sync_groups(one: Series, two: Series, cutoff: float = 0.16) -> list[SyncGroup]:
    """Distribute subtitles from two series into sync groups based on their overlap.

    Subtitles are grouped based on the overlap between them. Subtitles are treated as
    Gaussians whose centers are the midpoints of their start and end times and whose
    standard deviations are one quarter of their duration. The overlaps between all
    subtitles in the two series are calculated and stored in a matrix whose rows are
    subtitles in the first series and whose columns are subtitles in the second series.
    The matrix is then iteratively pruned by zeroing cells below an increasing cutoff
    value. Within each row, each value is divided by the max value in that row, and if
    the result is less than the cutoff, the cell is zeroed. The same process is then
    repeated for columns. The process repeats with an increasing cutoff until each
    non-zero value in the matrix is either the only value in its row, the only value in
    its column, or both, which provides a clean assignment of subtitles to sync groups.

    The cutoff starts at a minimum value, which defaults to 0.16. This serves as a lower
    bound; if a subtitle in series two overlaps less than this amount with a subtitle
    in series one, it is included without a partner.

    Arguments:
        one: First series
        two: Second series
        cutoff: Initial overlap cutoff used to adjust overlap matrix
    Returns:
        List of sync groups, each of which is a list of two lists of subtitle indexes,
        the first list corresponding to subtitles in series one and the second list
        corresponding to subtitles in series two.
    """
    if len(one) == 0:
        return []
    if len(two) == 0:
        return [([i], []) for i in range(len(one))]

    overlap = get_sync_overlap_matrix(one, two)
    debug(f"OVERLAP:\n{get_overlap_string(overlap)}")

    sync_groups = None
    while True:
        try:
            sync_groups = _get_sync_groups(one, two, overlap.copy(), cutoff)
        except ScinoephileError:
            cutoff += 0.01
            continue
        break

    return sync_groups


def get_sync_overlap_matrix(one: Series, two: Series) -> np.ndarray:
    """Quantify the overlap between two series and compile the results in a matrix.

    Arguments:
        one: First series
        two: Second series
    Returns:
        Two-dimensional array whose rows correspond to subtitle indexes within series
        one, whose columns correspond to subtitle indexes within series two, and whose
        values are the proportion of each subtitle in series two which overlaps with
        each subtitle in series one.
    """
    one_mu = np.array([e.start + (e.end - e.start) / 2 for e in one])
    one_sigma = np.array([(e.end - e.start) / 4 for e in one])
    two_mu = np.array([e.start + (e.end - e.start) / 2 for e in two])
    two_sigma = np.array([(e.end - e.start) / 4 for e in two])

    mu_diff_sq = (one_mu[:, np.newaxis] - two_mu[np.newaxis, :]) ** 2
    sigma_sq_sum = one_sigma[:, np.newaxis] ** 2 + two_sigma[np.newaxis, :] ** 2
    overlap = np.exp(-mu_diff_sq / (2 * sigma_sq_sum))

    return overlap


def get_synced_series(one: Series, two: Series) -> Series:
    """Compile synchonized subtitles from two series.

    Arguments:
        one: First Series
        two: Second Series
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
        one: First series
        two: Second series
        groups: Sync groups including the indexes of subtitles in each series
    Returns:
        Series whose subtitles are composed of the text of the subtitles from the two
        input series as indicated by the sync groups
    """
    synced = Series()

    for group in groups:
        one_events = [one[i] for i in group[0]]
        two_events = [two[i] for i in group[1]]

        # One to zero mapping
        if len(one_events) == 1 and len(two_events) == 0:
            synced.events.append(deepcopy(one_events[0]))
            continue

        # Zero to one mapping
        if len(one_events) == 0 and len(two_events) == 1:
            synced.events.append(deepcopy(two_events[0]))
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
        raise ScinoephileError()

    return synced


def _compare_sync_groups(first: SyncGroup, second: SyncGroup) -> int | None:  # noqa: PLR0912
    """Compare two sync groups.

    Arguments:
        first: First sync group
        second: Second sync group
    Returns:
        -1 if first is less than second, 0 if they are equal, 1 if first is greater,
        and None if they cannot be compared
    """
    first_min_one = min(first[0]) if first[0] else None
    first_min_two = min(first[1]) if first[1] else None
    second_min_one = min(second[0]) if second[0] else None
    second_min_two = min(second[1]) if second[1] else None
    first_order = None
    second_order = None
    if first_min_one is not None and second_min_one is not None:
        if first_min_one < second_min_one:
            first_order = -1
        elif first_min_one > second_min_one:
            first_order = 1
        else:
            first_order = 0
    if first_min_two is not None and second_min_two is not None:
        if first_min_two < second_min_two:
            second_order = -1
        elif first_min_two > second_min_two:
            second_order = 1
        else:
            second_order = 0
    match (first_order, second_order):
        case (None, None):
            return None
        case (None, _):
            return second_order
        case (_, None):
            return first_order
        case (-1, -1):
            return -1
        case (0, 0):
            return 0
        case (1, 1):
            return 1
        case _:
            raise ScinoephileError("Unexpected comparison result between sync groups")


def _get_sync_groups(  # noqa: PLR0912
    one: Series, two: Series, overlap: np.ndarray, cutoff: float
) -> list[SyncGroup]:
    sync_groups = []

    for i in range(len(one)):
        scale = np.max(overlap[i])
        for j in range(len(two)):
            if overlap[i, j] / scale < cutoff:
                overlap[i, j] = 0
    for j in range(len(two)):
        scale = np.max(overlap[:, j])
        if scale > 0:
            for i in range(len(one)):
                if overlap[i, j] / scale < cutoff:
                    overlap[i, j] = 0

    debug(f"OVERLAP ({cutoff:.2f}):\n{get_overlap_string(overlap)}")

    available_is = set(range(len(one)))
    available_js = set(range(len(two)))

    nonzero = np.argwhere(overlap)

    js_that_match_each_i = {}
    for i in range(len(one)):
        js_that_match_each_i[i] = sorted(nonzero[nonzero[:, 0] == i, 1])

    is_that_match_each_j = {}
    for j in range(len(two)):
        is_that_match_each_j[j] = sorted(nonzero[nonzero[:, 1] == j, 0])

    for i, js_that_match_this_i in js_that_match_each_i.items():
        if i not in available_is:
            continue

        # One to zero
        if len(js_that_match_this_i) == 0:
            available_is.remove(i)
            sync_groups.append(([i], []))
            continue

        if len(js_that_match_this_i) == 1:
            j = js_that_match_this_i[0]
            is_that_match_this_j = is_that_match_each_j[j]

            # One to one
            if len(is_that_match_this_j) == 1:
                available_is.remove(i)
                available_js.remove(j)
                sync_groups.append(([i], [j]))
                continue

            # Many to one
            if len(is_that_match_this_j) > 1:
                if not all(i2 in available_is for i2 in is_that_match_this_j):
                    raise ScinoephileError()
                for i2 in is_that_match_this_j:
                    available_is.remove(i2)
                available_js.remove(j)
                sync_groups.append((is_that_match_this_j, [j]))
                continue

        # One to many
        if len(js_that_match_this_i) > 1:
            for j in js_that_match_this_i:
                is_that_match_this_j = is_that_match_each_j[j]
                if len(is_that_match_this_j) != 1:
                    raise ScinoephileError()
            available_is.remove(i)
            for j in js_that_match_this_i:
                available_js.remove(j)
            sync_groups.append(([i], js_that_match_this_i))
            continue

    # Raise exception if there are any remaining subtitles in series one
    if len(available_is) > 0:
        raise ScinoephileError()

    # Add remaining subtitles from series two
    for j in available_js:
        sync_groups.extend([([], [j])])

    # Sort sync groups by their indexes
    sync_groups = _sort_sync_groups(sync_groups)

    return sync_groups


def _sort_sync_groups(sync_groups: list[SyncGroup]) -> list[SyncGroup]:
    """Sort sync groups.

    May not correctly handle all initial orders, but should work for the cases
    encountered.

    Arguments:
        sync_groups: Sync groups to sort
    Returns:
        Sorted sync groups
    """
    sorted_groups = []

    for group in sync_groups:
        inserted = False
        for i in range(len(sorted_groups) + 1):
            # Try inserting at position i
            if i == len(sorted_groups):
                sorted_groups.append(group)
                inserted = True
                break

            result = _compare_sync_groups(group, sorted_groups[i])
            if result is None:
                continue  # Try comparing with the next one
            elif result < 0:
                sorted_groups.insert(i, group)
                inserted = True
                break
        if not inserted:
            raise ScinoephileError(
                "Could not determine correct position for sync group"
            )

    return sorted_groups


__all__ = [
    "SyncGroup",
    "are_series_one_to_one",
    "get_overlap_string",
    "get_sync_groups",
    "get_sync_groups_string",
    "get_sync_overlap_matrix",
    "get_synced_series",
    "get_synced_series_from_groups",
]
