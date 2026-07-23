#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle synchronization group derivation."""

from __future__ import annotations

from logging import getLogger
from pprint import pformat

import numpy as np

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series

from .overlap import get_overlap_string, get_sync_overlap_matrix

__all__ = [
    "SyncGroup",
    "get_sync_groups",
    "get_sync_groups_string",
]

logger = getLogger(__name__)

SyncGroup = tuple[list[int], list[int]]
"""Group of subtitles; items are indexes in first and second series, respectively."""


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
        return [([], [j]) for j in range(len(two))]
    if len(two) == 0:
        return [([i], []) for i in range(len(one))]

    overlap = get_sync_overlap_matrix(one, two)
    logger.debug(f"OVERLAP:\n{get_overlap_string(overlap)}")

    max_cutoff = 1.0
    sync_groups = None
    while True:
        try:
            sync_groups = _get_sync_groups(one, two, overlap.copy(), cutoff)
        except ScinoephileError:
            cutoff += 0.01
            if cutoff > max_cutoff:
                raise ScinoephileError(
                    f"Failed to compute sync groups: cutoff exceeded {max_cutoff}. "
                    f"Final cutoff: {cutoff:.2f}. "
                    f"Overlap matrix shape: {overlap.shape}. "
                    f"This may indicate malformed or incompatible subtitle timing."
                )
            continue
        break

    return sync_groups


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


def _compare_sync_groups(  # noqa: PLR0912
    first: SyncGroup, second: SyncGroup
) -> int | None:
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


def _compare_sync_groups_by_timing(
    one: Series, two: Series, first: SyncGroup, second: SyncGroup
) -> int:
    """Compare two sync groups by subtitle timing.

    Arguments:
        one: First series
        two: Second series
        first: First sync group
        second: Second sync group
    Returns:
        -1 if first is less than second, 0 if they are equal, and 1 if first is
        greater
    """
    first_start, first_end = _get_sync_group_timing(one, two, first)
    second_start, second_end = _get_sync_group_timing(one, two, second)

    if first_start < second_start:
        return -1
    if first_start > second_start:
        return 1
    if first_end < second_end:
        return -1
    if first_end > second_end:
        return 1
    return 0


def _get_sync_group_timing(
    one: Series, two: Series, sync_group: SyncGroup
) -> tuple[int, int]:
    """Get the timing span of a sync group.

    Arguments:
        one: First series
        two: Second series
        sync_group: Sync group
    Returns:
        Start and end times of subtitles in the sync group
    """
    subtitles = [one.events[i] for i in sync_group[0]]
    subtitles.extend(two.events[j] for j in sync_group[1])
    if not subtitles:
        raise ScinoephileError("Cannot sort empty sync group")

    return (
        min(subtitle.start for subtitle in subtitles),
        max(subtitle.end for subtitle in subtitles),
    )


def _get_sync_groups(  # noqa: PLR0912, PLR0915
    one: Series, two: Series, overlap: np.ndarray, cutoff: float
) -> list[SyncGroup]:
    """Build sync groups from a filtered overlap matrix.

    Arguments:
        one: first subtitle series
        two: second subtitle series
        overlap: overlap matrix between series
        cutoff: overlap cutoff used when pruning matrix values
    Returns:
        list of sync groups derived from the overlap matrix
    """
    sync_groups = []

    for i in range(len(one)):
        scale = np.max(overlap[i])
        if scale == 0:
            continue
        for j in range(len(two)):
            if overlap[i, j] / scale < cutoff:
                overlap[i, j] = 0
    for j in range(len(two)):
        scale = np.max(overlap[:, j])
        if scale > 0:
            for i in range(len(one)):
                if overlap[i, j] / scale < cutoff:
                    overlap[i, j] = 0

    logger.debug(f"OVERLAP ({cutoff:.2f}):\n{get_overlap_string(overlap)}")

    available_is = set(range(len(one)))
    available_js = set(range(len(two)))

    nonzero = np.argwhere(overlap)

    js_that_match_each_i = {}
    for i in range(len(one)):
        js_that_match_each_i[i] = [
            int(j) for j in sorted(nonzero[nonzero[:, 0] == i, 1])
        ]

    is_that_match_each_j = {}
    for j in range(len(two)):
        is_that_match_each_j[j] = [
            int(i) for i in sorted(nonzero[nonzero[:, 1] == j, 0])
        ]

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

    # Sort sync groups by indexes, falling back to timing when needed
    sync_groups = _sort_sync_groups(one, two, sync_groups)

    logger.info(f"OVERLAP ({cutoff:.2f}):\n{get_overlap_string(overlap)}")

    return sync_groups


def _sort_sync_groups(
    one: Series, two: Series, sync_groups: list[SyncGroup]
) -> list[SyncGroup]:
    """Sort sync groups.

    May not correctly handle all initial orders, but should work for the cases
    encountered.

    Arguments:
        one: First series
        two: Second series
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
                result = _compare_sync_groups_by_timing(
                    one, two, group, sorted_groups[i]
                )
            if result < 0:
                sorted_groups.insert(i, group)
                inserted = True
                break
        if not inserted:
            raise ScinoephileError(
                "Could not determine correct position for sync group"
            )

    return sorted_groups
