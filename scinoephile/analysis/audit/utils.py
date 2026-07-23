#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared helpers for Markdown subtitle audit reports."""

from __future__ import annotations

from collections.abc import Collection, Hashable, Mapping, MutableSequence, Sequence
from enum import StrEnum
from typing import Literal

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series

__all__ = [
    "AuditColumn",
    "AuditFilter",
    "AuditResult",
    "ChangeAuditFilter",
    "ExtendedAuditFilter",
    "format_audit_report",
    "format_verification_marker",
    "get_contextual_index",
    "get_selected_event_indexes",
    "get_superseded_keys",
    "is_block_in_range",
    "resolve_contextual_index",
    "validate_audit_range",
]

type AuditColumn = tuple[str, Literal["left", "right", "center"]]
"""Semantic label and alignment for one audit report column."""


class AuditFilter(StrEnum):
    """Row filters for audits whose only row state is verification."""

    all = "all"
    """Include every eligible row."""

    unverified = "unverified"
    """Include only rows from cases not marked as verified."""


class AuditResult(StrEnum):
    """Result types shared by decision-log audit rows."""

    changed = "changed"
    """The logged answer changed its input."""

    unchanged = "unchanged"
    """The logged answer explicitly retained its input."""

    unanswered = "unanswered"
    """The logged case has no answer."""


class ChangeAuditFilter(StrEnum):
    """Row filters shared by audit reports that identify changed rows."""

    all = "all"
    """Include every eligible row."""

    changes = "changes"
    """Include only changed rows."""

    unverified = "unverified"
    """Include only rows from unverified logged cases."""


class ExtendedAuditFilter(StrEnum):
    """Row filters for audits that also identify final discrepancies."""

    all = "all"
    """Include every eligible row."""

    changes = "changes"
    """Include rows that the audit classifies as changed."""

    discrepancies = "discrepancies"
    """Include only final discrepancies."""

    unverified = "unverified"
    """Include only rows from unverified logged cases."""


def format_audit_report(
    *,
    title: str,
    summary_items: Sequence[str],
    columns: Sequence[AuditColumn],
    rows: Sequence[Sequence[str]],
    first_index: int | None = None,
    last_index: int | None = None,
    index_track_name: str | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
) -> str:
    """Format the shared structure of a Markdown audit report.

    Arguments:
        title: report title without the Markdown heading marker
        summary_items: report-specific summary text without Markdown list markers
        columns: audit table labels and alignments
        rows: raw audit table cell values
        first_index: first included one-based subtitle index
        last_index: last included one-based subtitle index
        index_track_name: optional name of the indexed subtitle track
        first_block: first included one-based block number
        last_block: last included one-based block number
    Returns:
        formatted Markdown audit report
    Raises:
        ScinoephileError: if subtitle-index and block ranges are both provided
        ValueError: if a column alignment or table row is invalid
    """
    # Validate ranges at the shared output boundary
    validate_audit_range(first_index, last_index, first_block, last_block)

    # Format and validate the table schema
    separators_by_alignment = {
        "left": "---",
        "right": "---:",
        "center": ":---:",
    }
    column_labels = []
    column_separators = []
    for label, alignment in columns:
        separator = separators_by_alignment.get(alignment)
        if separator is None:
            raise ValueError(f"Unsupported table column alignment: {alignment}")
        column_labels.append(_escape_table_cell(label))
        column_separators.append(separator)

    # Escape raw cell values and verify every row matches the schema
    table_rows = []
    for row_number, row in enumerate(rows, 1):
        if len(row) != len(columns):
            raise ValueError(
                f"Table row {row_number} has {len(row)} cells; expected {len(columns)}"
            )
        table_rows.append(f"| {' | '.join(_escape_table_cell(cell) for cell in row)} |")

    # Format the report heading and summary
    lines = [
        f"# {title}",
        "",
        "## Summary",
        "",
        *(f"- {item}" for item in summary_items),
    ]
    index_range = _format_index_range(
        first_index,
        last_index,
        track_name=index_track_name,
    )
    if index_range is not None:
        lines.append(f"- {index_range}")
    block_range = _format_block_range(first_block, last_block)
    if block_range is not None:
        lines.append(f"- {block_range}")
    lines.extend(
        (
            f"- table rows: {len(table_rows)}",
            "",
            "## Audit Table",
            "",
            f"| {' | '.join(column_labels)} |",
            f"|{'|'.join(column_separators)}|",
            *table_rows,
        )
    )
    return "\n".join(lines) + "\n"


def format_verification_marker(verified: bool | None) -> str:
    """Format semantic verification state for an audit table.

    Arguments:
        verified: verification state, or None when verification is unavailable
    Returns:
        check mark, blank text, or em dash
    """
    if verified is None:
        return "—"
    if verified:
        return "✓"
    return ""


def get_contextual_index(
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
        candidates_between_anchors = [
            candidate
            for candidate in candidate_indexes
            if previous_index <= candidate <= next_index
        ]
        if len(candidates_between_anchors) == 1:
            return candidates_between_anchors[0]
        if candidates_between_anchors:
            narrowed_candidates = candidates_between_anchors

    scores: dict[int, tuple[int, int]] = {}
    for candidate in narrowed_candidates:
        distances = []
        if previous_index is not None:
            distances.append(abs(candidate - previous_index))
        if next_index is not None:
            distances.append(abs(candidate - next_index))
        if previous_index is not None and next_index is not None:
            primary_score = sum(distances)
        else:
            primary_score = distances[0]

        previous_distance = 0
        if previous_index is not None:
            previous_distance = abs(candidate - previous_index)
        scores[candidate] = (primary_score, previous_distance)

    minimum_score = min(scores.values())
    best_candidates = [
        candidate for candidate, score in scores.items() if score == minimum_score
    ]
    if len(best_candidates) == 1:
        return best_candidates[0]
    return None


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
    has_block_range = first_block is not None or last_block is not None
    block_indexes = None
    if has_block_range:
        block_indexes = Series.get_block_indexes_by_pause(series)
    block_count = None
    if block_indexes is not None:
        block_count = len(block_indexes)
    validate_audit_range(
        first_index,
        last_index,
        first_block,
        last_block,
        block_count=block_count,
    )

    if not has_block_range:
        start = 0
        if first_index is not None:
            start = first_index - 1
        stop = len(series)
        if last_index is not None:
            stop = min(last_index, stop)
        return frozenset(range(start, stop))

    assert block_indexes is not None
    selected_block_indexes = {
        event_index
        for block_number, (block_start, block_stop) in enumerate(
            block_indexes,
            1,
        )
        if is_block_in_range(block_number, first_block, last_block)
        for event_index in range(block_start, block_stop)
    }
    return frozenset(selected_block_indexes)


def get_superseded_keys[KeyT: Hashable, ValueT: Hashable](
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


def is_block_in_range(
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


def resolve_contextual_index(
    candidate_indexes: Sequence[int],
    resolved_indexes: MutableSequence[int | None],
    test_case_index: int,
) -> int | None:
    """Resolve and memoize one logged case's source index.

    Arguments:
        candidate_indexes: possible zero-indexed source positions
        resolved_indexes: resolved indexes for every logged case
        test_case_index: zero-indexed test case position
    Returns:
        resolved source position, or None if ambiguity remains
    """
    index = resolved_indexes[test_case_index]
    if index is not None:
        return index

    index = get_contextual_index(
        candidate_indexes,
        resolved_indexes,
        test_case_index,
    )
    if index is not None:
        resolved_indexes[test_case_index] = index
    return index


def validate_audit_range(
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
    *,
    block_count: int | None = None,
):
    """Validate mutually exclusive subtitle-index and block ranges.

    Arguments:
        first_index: first included one-based subtitle index
        last_index: last included one-based subtitle index
        first_block: first included one-based block number
        last_block: last included one-based block number
        block_count: optional total number of available blocks
    Raises:
        ScinoephileError: if either range is invalid or both range types are used
    """
    has_index_range = first_index is not None or last_index is not None
    has_block_range = first_block is not None or last_block is not None
    if has_index_range and has_block_range:
        raise ScinoephileError("Subtitle-index and block ranges are mutually exclusive")
    _validate_index_range(first_index, last_index)
    _validate_block_range(first_block, last_block, block_count)


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
        return f"block range: through {last_block}"
    if last_block is None:
        return f"block range: from {first_block}"
    return f"block range: {first_block} through {last_block}"


def _format_index_range(
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
        return f"{range_name} range: through {last_index}"
    if last_index is None:
        return f"{range_name} range: from {first_index}"
    return f"{range_name} range: {first_index} through {last_index}"


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
