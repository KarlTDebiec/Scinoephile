#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit subtitle review workflows and format the results as Markdown."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import cast

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import TestCase
from scinoephile.core.subtitles import Series

from .utils import (
    AuditColumn,
    format_audit_report,
    format_verification_marker,
    get_selected_event_indexes,
)

__all__ = [
    "ReviewAuditComparison",
    "ReviewAuditFilter",
    "ReviewAuditPair",
    "audit_review",
]


class ReviewAuditFilter(StrEnum):
    """Row filters supported by a subtitle review audit."""

    all = "all"
    """Include every eligible row."""

    changes = "changes"
    """Include only rows with review edits."""

    unverified = "unverified"
    """Include only rows from cases not marked as verified."""


@dataclass(frozen=True, kw_only=True)
class ReviewAuditPair:
    """One subtitle review's input, output, and optional notes.

    A pair is the reusable unit shared by single-review, sequential, and parallel
    audit workflows.
    """

    label: str
    """Human-readable label used in the report, without the word "review"."""
    original: Series
    """Subtitle series before review."""
    reviewed: Series
    """Subtitle series after review."""
    review_cases: Sequence[TestCase] = ()
    """Optional review test cases containing revision notes."""


@dataclass(frozen=True, kw_only=True)
class ReviewAuditComparison:
    """One final comparison between outputs of an audit workflow."""

    column_label: str
    """Human-readable label used for the report table column."""
    summary_label: str
    """Human-readable label used before "discrepancies" in the summary."""
    left: Series
    """Left-hand subtitle series."""
    right: Series
    """Right-hand subtitle series."""


@dataclass(frozen=True, kw_only=True)
class _ReviewAuditMetadata:
    """Matched notes and verification state for one review decision log."""

    covered_indexes: frozenset[int]
    """Zero-based subtitle indexes covered by current logged cases."""
    notes_by_index: Mapping[int, tuple[str, ...]]
    """Current revision notes keyed by zero-based subtitle index."""
    unverified_indexes: frozenset[int]
    """Covered subtitle indexes belonging to unverified cases."""


def audit_review(
    *,
    reviews: Sequence[ReviewAuditPair],
    comparisons: Sequence[ReviewAuditComparison] = (),
    row_filter: StrEnum = ReviewAuditFilter.changes,
    characters: Sequence[str] = (),
    first_index: int | None = None,
    last_index: int | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
) -> str:
    """Audit a composition of review pairs and final comparisons.

    Arguments:
        reviews: ordered review pairs to audit
        comparisons: ordered final output comparisons to audit
        row_filter: row status filter
        characters: individual characters whose occurrence limits included rows
        first_index: first 1-indexed subtitle number to include, inclusive
        last_index: last 1-indexed subtitle number to include, inclusive
        first_block: first 1-indexed workflow block number to include, inclusive
        last_block: last 1-indexed workflow block number to include, inclusive
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if inputs are absent, differ in length, or do not match
            review test cases
    """
    if not reviews:
        raise ScinoephileError("Unable to audit subtitle reviews: no reviews provided")
    if row_filter.value == "discrepancies" and not comparisons:
        raise ScinoephileError(
            "Unable to audit subtitle reviews: discrepancy filtering requires at "
            "least one comparison"
        )

    all_series = tuple(
        series for review in reviews for series in (review.original, review.reviewed)
    ) + tuple(
        series
        for comparison in comparisons
        for series in (comparison.left, comparison.right)
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
            tuple(subtitle.text_with_newline for subtitle in comparison.left),
            tuple(subtitle.text_with_newline for subtitle in comparison.right),
        )
        for comparison in comparisons
    )

    # Match block-based log data against the complete inputs
    try:
        review_metadata = tuple(
            _get_review_metadata(review.review_cases, original, reviewed)
            for review, (original, reviewed) in zip(
                reviews,
                review_series,
                strict=True,
            )
        )
        notes = tuple(metadata.notes_by_index for metadata in review_metadata)
        covered_indexes = frozenset(
            index for metadata in review_metadata for index in metadata.covered_indexes
        )
        unverified_indexes = frozenset(
            index
            for metadata in review_metadata
            for index in metadata.unverified_indexes
        )
        has_review_cases = any(review.review_cases for review in reviews)
    except ValueError as exc:
        raise ScinoephileError(f"Unable to audit subtitle reviews: {exc}") from exc

    indexes = get_selected_event_indexes(
        reviews[0].original,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )

    review_changes = tuple(
        _get_changed_indexes(original, reviewed, indexes)
        for original, reviewed in review_series
    )
    comparison_changes = tuple(
        _get_changed_indexes(left, right, indexes) for left, right in comparison_series
    )
    selected_indexes = _get_filtered_indexes(
        series=tuple(
            item for pair in (*review_series, *comparison_series) for item in pair
        ),
        review_changes=review_changes,
        comparison_changes=comparison_changes,
        indexes=indexes,
        row_filter=row_filter,
        unverified_indexes=unverified_indexes,
        characters=characters,
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
        row_filter=row_filter,
        unverified_indexes=unverified_indexes,
        characters=characters,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )


def _format_report(
    *,
    reviews: Sequence[ReviewAuditPair],
    review_series: Sequence[tuple[Sequence[str], Sequence[str]]],
    review_changes: Sequence[set[int]],
    notes: Sequence[Mapping[int, Sequence[str]]],
    comparisons: Sequence[ReviewAuditComparison],
    comparison_series: Sequence[tuple[Sequence[str], Sequence[str]]],
    comparison_changes: Sequence[set[int]],
    covered_indexes: frozenset[int],
    has_review_cases: bool,
    indexes: Sequence[int],
    row_filter: StrEnum,
    unverified_indexes: frozenset[int],
    characters: Sequence[str],
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
) -> str:
    """Build semantic review data and format it with the shared renderer.

    Arguments:
        reviews: ordered review-pair specifications
        review_series: original and reviewed subtitle text for each review
        review_changes: changed subtitle indexes for each review
        notes: review notes by review and subtitle index
        comparisons: ordered comparison specifications
        comparison_series: left- and right-hand subtitle text for each comparison
        comparison_changes: changed subtitle indexes for each comparison
        covered_indexes: subtitle indexes covered by logged cases
        has_review_cases: whether any review decision log was supplied
        indexes: zero-based subtitle indexes to include
        row_filter: active row filter
        unverified_indexes: subtitle indexes covered by unverified cases
        characters: active character filter
        first_index: first included 1-indexed subtitle number
        last_index: last included 1-indexed subtitle number
        first_block: first included 1-indexed workflow block number
        last_block: last included 1-indexed workflow block number
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
                review_changes,
                review_series,
                strict=True,
            )
        )
        cells.extend(
            _format_review_cell(index, changed_indexes, left, right)
            for changed_indexes, (left, right) in zip(
                comparison_changes,
                comparison_series,
                strict=True,
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
            comparisons,
            comparison_changes,
            strict=True,
        )
    )
    summary_items.append(f"row filter: {row_filter.value}")
    if characters:
        summary_items.append(f"character filter: {', '.join(characters)}")

    columns: list[AuditColumn] = [("Subtitle", "right")]
    columns.extend((review.label, "left") for review in reviews)
    columns.extend((comparison.column_label, "left") for comparison in comparisons)
    columns.append(("Notes", "left"))
    if has_review_cases:
        columns.append(("Verified", "center"))
    return format_audit_report(
        title="Review Audit",
        summary_items=summary_items,
        columns=columns,
        rows=rows,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
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
    original: Sequence[str],
    reviewed: Sequence[str],
    indexes: Iterable[int],
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
    row_filter: StrEnum,
    unverified_indexes: frozenset[int],
    characters: Sequence[str],
) -> list[int]:
    """Get subtitle indexes selected for the report.

    Arguments:
        series: all subtitle text sequences
        review_changes: changed subtitle indexes for each review
        comparison_changes: changed subtitle indexes for each comparison
        indexes: zero-based subtitle indexes eligible for inclusion
        row_filter: row status filter
        unverified_indexes: subtitle indexes covered by unverified review cases
        characters: optional character filter
    Returns:
        selected subtitle indexes
    """
    if row_filter.value == "all":
        selected_indexes = set(indexes)
    elif row_filter.value == "changes":
        selected_indexes = {
            index
            for changed_indexes in (*review_changes, *comparison_changes)
            for index in changed_indexes
        }
    elif row_filter.value == "discrepancies":
        selected_indexes = {
            index for changed_indexes in comparison_changes for index in changed_indexes
        }
    else:
        selected_indexes = set(indexes) & unverified_indexes

    if characters:
        selected_indexes = {
            index
            for index in selected_indexes
            if any(
                character in subtitles[index]
                for subtitles in series
                for character in characters
            )
        }
    return sorted(selected_indexes)


def _get_review_case_data(
    review_case: TestCase,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    dict[int, dict[str, int | str]],
]:
    """Get query, reviewed, and revision data from a review test case.

    Arguments:
        review_case: deserialized review test case
    Returns:
        query texts, expected reviewed texts, and revisions keyed by local index
    """
    answer = review_case.answer
    query_subtitles = cast(
        list[dict[str, int | str]],
        review_case.query.model_dump()["subtitles"],
    )
    answer_revisions: list[dict[str, int | str]] = []
    if answer is not None:
        answer_revisions = cast(
            list[dict[str, int | str]],
            answer.model_dump()["revisions"],
        )
    query_texts = tuple(cast(str, subtitle["text"]) for subtitle in query_subtitles)
    revision_by_index = {
        cast(int, revision["index"]): revision for revision in answer_revisions
    }
    revised_texts_list = []
    for local_index, query_text in enumerate(query_texts, 1):
        revised_text = query_text
        if local_index in revision_by_index:
            revised_text = cast(str, revision_by_index[local_index]["text"])
        revised_texts_list.append(revised_text)
    revised_texts = tuple(revised_texts_list)
    return query_texts, revised_texts, revision_by_index


def _get_review_metadata(
    review_cases: Sequence[TestCase],
    original: tuple[str, ...],
    reviewed: tuple[str, ...],
) -> _ReviewAuditMetadata:
    """Match the latest current review cases to subtitle text.

    Arguments:
        review_cases: deserialized review test cases
        original: original subtitle text
        reviewed: reviewed subtitle text
    Returns:
        current notes and verification metadata
    Raises:
        ValueError: if a current query's answer does not match reviewed subtitles
    """
    # Retain the latest logged decision for each deduplicated query
    latest_cases_by_query = {
        review_case.query.key: (case_index, review_case)
        for case_index, review_case in enumerate(review_cases, 1)
    }

    # Match current cases once and derive all report metadata together
    covered_indexes: set[int] = set()
    notes_by_index: dict[int, list[str]] = {}
    unverified_indexes: set[int] = set()
    for case_index, review_case in latest_cases_by_query.values():
        query_texts, revised_texts, revision_by_index = _get_review_case_data(
            review_case
        )
        candidate_starts = [
            start
            for start in range(len(original) - len(query_texts) + 1)
            if original[start : start + len(query_texts)] == query_texts
        ]
        if not candidate_starts:
            # Persisted logs retain historical queries after their input changes
            continue

        matched_starts = [
            start
            for start in candidate_starts
            if reviewed[start : start + len(revised_texts)] == revised_texts
        ]
        if not matched_starts:
            raise ValueError(
                f"Review test case {case_index} does not match its subtitle pair"
            )

        for start in matched_starts:
            matched_indexes = set(range(start, start + len(query_texts)))
            covered_indexes.update(matched_indexes)
            if not review_case.verified:
                unverified_indexes.update(matched_indexes)
            for local_index, revision in revision_by_index.items():
                index = start + local_index - 1
                note = cast(str, revision["note"]).strip()
                notes = notes_by_index.setdefault(index, [])
                if note not in notes:
                    notes.append(note)

    return _ReviewAuditMetadata(
        covered_indexes=frozenset(covered_indexes),
        notes_by_index={index: tuple(notes) for index, notes in notes_by_index.items()},
        unverified_indexes=frozenset(unverified_indexes),
    )
