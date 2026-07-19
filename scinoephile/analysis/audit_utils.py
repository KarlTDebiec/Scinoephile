#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared helpers for Markdown subtitle audit reports."""

from __future__ import annotations

from collections.abc import Collection, Hashable, Mapping, Sequence
from enum import StrEnum

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series


class _AuditResult(StrEnum):
    """Result types shared by decision-log audit rows."""

    changed = "changed"
    """The logged answer changed its input."""

    unchanged = "unchanged"
    """The logged answer explicitly retained its input."""

    unanswered = "unanswered"
    """The logged case has no answer."""


def _escape_table_cell(value: str) -> str:
    """Escape one Markdown table cell.

    Arguments:
        value: cell text
    Returns:
        escaped cell text
    """
    return value.replace("\\N", "\n").replace("\n", "<br>").replace("|", "\\|")


def _format_block_range(
    first_block: int | None,
    last_block: int | None,
) -> str | None:
    """Format an optional block range for a report summary.

    Arguments:
        first_block: first included one-based block number
        last_block: last included one-based block number
    Returns:
        formatted block-range summary, or None if the range is unbounded
    """
    if first_block is None and last_block is None:
        return None
    if first_block is None:
        return f"- block range: through {last_block}"
    if last_block is None:
        return f"- block range: from {first_block}"
    return f"- block range: {first_block} through {last_block}"


def _format_difficulty_filter(difficulties: Sequence[int]) -> str:
    """Format an exact difficulty filter for a report summary.

    Arguments:
        difficulties: selected exact difficulty levels
    Returns:
        formatted difficulty-filter summary
    """
    if not difficulties:
        return "- difficulty filter: all"
    return f"- difficulty filter: {', '.join(str(value) for value in difficulties)}"


def _format_index_range(
    first_index: int | None,
    last_index: int | None,
    *,
    track_name: str,
) -> str | None:
    """Format an optional subtitle range for a report summary.

    Arguments:
        first_index: first included one-based subtitle index
        last_index: last included one-based subtitle index
        track_name: name of the subtitle track whose indexes are selected
    Returns:
        formatted range summary, or None if the range is unbounded
    """
    if first_index is None and last_index is None:
        return None
    if first_index is None:
        return f"- {track_name} subtitle range: through {last_index}"
    if last_index is None:
        return f"- {track_name} subtitle range: from {first_index}"
    return f"- {track_name} subtitle range: {first_index} through {last_index}"


def _get_contextual_index(
    candidate_indexes: Sequence[int],
    direct_indexes: Sequence[int | None],
    test_case_index: int,
) -> int | None:
    """Resolve a repeated source key from neighboring logged cases.

    Arguments:
        candidate_indexes: possible zero-indexed source positions
        direct_indexes: directly resolved indexes for every logged case
        test_case_index: zero-indexed test case position
    Returns:
        uniquely resolved source position, or None if ambiguity remains
    """
    previous_index = next(
        (
            index
            for index in reversed(direct_indexes[:test_case_index])
            if index is not None
        ),
        None,
    )
    next_index = next(
        (index for index in direct_indexes[test_case_index + 1 :] if index is not None),
        None,
    )
    if previous_index is None and next_index is None:
        return None

    narrowed_candidates = list(candidate_indexes)
    if (
        previous_index is not None
        and next_index is not None
        and previous_index <= next_index
    ):
        narrowed_candidates = [
            candidate
            for candidate in candidate_indexes
            if previous_index <= candidate <= next_index
        ]
        if len(narrowed_candidates) == 1:
            return narrowed_candidates[0]
        if not narrowed_candidates:
            return None

    scores: dict[int, int] = {}
    for candidate in narrowed_candidates:
        distances = []
        if previous_index is not None:
            distances.append(abs(candidate - previous_index))
        if next_index is not None:
            distances.append(abs(candidate - next_index))
        if previous_index is not None and next_index is not None:
            if previous_index <= next_index:
                scores[candidate] = sum(distances)
            else:
                scores[candidate] = min(distances)
        else:
            scores[candidate] = distances[0]

    minimum_score = min(scores.values())
    best_candidates = [
        candidate for candidate, score in scores.items() if score == minimum_score
    ]
    if len(best_candidates) == 1:
        return best_candidates[0]
    return None


def _get_paired_event_block_numbers(
    block_pairs: Sequence[tuple[Series, Series]],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Get paired workflow block numbers for two subtitle series.

    Arguments:
        block_pairs: paired subtitle workflow blocks
    Returns:
        one-based paired block number for every event in each series
    """
    one_block_numbers: list[int] = []
    two_block_numbers: list[int] = []
    for block_number, (one_block, two_block) in enumerate(block_pairs, 1):
        one_block_numbers.extend([block_number] * len(one_block))
        two_block_numbers.extend([block_number] * len(two_block))
    return tuple(one_block_numbers), tuple(two_block_numbers)


def _get_selected_event_indexes(
    series: Series,
    *,
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
) -> frozenset[int]:
    """Get event indexes selected by optional subtitle and block ranges.

    Arguments:
        series: subtitle series whose event and block indexes are selected
        first_index: first included one-based subtitle index
        last_index: last included one-based subtitle index
        first_block: first included one-based block number
        last_block: last included one-based block number
    Returns:
        selected zero-based event indexes
    """
    start = 0
    if first_index is not None:
        start = first_index - 1
    stop = len(series)
    if last_index is not None:
        stop = min(last_index, stop)
    selected_indexes = set(range(start, stop))

    block_indexes = Series.get_block_indexes_by_pause(series)
    _validate_block_range(first_block, last_block, len(block_indexes))

    if first_block is None and last_block is None:
        return frozenset(selected_indexes)

    selected_block_indexes = {
        event_index
        for block_number, (block_start, block_stop) in enumerate(
            block_indexes,
            1,
        )
        if (first_block is None or block_number >= first_block)
        and (last_block is None or block_number <= last_block)
        for event_index in range(block_start, block_stop)
    }
    return frozenset(selected_indexes & selected_block_indexes)


def _get_validated_block_pairs_by_pause(
    one: Series,
    two: Series,
    first_block: int | None,
    last_block: int | None,
) -> list[tuple[Series, Series]]:
    """Get paired workflow blocks and validate a range against their count.

    Arguments:
        one: first subtitle series
        two: second subtitle series
        first_block: first included one-based block number
        last_block: last included one-based block number
    Returns:
        paired workflow blocks
    Raises:
        ScinoephileError: if the requested range exceeds the available blocks
    """
    block_pairs = get_block_pairs_by_pause(one, two)
    _validate_block_range(first_block, last_block, len(block_pairs))
    return block_pairs


def _get_superseded_keys[KeyT: Hashable, ValueT: Hashable](
    current_keys: Collection[KeyT],
    values_by_key: Mapping[KeyT, Collection[ValueT]],
) -> set[KeyT]:
    """Get historical keys directly replaced by current logged cases.

    A historical key is superseded only when one of its logged values also
    appears under a current key. Avoid transitive propagation because a reused
    historical key may otherwise connect unrelated cases.

    Arguments:
        current_keys: keys present in the current source data
        values_by_key: logged target values grouped by source key
    Returns:
        absent keys directly connected to a current key by a shared value
    """
    current_values = {
        value for key in current_keys for value in values_by_key.get(key, ())
    }
    return {
        key
        for key, values in values_by_key.items()
        if key not in current_keys and not current_values.isdisjoint(values)
    }


def _is_block_in_range(
    block_number: int,
    first_block: int | None,
    last_block: int | None,
) -> bool:
    """Check whether a one-based block number is selected.

    Arguments:
        block_number: one-based block number
        first_block: first included block number
        last_block: last included block number
    Returns:
        whether the block is selected
    """
    return (first_block is None or block_number >= first_block) and (
        last_block is None or block_number <= last_block
    )


def _validate_block_range(
    first_block: int | None,
    last_block: int | None,
    block_count: int | None = None,
):
    """Validate optional one-based block boundaries.

    Arguments:
        first_block: first included block number
        last_block: last included block number
        block_count: number of available workflow blocks, if known
    Raises:
        ScinoephileError: if either boundary is invalid
    """
    if first_block is not None and first_block < 1:
        raise ScinoephileError("First block must be at least 1")
    if last_block is not None and last_block < 1:
        raise ScinoephileError("Last block must be at least 1")
    if first_block is not None and last_block is not None and first_block > last_block:
        raise ScinoephileError("First block must be less than or equal to last block")
    if block_count is None:
        return
    if first_block is not None and first_block > block_count:
        raise ScinoephileError(
            f"First block must not exceed available block count {block_count}"
        )
    if last_block is not None and last_block > block_count:
        raise ScinoephileError(
            f"Last block must not exceed available block count {block_count}"
        )


def _validate_index_range(first_index: int | None, last_index: int | None):
    """Validate optional one-based index boundaries.

    Arguments:
        first_index: first included subtitle index
        last_index: last included subtitle index
    Raises:
        ScinoephileError: if either boundary is invalid
    """
    if first_index is not None and first_index < 1:
        raise ScinoephileError("First index must be at least 1")
    if last_index is not None and last_index < 1:
        raise ScinoephileError("Last index must be at least 1")
    if first_index is not None and last_index is not None and first_index > last_index:
        raise ScinoephileError("First index must be less than or equal to last index")
