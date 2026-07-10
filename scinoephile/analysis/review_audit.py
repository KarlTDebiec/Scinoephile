#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit dual-script subtitle reviews and format the results as Markdown."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from enum import StrEnum
from pathlib import Path

from scinoephile.core import ScinoephileError
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
    traditional_json_path: Path | None = None,
    traditional_simplified_json_path: Path | None = None,
    simplified_json_path: Path | None = None,
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
        traditional_json_path: optional traditional review JSON path
        traditional_simplified_json_path: optional traditional simplification review
            JSON path
        simplified_json_path: optional simplified review JSON path
        row_filter: row status filter
        characters: characters whose occurrence further limits included rows
        first_index: first 1-indexed subtitle number to include, inclusive
        last_index: last 1-indexed subtitle number to include, inclusive
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if review JSON cannot be read or parsed
    """
    try:
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
        notes = {
            "traditional": _get_review_notes(
                traditional_json_path,
                series["traditional"],
                series["traditional_reviewed"],
            ),
            "traditional_simplified": _get_review_notes(
                traditional_simplified_json_path,
                series["traditional_simplified"],
                series["traditional_simplified_reviewed"],
            ),
            "simplified": _get_review_notes(
                simplified_json_path,
                series["simplified"],
                series["simplified_reviewed"],
            ),
        }

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

        normalized_characters = tuple(
            dict.fromkeys(character for value in characters for character in value)
        )
        selected_indexes = _get_filtered_indexes(
            series=series,
            changes=changes,
            indexes=indexes,
            row_filter=row_filter,
            characters=normalized_characters,
        )
        return _format_markdown(
            series=series,
            changes=changes,
            notes=notes,
            indexes=selected_indexes,
            row_filter=row_filter,
            characters=normalized_characters,
            first_index=first_index,
            last_index=last_index,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        raise ScinoephileError(f"Unable to audit subtitle reviews: {exc}") from exc


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
        if index not in changes["final"]:
            final_cell = series["simplified_reviewed"][index]
        else:
            final_cell = (
                f"{series['simplified_reviewed'][index]}\n"
                f"{series['traditional_simplified_reviewed'][index]}"
            )

        note_lines: list[str] = []
        for label, review_notes in note_sources:
            note_lines.extend(
                f"{label}: {note}" for note in review_notes.get(index, ())
            )

        row_lines.append(
            "| "
            + " | ".join(
                (
                    _escape_cell(str(index + 1)),
                    _escape_cell(
                        _format_review_cell(
                            index,
                            changes["simplified"],
                            series["simplified"],
                            series["simplified_reviewed"],
                        )
                    ),
                    _escape_cell(
                        _format_review_cell(
                            index,
                            changes["traditional"],
                            series["traditional"],
                            series["traditional_reviewed"],
                        )
                    ),
                    _escape_cell(final_cell),
                    _escape_cell("\n".join(note_lines)),
                )
            )
            + " |"
        )

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
                "Simplified vs Traditional->Simplified | Notes |"
            ),
            "|---:|---|---|---|---|",
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
    json_path: Path | None,
    original: Sequence[str],
    reviewed: Sequence[str],
) -> dict[int, tuple[str, ...]]:
    """Load review notes and match their blocks to subtitle text.

    Arguments:
        json_path: optional review JSON path
        original: original subtitle text
        reviewed: reviewed subtitle text
    Returns:
        review notes keyed by zero-based subtitle index
    Raises:
        ValueError: if review JSON has an invalid or mismatched structure
    """
    if json_path is None:
        return {}

    data: object = json.loads(json_path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list):
        raise ValueError(f"Review JSON must contain a list: {json_path}")

    original_texts = list(original)
    reviewed_texts = list(reviewed)
    notes_by_index: dict[int, list[str]] = {}
    for case_index, raw_case in enumerate(data, 1):
        review_case = _parse_review_case(raw_case, case_index, json_path)
        if review_case is None:
            continue
        query_texts, revised_texts, note_fields = review_case

        candidate_starts = [
            start
            for start in range(len(original_texts) - len(query_texts) + 1)
            if original_texts[start : start + len(query_texts)] == query_texts
        ]
        if not candidate_starts:
            raise ValueError(
                f"Review JSON item {case_index} does not match its SRT pair: "
                f"{json_path}"
            )
        matched_note_fields: set[int] = set()
        for start in candidate_starts:
            for local_index, note in note_fields.items():
                if (
                    reviewed_texts[start + local_index - 1]
                    != revised_texts[local_index - 1]
                ):
                    continue
                index = start + local_index - 1
                notes = notes_by_index.setdefault(index, [])
                if note not in notes:
                    notes.append(note)
                matched_note_fields.add(local_index)
        unmatched_note_fields = sorted(set(note_fields) - matched_note_fields)
        if unmatched_note_fields:
            formatted_fields = ", ".join(
                f"note_{local_index}" for local_index in unmatched_note_fields
            )
            raise ValueError(
                f"Review JSON item {case_index} fields {formatted_fields} do not "
                f"match reviewed SRT text: {json_path}"
            )

    return {index: tuple(notes) for index, notes in sorted(notes_by_index.items())}


def _parse_review_case(
    raw_case: object,
    case_index: int,
    json_path: Path,
) -> tuple[list[str], list[str], dict[int, str]] | None:
    """Parse one block-based review JSON item.

    Arguments:
        raw_case: unchecked JSON item
        case_index: one-based JSON item index
        json_path: review JSON path for error messages
    Returns:
        query texts, revised texts, and nonempty notes, or None when there are no
        notes
    Raises:
        ValueError: if the JSON item has an invalid review structure
    """
    if not isinstance(raw_case, dict):
        raise ValueError(
            f"Review JSON item {case_index} must be an object: {json_path}"
        )
    raw_query = raw_case.get("query")
    raw_answer = raw_case.get("answer", {})
    if not isinstance(raw_query, dict) or not isinstance(raw_answer, dict):
        raise ValueError(
            f"Review JSON item {case_index} must contain query and answer objects: "
            f"{json_path}"
        )

    note_fields = {
        int(key[5:]): value.strip()
        for key, value in raw_answer.items()
        if isinstance(key, str)
        and key.startswith("note_")
        and key[5:].isdigit()
        and isinstance(value, str)
        and value.strip()
    }
    if not note_fields:
        return None

    query_texts: list[str] = []
    revised_texts: list[str] = []
    for local_index in range(1, len(raw_query) + 1):
        query_text = raw_query.get(f"subtitle_{local_index}")
        if not isinstance(query_text, str):
            raise ValueError(
                f"Review JSON item {case_index} has nonsequential subtitle fields: "
                f"{json_path}"
            )
        revised_text = raw_answer.get(f"revised_{local_index}", query_text)
        if not isinstance(revised_text, str):
            raise ValueError(
                f"Review JSON item {case_index} has an invalid revised field: "
                f"{json_path}"
            )
        if revised_text == "":
            revised_text = query_text
        query_texts.append(query_text)
        revised_texts.append(revised_text)

    for local_index in note_fields:
        if local_index > len(query_texts):
            raise ValueError(
                f"Review JSON item {case_index} has a note without a matching "
                f"subtitle: {json_path}"
            )
        if revised_texts[local_index - 1] == query_texts[local_index - 1]:
            raise ValueError(
                f"Review JSON item {case_index} has a note without a matching "
                f"revision: {json_path}"
            )
    return query_texts, revised_texts, note_fields
