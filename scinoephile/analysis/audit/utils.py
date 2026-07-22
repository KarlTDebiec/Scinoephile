#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared helpers for Markdown subtitle audit reports."""

from __future__ import annotations

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series

__all__ = [
    "escape_table_cell",
    "format_block_range",
    "format_index_range",
    "get_selected_event_indexes",
    "validate_block_range",
    "validate_index_range",
]


def escape_table_cell(value: str) -> str:
    """Escape one Markdown table cell.

    Arguments:
        value: cell text
    Returns:
        escaped cell text
    """
    return value.replace("\\N", "\n").replace("\n", "<br>").replace("|", "\\|")


def format_block_range(
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


def format_index_range(
    first_index: int | None,
    last_index: int | None,
    *,
    track_name: str | None = None,
) -> str | None:
    """Format an optional subtitle range for a report summary.

    Arguments:
        first_index: first included one-based subtitle index
        last_index: last included one-based subtitle index
        track_name: optional name of the subtitle track whose indexes are selected
    Returns:
        formatted range summary, or None if the range is unbounded
    """
    if first_index is None and last_index is None:
        return None
    range_name = "subtitle"
    if track_name is not None:
        range_name = f"{track_name} subtitle"
    if first_index is None:
        return f"- {range_name} range: through {last_index}"
    if last_index is None:
        return f"- {range_name} range: from {first_index}"
    return f"- {range_name} range: {first_index} through {last_index}"


def get_selected_event_indexes(
    series: Series,
    *,
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
) -> frozenset[int]:
    """Get event indexes selected by a subtitle-index or block range.

    Arguments:
        series: subtitle series whose event and block indexes are selected
        first_index: first included one-based subtitle index, if filtering by index
        last_index: last included one-based subtitle index, if filtering by index
        first_block: first included one-based block number, if filtering by block
        last_block: last included one-based block number, if filtering by block
    Returns:
        selected zero-based event indexes
    Raises:
        ScinoephileError: if selection ranges are invalid or mixed
    """
    has_index_range = first_index is not None or last_index is not None
    has_block_range = first_block is not None or last_block is not None
    if has_index_range and has_block_range:
        raise ScinoephileError("Subtitle-index and block ranges are mutually exclusive")
    validate_index_range(first_index, last_index)

    if not has_block_range:
        start = 0
        if first_index is not None:
            start = first_index - 1
        stop = len(series)
        if last_index is not None:
            stop = min(last_index, stop)
        return frozenset(range(start, stop))

    block_indexes = Series.get_block_indexes_by_pause(series)
    validate_block_range(first_block, last_block, len(block_indexes))
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
    return frozenset(selected_block_indexes)


def validate_block_range(
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


def validate_index_range(first_index: int | None, last_index: int | None):
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
