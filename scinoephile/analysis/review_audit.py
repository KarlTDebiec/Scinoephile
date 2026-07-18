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

from .audit_utils import _validate_index_range

__all__ = [
    "ReviewAuditComparison",
    "ReviewAuditFilter",
    "ReviewAuditPair",
    "audit_review_workflow",
    "audit_reviews",
]


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


class ReviewAuditFilter(StrEnum):
    """Row filters supported by a review audit."""

    all = "all"
    """Include every subtitle row."""

    changes = "changes"
    """Include review edits and final discrepancies."""

    discrepancies = "discrepancies"
    """Include only final discrepancies."""


def audit_reviews(
    *,
    traditional: Series,
    traditional_reviewed: Series,
    traditional_simplified: Series,
    traditional_simplified_reviewed: Series,
    simplified: Series,
    simplified_reviewed: Series,
    traditional_review_cases: Sequence[TestCase] = (),
    traditional_simplified_review_cases: Sequence[TestCase] = (),
    simplified_review_cases: Sequence[TestCase] = (),
    row_filter: ReviewAuditFilter = ReviewAuditFilter.changes,
    characters: Sequence[str] = (),
    first_index: int | None = None,
    last_index: int | None = None,
) -> str:
    """Audit parallel simplified and traditional-to-simplified review paths.

    Arguments:
        traditional: traditional-script review input
        traditional_reviewed: traditional-script reviewed subtitles
        traditional_simplified: simplified traditional-script subtitles
        traditional_simplified_reviewed: reviewed simplified traditional-script
            subtitles
        simplified: simplified-script review input
        simplified_reviewed: simplified-script reviewed subtitles
        traditional_review_cases: traditional review test cases
        traditional_simplified_review_cases: traditional simplification review test
            cases
        simplified_review_cases: simplified review test cases
        row_filter: row status filter
        characters: individual characters whose occurrence limits included rows
        first_index: first 1-indexed subtitle number to include, inclusive
        last_index: last 1-indexed subtitle number to include, inclusive
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if review test cases do not match the subtitle series
    """
    return audit_review_workflow(
        reviews=(
            ReviewAuditPair(
                label="Simplified",
                original=simplified,
                reviewed=simplified_reviewed,
                review_cases=simplified_review_cases,
            ),
            ReviewAuditPair(
                label="Traditional",
                original=traditional,
                reviewed=traditional_reviewed,
                review_cases=traditional_review_cases,
            ),
            ReviewAuditPair(
                label="Traditional simplification",
                original=traditional_simplified,
                reviewed=traditional_simplified_reviewed,
                review_cases=traditional_simplified_review_cases,
            ),
        ),
        comparisons=(
            ReviewAuditComparison(
                column_label="Simplified vs Traditional->Simplified",
                summary_label="Final text",
                left=simplified_reviewed,
                right=traditional_simplified_reviewed,
            ),
        ),
        row_filter=row_filter,
        characters=characters,
        first_index=first_index,
        last_index=last_index,
    )


def audit_review_workflow(
    *,
    reviews: Sequence[ReviewAuditPair],
    comparisons: Sequence[ReviewAuditComparison] = (),
    row_filter: ReviewAuditFilter = ReviewAuditFilter.changes,
    characters: Sequence[str] = (),
    first_index: int | None = None,
    last_index: int | None = None,
) -> str:
    """Audit a composition of review pairs and final comparisons.

    Arguments:
        reviews: ordered review pairs to audit
        comparisons: ordered final output comparisons to audit
        row_filter: row status filter
        characters: individual characters whose occurrence limits included rows
        first_index: first 1-indexed subtitle number to include, inclusive
        last_index: last 1-indexed subtitle number to include, inclusive
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if inputs are absent, differ in length, or do not match
            review test cases
    """
    _validate_index_range(first_index, last_index)

    if not reviews:
        raise ScinoephileError("Unable to audit subtitle reviews: no reviews provided")

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

    # Match block-based notes against the complete inputs
    try:
        notes = tuple(
            _get_review_notes(review.review_cases, original, reviewed)
            for review, (original, reviewed) in zip(
                reviews,
                review_series,
                strict=True,
            )
        )
    except ValueError as exc:
        raise ScinoephileError(f"Unable to audit subtitle reviews: {exc}") from exc

    # Select the requested zero-based subtitle indexes
    start_index = 0
    if first_index is not None:
        start_index = first_index - 1
    stop_index = len(all_series[0])
    if last_index is not None:
        stop_index = min(last_index, stop_index)
    indexes = range(start_index, stop_index)

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
        characters=characters,
    )
    return _format_markdown(
        reviews=reviews,
        review_series=review_series,
        review_changes=review_changes,
        notes=notes,
        comparisons=comparisons,
        comparison_series=comparison_series,
        comparison_changes=comparison_changes,
        indexes=selected_indexes,
        row_filter=row_filter,
        characters=characters,
        first_index=first_index,
        last_index=last_index,
    )


def _escape_cell(value: str) -> str:
    """Escape one Markdown table cell.

    Arguments:
        value: cell text
    Returns:
        escaped cell text
    """
    return value.replace("\n", "<br>").replace("|", "\\|")


def _format_markdown(
    *,
    reviews: Sequence[ReviewAuditPair],
    review_series: Sequence[tuple[Sequence[str], Sequence[str]]],
    review_changes: Sequence[set[int]],
    notes: Sequence[Mapping[int, Sequence[str]]],
    comparisons: Sequence[ReviewAuditComparison],
    comparison_series: Sequence[tuple[Sequence[str], Sequence[str]]],
    comparison_changes: Sequence[set[int]],
    indexes: Sequence[int],
    row_filter: ReviewAuditFilter,
    characters: Sequence[str],
    first_index: int | None,
    last_index: int | None,
) -> str:
    """Format a review audit as Markdown.

    Arguments:
        reviews: ordered review-pair specifications
        review_series: original and reviewed subtitle text for each review
        review_changes: changed subtitle indexes for each review
        notes: review notes by review and subtitle index
        comparisons: ordered comparison specifications
        comparison_series: left- and right-hand subtitle text for each comparison
        comparison_changes: changed subtitle indexes for each comparison
        indexes: zero-based subtitle indexes to include
        row_filter: active row filter
        characters: active character filter
        first_index: first included 1-indexed subtitle number
        last_index: last included 1-indexed subtitle number
    Returns:
        Markdown report
    """
    row_lines: list[str] = []
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
        row_lines.append(f"| {' | '.join(_escape_cell(cell) for cell in cells)} |")

    lines = [
        "# Review Audit",
        "",
        "## Summary",
        "",
    ]
    lines.extend(
        f"- {review.label.lower()} review edits: {len(changed_indexes)}"
        for review, changed_indexes in zip(reviews, review_changes, strict=True)
    )
    lines.extend(
        f"- {comparison.summary_label.lower()} discrepancies: {len(changed_indexes)}"
        for comparison, changed_indexes in zip(
            comparisons,
            comparison_changes,
            strict=True,
        )
    )
    lines.append(f"- row filter: {row_filter.value}")
    if characters:
        lines.append(f"- character filter: {', '.join(characters)}")
    if first_index is not None or last_index is not None:
        if first_index is None:
            lines.append(f"- subtitle range: 1-indexed numbers through {last_index}")
        elif last_index is None:
            lines.append(f"- subtitle range: 1-indexed numbers from {first_index}")
        else:
            lines.append(
                f"- subtitle range: 1-indexed numbers {first_index} through "
                f"{last_index}"
            )

    column_labels = ["Subtitle"]
    column_labels.extend(review.label for review in reviews)
    column_labels.extend(comparison.column_label for comparison in comparisons)
    column_labels.append("Notes")
    lines.extend(
        (
            f"- table rows: {len(row_lines)}",
            "",
            "## Audit Table",
            "",
            f"| {' | '.join(column_labels)} |",
            f"|---:|{'|'.join('---' for _ in column_labels[1:])}|",
            *row_lines,
        )
    )
    return "\n".join(lines) + "\n"


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
    row_filter: ReviewAuditFilter,
    characters: Sequence[str],
) -> list[int]:
    """Get subtitle indexes selected for the report.

    Arguments:
        series: all subtitle text sequences
        review_changes: changed subtitle indexes for each review
        comparison_changes: changed subtitle indexes for each comparison
        indexes: zero-based subtitle indexes eligible for inclusion
        row_filter: row status filter
        characters: optional character filter
    Returns:
        selected subtitle indexes
    """
    if row_filter is ReviewAuditFilter.all:
        selected_indexes = set(indexes)
    elif row_filter is ReviewAuditFilter.changes:
        selected_indexes = {
            index
            for changed_indexes in (*review_changes, *comparison_changes)
            for index in changed_indexes
        }
    else:
        selected_indexes = {
            index for changed_indexes in comparison_changes for index in changed_indexes
        }

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


def _get_review_notes(
    review_cases: Sequence[TestCase],
    original: tuple[str, ...],
    reviewed: tuple[str, ...],
) -> dict[int, tuple[str, ...]]:
    """Match review test-case notes to subtitle text.

    Arguments:
        review_cases: deserialized review test cases
        original: original subtitle text
        reviewed: reviewed subtitle text
    Returns:
        review notes keyed by zero-based subtitle index
    Raises:
        ValueError: if a review test case does not match the subtitles
    """
    notes_by_index: dict[int, list[str]] = {}
    for case_index, review_case in enumerate(review_cases, 1):
        answer = review_case.answer
        if answer is None:
            continue
        query_subtitles = cast(
            list[dict[str, int | str]],
            review_case.query.model_dump()["subtitles"],
        )
        answer_revisions = cast(
            list[dict[str, int | str]],
            answer.model_dump()["revisions"],
        )
        query_texts = tuple(cast(str, subtitle["text"]) for subtitle in query_subtitles)
        revision_by_index = {
            cast(int, revision["index"]): revision for revision in answer_revisions
        }
        revised_texts: list[str] = []
        for local_index, query_text in enumerate(query_texts, 1):
            revision = revision_by_index.get(local_index)
            if revision is None:
                revised_texts.append(query_text)
            else:
                revised_texts.append(cast(str, revision["text"]))
        note_fields = {
            local_index: cast(str, revision["note"]).strip()
            for local_index, revision in revision_by_index.items()
        }
        if not note_fields:
            continue

        candidate_starts = [
            start
            for start in range(len(original) - len(query_texts) + 1)
            if original[start : start + len(query_texts)] == query_texts
        ]
        if not candidate_starts:
            raise ValueError(
                f"Review test case {case_index} does not match its subtitle pair"
            )
        matched_note_fields: set[int] = set()
        for start in candidate_starts:
            for local_index, note in note_fields.items():
                if reviewed[start + local_index - 1] != revised_texts[local_index - 1]:
                    continue
                index = start + local_index - 1
                notes = notes_by_index.setdefault(index, [])
                if note not in notes:
                    notes.append(note)
                matched_note_fields.add(local_index)
        unmatched_note_fields = sorted(note_fields.keys() - matched_note_fields)
        if unmatched_note_fields:
            formatted_fields = ", ".join(
                f"revision {local_index}" for local_index in unmatched_note_fields
            )
            raise ValueError(
                f"Review test case {case_index} fields {formatted_fields} do not "
                "match reviewed subtitle text"
            )

    return {index: tuple(notes) for index, notes in notes_by_index.items()}
