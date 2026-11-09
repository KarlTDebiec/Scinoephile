#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit subtitle review workflows and format the results as Markdown."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from scinoephile.core import ScinoephileError

from .review_filters import ReviewAuditFilter, ReviewAuditFilterGroup
from .review_inputs import ReviewAuditBeforeAfterPair, ReviewAuditSeriesPair
from .review_metadata import get_review_audit_metadata
from .utils import (
    AuditColumn,
    format_audit_report,
    format_verification_marker,
    get_event_indexes_in_range,
)

__all__ = ["audit_review"]


def audit_review(
    *,
    reviews: Sequence[ReviewAuditBeforeAfterPair],
    comparisons: Sequence[ReviewAuditSeriesPair] = (),
    filters: ReviewAuditFilterGroup = ReviewAuditFilterGroup(),
) -> str:
    """Audit a composition of review pairs and final comparisons.

    Arguments:
        reviews: ordered review pairs to audit
        comparisons: ordered final output comparisons to audit
        filters: row, character, and range filters
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if inputs are absent, differ in length, or do not match
            review test cases
    """
    if not reviews:
        raise ScinoephileError("Unable to audit subtitle reviews: no reviews provided")
    row_filter = filters.row_filter
    if row_filter not in ReviewAuditFilter:
        raise ScinoephileError(
            f"Unable to audit subtitle reviews: unsupported row filter "
            f"{row_filter.value!r}"
        )
    if row_filter == ReviewAuditFilter.discrepancies and not comparisons:
        raise ScinoephileError(
            "Unable to audit subtitle reviews: discrepancy filtering requires at "
            "least one comparison"
        )

    all_series = tuple(
        series for review in reviews for series in (review.original, review.reviewed)
    ) + tuple(
        series
        for comparison in comparisons
        for series in (comparison.one, comparison.two)
    )
    if len({len(series) for series in all_series}) != 1:
        raise ScinoephileError(
            "Unable to audit subtitle reviews: subtitle inputs must contain the "
            "same number of subtitles"
        )

    review_series = tuple(
        (
            tuple(subtitle.text_with_newline for subtitle in review.original),
            tuple(subtitle.text_with_newline for subtitle in review.reviewed),
        )
        for review in reviews
    )
    comparison_series = tuple(
        (
            tuple(subtitle.text_with_newline for subtitle in comparison.one),
            tuple(subtitle.text_with_newline for subtitle in comparison.two),
        )
        for comparison in comparisons
    )

    # Match block-based log data against the complete inputs
    try:
        metadata_by_review = tuple(
            get_review_audit_metadata(review.review_cases, original, reviewed)
            for review, (original, reviewed) in zip(reviews, review_series, strict=True)
        )
        notes = tuple(metadata.notes_by_index for metadata in metadata_by_review)
        covered_indexes = frozenset(
            index
            for metadata in metadata_by_review
            for index in metadata.covered_indexes
        )
        unverified_indexes = frozenset(
            index
            for metadata in metadata_by_review
            for index in metadata.unverified_indexes
        )
        has_review_cases = any(review.review_cases for review in reviews)
    except ValueError as exc:
        raise ScinoephileError(f"Unable to audit subtitle reviews: {exc}") from exc

    indexes = get_event_indexes_in_range(
        reviews[0].original,
        first_index=filters.first_index,
        last_index=filters.last_index,
        first_block=filters.first_block,
        last_block=filters.last_block,
    )

    review_changes = tuple(
        _get_changed_indexes(original, reviewed, indexes)
        for original, reviewed in review_series
    )
    comparison_changes = tuple(
        _get_changed_indexes(one, two, indexes) for one, two in comparison_series
    )
    selected_indexes = _get_filtered_indexes(
        series=tuple(
            item for pair in (*review_series, *comparison_series) for item in pair
        ),
        review_changes=review_changes,
        comparison_changes=comparison_changes,
        indexes=indexes,
        filters=filters,
        unverified_indexes=unverified_indexes,
    )
    return _format_report(
        reviews=reviews,
        review_series=review_series,
        review_changes=review_changes,
        notes=notes,
        comparisons=comparisons,
        comparison_series=comparison_series,
        comparison_changes=comparison_changes,
        covered_indexes=covered_indexes,
        has_review_cases=has_review_cases,
        indexes=selected_indexes,
        filters=filters,
        unverified_indexes=unverified_indexes,
    )


def _format_report(
    *,
    reviews: Sequence[ReviewAuditBeforeAfterPair],
    review_series: Sequence[tuple[Sequence[str], Sequence[str]]],
    review_changes: Sequence[set[int]],
    notes: Sequence[Mapping[int, Sequence[str]]],
    comparisons: Sequence[ReviewAuditSeriesPair],
    comparison_series: Sequence[tuple[Sequence[str], Sequence[str]]],
    comparison_changes: Sequence[set[int]],
    covered_indexes: frozenset[int],
    has_review_cases: bool,
    indexes: Sequence[int],
    filters: ReviewAuditFilterGroup,
    unverified_indexes: frozenset[int],
) -> str:
    """Build semantic review data and format it with the shared renderer.

    Arguments:
        reviews: ordered review-pair specifications
        review_series: original and reviewed subtitle text for each review
        review_changes: changed subtitle indexes for each review
        notes: review notes by review and subtitle index
        comparisons: ordered comparison specifications
        comparison_series: subtitle text for both series in each comparison
        comparison_changes: changed subtitle indexes for each comparison
        covered_indexes: subtitle indexes covered by logged cases
        has_review_cases: whether any review decision log was supplied
        indexes: zero-based subtitle indexes to include
        filters: active row, character, and range filters
        unverified_indexes: subtitle indexes covered by unverified cases
    Returns:
        Markdown report
    """
    rows: list[list[str]] = []
    for index in indexes:
        note_lines = [
            f"{review.label} review: {note}"
            for review, review_notes in zip(reviews, notes, strict=True)
            for note in review_notes.get(index, ())
        ]
        cells = [str(index + 1)]
        cells.extend(
            _format_review_cell(index, changed_indexes, original, reviewed)
            for changed_indexes, (original, reviewed) in zip(
                review_changes, review_series, strict=True
            )
        )
        cells.extend(
            _format_review_cell(index, changed_indexes, one, two)
            for changed_indexes, (one, two) in zip(
                comparison_changes, comparison_series, strict=True
            )
        )
        cells.append("\n".join(note_lines))
        if has_review_cases:
            verified: bool | None = None
            if index in covered_indexes:
                verified = index not in unverified_indexes
            verified_marker = format_verification_marker(verified)
            cells.append(verified_marker)
        rows.append(cells)

    summary_items = [
        f"{review.label.lower()} review edits: {len(changed_indexes)}"
        for review, changed_indexes in zip(reviews, review_changes, strict=True)
    ]
    summary_items.extend(
        f"{comparison.summary_label.lower()} discrepancies: {len(changed_indexes)}"
        for comparison, changed_indexes in zip(
            comparisons, comparison_changes, strict=True
        )
    )
    summary_items.extend(filters.get_summary_items())

    columns: list[AuditColumn] = [("Subtitle", "right")]
    columns.extend((review.label, "left") for review in reviews)
    columns.extend((comparison.column_label, "left") for comparison in comparisons)
    columns.append(("Notes", "left"))
    if has_review_cases:
        columns.append(("Verified", "center"))
    return format_audit_report(
        title="Review Audit", summary_items=summary_items, columns=columns, rows=rows
    )


def _format_review_cell(
    index: int,
    changed_indexes: set[int],
    original: Sequence[str],
    reviewed: Sequence[str],
) -> str:
    """Format one initial-review table cell.

    Arguments:
        index: zero-based subtitle index
        changed_indexes: subtitle indexes changed during review
        original: original subtitle text
        reviewed: reviewed subtitle text
    Returns:
        formatted review text
    """
    if index not in changed_indexes:
        return reviewed[index]
    return f"{original[index]}\n{reviewed[index]}"


def _get_changed_indexes(
    original: Sequence[str], reviewed: Sequence[str], indexes: Iterable[int]
) -> set[int]:
    """Get subtitle indexes changed during review.

    Arguments:
        original: original subtitle text
        reviewed: reviewed subtitle text
        indexes: zero-based subtitle indexes to compare
    Returns:
        changed subtitle indexes
    """
    return {index for index in indexes if original[index] != reviewed[index]}


def _get_filtered_indexes(
    *,
    series: Sequence[Sequence[str]],
    review_changes: Sequence[set[int]],
    comparison_changes: Sequence[set[int]],
    indexes: Iterable[int],
    filters: ReviewAuditFilterGroup,
    unverified_indexes: frozenset[int],
) -> list[int]:
    """Get subtitle indexes selected for the report.

    Arguments:
        series: all subtitle text sequences
        review_changes: changed subtitle indexes for each review
        comparison_changes: changed subtitle indexes for each comparison
        indexes: zero-based subtitle indexes eligible for inclusion
        filters: row status and character filters
        unverified_indexes: subtitle indexes covered by unverified review cases
    Returns:
        selected subtitle indexes
    Raises:
        AssertionError: if an internal invariant is violated
    """
    row_filter = filters.row_filter
    if row_filter == ReviewAuditFilter.all:
        selected_indexes = set(indexes)
    elif row_filter == ReviewAuditFilter.changes:
        selected_indexes = {
            index
            for changed_indexes in (*review_changes, *comparison_changes)
            for index in changed_indexes
        }
    elif row_filter == ReviewAuditFilter.discrepancies:
        selected_indexes = {
            index for changed_indexes in comparison_changes for index in changed_indexes
        }
    elif row_filter == ReviewAuditFilter.unverified:
        selected_indexes = set(indexes) & unverified_indexes
    else:
        raise AssertionError(f"Unexpected validated row filter {row_filter!r}")

    if filters.character_filter:
        selected_indexes = {
            index
            for index in selected_indexes
            if filters.matches_characters(subtitles[index] for subtitles in series)
        }
    return sorted(selected_indexes)
