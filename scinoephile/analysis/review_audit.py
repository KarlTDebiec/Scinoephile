#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit dual-script subtitle reviews and format the results as Markdown."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from enum import StrEnum
from typing import cast

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import TestCase
from scinoephile.core.subtitles import Series

__all__ = [
    "ReviewAuditFilter",
    "audit_reviews",
]


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
    """Audit subtitle review series and return a Markdown report.

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
    input_series = {
        "traditional": traditional,
        "traditional_reviewed": traditional_reviewed,
        "traditional_simplified": traditional_simplified,
        "traditional_simplified_reviewed": traditional_simplified_reviewed,
        "simplified": simplified,
        "simplified_reviewed": simplified_reviewed,
    }
    series = {
        name: tuple(subtitle.text_with_newline for subtitle in subtitle_series)
        for name, subtitle_series in input_series.items()
    }

    # Match block-based notes against the complete inputs
    try:
        notes = {
            "traditional": _get_review_notes(
                traditional_review_cases,
                series["traditional"],
                series["traditional_reviewed"],
            ),
            "traditional_simplified": _get_review_notes(
                traditional_simplified_review_cases,
                series["traditional_simplified"],
                series["traditional_simplified_reviewed"],
            ),
            "simplified": _get_review_notes(
                simplified_review_cases,
                series["simplified"],
                series["simplified_reviewed"],
            ),
        }
    except ValueError as exc:
        raise ScinoephileError(f"Unable to audit subtitle reviews: {exc}") from exc

    # Select the requested zero-based subtitle indexes
    start_index = 0
    if first_index is not None:
        start_index = first_index - 1
    stop_index = len(series["traditional"])
    if last_index is not None:
        stop_index = min(last_index, stop_index)
    indexes = range(start_index, stop_index)

    changes = {
        "traditional": _get_changed_indexes(
            series["traditional"],
            series["traditional_reviewed"],
            indexes,
        ),
        "traditional_simplified": _get_changed_indexes(
            series["traditional_simplified"],
            series["traditional_simplified_reviewed"],
            indexes,
        ),
        "simplified": _get_changed_indexes(
            series["simplified"],
            series["simplified_reviewed"],
            indexes,
        ),
        "final": _get_changed_indexes(
            series["simplified_reviewed"],
            series["traditional_simplified_reviewed"],
            indexes,
        ),
    }

    selected_indexes = _get_filtered_indexes(
        series=series,
        changes=changes,
        indexes=indexes,
        row_filter=row_filter,
        characters=characters,
    )
    return _format_markdown(
        series=series,
        changes=changes,
        notes=notes,
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
    series: Mapping[str, Sequence[str]],
    changes: Mapping[str, set[int]],
    notes: Mapping[str, Mapping[int, Sequence[str]]],
    indexes: Sequence[int],
    row_filter: ReviewAuditFilter,
    characters: Sequence[str],
    first_index: int | None,
    last_index: int | None,
) -> str:
    """Format a review audit as Markdown.

    Arguments:
        series: subtitle text by internal series name
        changes: changed subtitle indexes by review name
        notes: review notes by review name and subtitle index
        indexes: zero-based subtitle indexes to include
        row_filter: active row filter
        characters: active character filter
        first_index: first included 1-indexed subtitle number
        last_index: last included 1-indexed subtitle number
    Returns:
        Markdown report
    """
    row_lines: list[str] = []
    note_sources = (
        ("Simplified review", notes["simplified"]),
        ("Traditional review", notes["traditional"]),
        ("Traditional simplification review", notes["traditional_simplified"]),
    )
    for index in indexes:
        note_lines = [
            f"{label}: {note}"
            for label, review_notes in note_sources
            for note in review_notes.get(index, ())
        ]
        cells = (
            str(index + 1),
            _format_review_cell(
                index,
                changes["simplified"],
                series["simplified"],
                series["simplified_reviewed"],
            ),
            _format_review_cell(
                index,
                changes["traditional"],
                series["traditional"],
                series["traditional_reviewed"],
            ),
            _format_review_cell(
                index,
                changes["traditional_simplified"],
                series["traditional_simplified"],
                series["traditional_simplified_reviewed"],
            ),
            _format_review_cell(
                index,
                changes["final"],
                series["simplified_reviewed"],
                series["traditional_simplified_reviewed"],
            ),
            "\n".join(note_lines),
        )
        row_lines.append(f"| {' | '.join(_escape_cell(cell) for cell in cells)} |")

    lines = [
        "# Review Audit",
        "",
        "## Summary",
        "",
        f"- simplified review edits: {len(changes['simplified'])}",
        f"- traditional review edits: {len(changes['traditional'])}",
        (
            "- traditional simplification review edits: "
            f"{len(changes['traditional_simplified'])}"
        ),
        f"- final text discrepancies: {len(changes['final'])}",
        f"- row filter: {row_filter.value}",
    ]
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
    lines.extend(
        (
            f"- table rows: {len(row_lines)}",
            "",
            "## Audit Table",
            "",
            (
                "| Subtitle | Simplified | Traditional | "
                "Traditional->Simplified review | "
                "Simplified vs Traditional->Simplified | Notes |"
            ),
            "|---:|---|---|---|---|---|",
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
    series: Mapping[str, Sequence[str]],
    changes: Mapping[str, set[int]],
    indexes: Iterable[int],
    row_filter: ReviewAuditFilter,
    characters: Sequence[str],
) -> list[int]:
    """Get subtitle indexes selected for the report.

    Arguments:
        series: subtitle text by internal series name
        changes: changed subtitle indexes by review name
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
            index for changed_indexes in changes.values() for index in changed_indexes
        }
    else:
        selected_indexes = changes["final"].copy()

    if characters:
        selected_indexes = {
            index
            for index in selected_indexes
            if any(
                character in subtitles[index]
                for subtitles in series.values()
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
