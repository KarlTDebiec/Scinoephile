#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit dual-script subtitle reviews and format the results as Markdown."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import cast

from scinoephile.core import ScinoephileError

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


@dataclass(frozen=True)
class _ReviewChange:
    """One subtitle review edit."""

    original: str
    """Original subtitle text."""

    revised: str
    """Reviewed subtitle text."""


@dataclass(frozen=True)
class _SrtEvent:
    """One SRT event parsed without normalizing its text."""

    number: int
    """Subtitle number."""

    timing: str
    """Raw SRT timing line."""

    text: str
    """Raw subtitle text."""


def audit_reviews(
    *,
    traditional_path: Path,
    traditional_reviewed_path: Path,
    traditional_simplified_path: Path,
    traditional_simplified_reviewed_path: Path,
    simplified_path: Path,
    simplified_reviewed_path: Path,
    traditional_json_path: Path | None = None,
    traditional_simplified_json_path: Path | None = None,
    simplified_json_path: Path | None = None,
    row_filter: ReviewAuditFilter = ReviewAuditFilter.changes,
    characters: Sequence[str] = (),
    first_index: int | None = None,
    last_index: int | None = None,
) -> str:
    """Audit subtitle review paths and return a Markdown report.

    Arguments:
        traditional_path: traditional-script review input SRT path
        traditional_reviewed_path: traditional-script reviewed SRT path
        traditional_simplified_path: simplified traditional-script SRT path
        traditional_simplified_reviewed_path: reviewed simplified traditional-script
            SRT path
        simplified_path: simplified-script review input SRT path
        simplified_reviewed_path: simplified-script reviewed SRT path
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
        ScinoephileError: if an input cannot be parsed or subtitle counts differ
    """
    try:
        _validate_index_range(first_index, last_index)
        series_paths = {
            "traditional": traditional_path,
            "traditional_reviewed": traditional_reviewed_path,
            "traditional_simplified": traditional_simplified_path,
            "traditional_simplified_reviewed": (traditional_simplified_reviewed_path),
            "simplified": simplified_path,
            "simplified_reviewed": simplified_reviewed_path,
        }
        series = {
            name: _parse_srt(series_path) for name, series_path in series_paths.items()
        }
        if len({len(events) for events in series.values()}) != 1:
            raise ValueError("Subtitle counts do not match across series")

        # Match block-based notes against the complete inputs
        traditional_notes = _get_review_notes(
            traditional_json_path,
            series["traditional"],
            series["traditional_reviewed"],
        )
        traditional_simplified_notes = _get_review_notes(
            traditional_simplified_json_path,
            series["traditional_simplified"],
            series["traditional_simplified_reviewed"],
        )
        simplified_notes = _get_review_notes(
            simplified_json_path,
            series["simplified"],
            series["simplified_reviewed"],
        )

        # Limit report calculations after validating the input counts
        series = {
            name: {
                number: event
                for number, event in events.items()
                if (first_index is None or number >= first_index)
                and (last_index is None or number <= last_index)
            }
            for name, events in series.items()
        }
        traditional_changes = _get_review_changes(
            series["traditional"],
            series["traditional_reviewed"],
        )
        traditional_simplified_changes = _get_review_changes(
            series["traditional_simplified"],
            series["traditional_simplified_reviewed"],
        )
        simplified_changes = _get_review_changes(
            series["simplified"],
            series["simplified_reviewed"],
        )
        final_discrepancies = _get_review_changes(
            series["simplified_reviewed"],
            series["traditional_simplified_reviewed"],
        )

        normalized_characters = tuple(
            dict.fromkeys(character for value in characters for character in value)
        )
        numbers = _get_filtered_numbers(
            series=series,
            traditional_changes=traditional_changes,
            traditional_simplified_changes=traditional_simplified_changes,
            simplified_changes=simplified_changes,
            final_discrepancies=final_discrepancies,
            row_filter=row_filter,
            characters=normalized_characters,
        )
        return _format_markdown(
            series=series,
            traditional_changes=traditional_changes,
            traditional_simplified_changes=traditional_simplified_changes,
            simplified_changes=simplified_changes,
            final_discrepancies=final_discrepancies,
            traditional_notes=traditional_notes,
            traditional_simplified_notes=traditional_simplified_notes,
            simplified_notes=simplified_notes,
            numbers=numbers,
            row_filter=row_filter,
            characters=normalized_characters,
            first_index=first_index,
            last_index=last_index,
        )
    except ScinoephileError:
        raise
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
    series: Mapping[str, Mapping[int, _SrtEvent]],
    traditional_changes: Mapping[int, _ReviewChange],
    traditional_simplified_changes: Mapping[int, _ReviewChange],
    simplified_changes: Mapping[int, _ReviewChange],
    final_discrepancies: Mapping[int, _ReviewChange],
    traditional_notes: Mapping[int, Sequence[str]],
    traditional_simplified_notes: Mapping[int, Sequence[str]],
    simplified_notes: Mapping[int, Sequence[str]],
    numbers: Sequence[int],
    row_filter: ReviewAuditFilter,
    characters: Sequence[str],
    first_index: int | None,
    last_index: int | None,
) -> str:
    """Format a review audit as Markdown.

    Arguments:
        series: parsed SRT events keyed by internal series name
        traditional_changes: traditional review changes by subtitle number
        traditional_simplified_changes: traditional simplification review changes by
            subtitle number
        simplified_changes: simplified review changes by subtitle number
        final_discrepancies: final discrepancies by subtitle number
        traditional_notes: traditional review notes by subtitle number
        traditional_simplified_notes: traditional simplification review notes by
            subtitle number
        simplified_notes: simplified review notes by subtitle number
        numbers: subtitle numbers to include
        row_filter: active row filter
        characters: active character filter
        first_index: first included 1-indexed subtitle number
        last_index: last included 1-indexed subtitle number
    Returns:
        Markdown report
    """
    row_lines: list[str] = []
    for number in numbers:
        final_discrepancy = final_discrepancies.get(number)
        if final_discrepancy is None:
            final_cell = series["simplified_reviewed"][number].text
        else:
            final_cell = f"{final_discrepancy.original}\n{final_discrepancy.revised}"

        note_lines: list[str] = []
        note_sources = (
            ("Simplified review", simplified_notes),
            ("Traditional review", traditional_notes),
            ("Traditional simplification review", traditional_simplified_notes),
        )
        for label, notes in note_sources:
            note_lines.extend(f"{label}: {note}" for note in notes.get(number, ()))

        row_lines.append(
            "| "
            + " | ".join(
                (
                    _escape_cell(str(number)),
                    _escape_cell(
                        _format_review_cell(
                            number,
                            simplified_changes,
                            series["simplified_reviewed"],
                        )
                    ),
                    _escape_cell(
                        _format_review_cell(
                            number,
                            traditional_changes,
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
        f"- simplified review edits: {len(simplified_changes)}",
        f"- traditional review edits: {len(traditional_changes)}",
        (
            "- traditional simplification review edits: "
            f"{len(traditional_simplified_changes)}"
        ),
        f"- final text discrepancies: {len(final_discrepancies)}",
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
    number: int,
    changes: Mapping[int, _ReviewChange],
    reviewed: Mapping[int, _SrtEvent],
) -> str:
    """Format one initial-review table cell.

    Arguments:
        number: subtitle number
        changes: review changes by subtitle number
        reviewed: reviewed subtitle events
    Returns:
        formatted review text
    """
    change = changes.get(number)
    if change is None:
        return reviewed[number].text
    return f"{change.original}\n{change.revised}"


def _get_filtered_numbers(
    *,
    series: Mapping[str, Mapping[int, _SrtEvent]],
    traditional_changes: Mapping[int, _ReviewChange],
    traditional_simplified_changes: Mapping[int, _ReviewChange],
    simplified_changes: Mapping[int, _ReviewChange],
    final_discrepancies: Mapping[int, _ReviewChange],
    row_filter: ReviewAuditFilter,
    characters: Sequence[str],
) -> list[int]:
    """Get subtitle numbers selected for the report.

    Arguments:
        series: parsed SRT events keyed by internal series name
        traditional_changes: traditional review changes by subtitle number
        traditional_simplified_changes: traditional simplification review changes by
            subtitle number
        simplified_changes: simplified review changes by subtitle number
        final_discrepancies: final discrepancies by subtitle number
        row_filter: row status filter
        characters: optional character filter
    Returns:
        selected subtitle numbers
    """
    if row_filter is ReviewAuditFilter.all:
        numbers = set(series["traditional"])
    elif row_filter is ReviewAuditFilter.changes:
        numbers = (
            set(traditional_changes)
            | set(traditional_simplified_changes)
            | set(simplified_changes)
            | set(final_discrepancies)
        )
    else:
        numbers = set(final_discrepancies)

    if characters:
        numbers = {
            number
            for number in numbers
            if any(
                character in events[number].text
                for events in series.values()
                for character in characters
            )
        }
    return sorted(numbers)


def _get_review_changes(
    original: Mapping[int, _SrtEvent],
    reviewed: Mapping[int, _SrtEvent],
) -> dict[int, _ReviewChange]:
    """Get text changes between original and reviewed events.

    Arguments:
        original: original subtitle events
        reviewed: reviewed subtitle events
    Returns:
        review changes keyed by subtitle number
    """
    return {
        number: _ReviewChange(
            original=event.text,
            revised=reviewed[number].text,
        )
        for number, event in original.items()
        if event.text != reviewed[number].text
    }


def _get_review_notes(
    json_path: Path | None,
    original: Mapping[int, _SrtEvent],
    reviewed: Mapping[int, _SrtEvent],
) -> dict[int, tuple[str, ...]]:
    """Load review notes and match their blocks to SRT events.

    Arguments:
        json_path: optional review JSON path
        original: original subtitle events
        reviewed: reviewed subtitle events
    Returns:
        review notes keyed by subtitle number
    Raises:
        ValueError: if review JSON has an invalid or mismatched structure
    """
    if json_path is None:
        return {}

    data: object = json.loads(json_path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list):
        raise ValueError(f"Review JSON must contain a list: {json_path}")

    ordered_numbers = list(original)
    original_texts = [original[number].text for number in ordered_numbers]
    reviewed_texts = [reviewed[number].text for number in ordered_numbers]
    notes_by_number: dict[int, list[str]] = {}
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
                number = ordered_numbers[start + local_index - 1]
                notes = notes_by_number.setdefault(number, [])
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

    return {number: tuple(notes) for number, notes in sorted(notes_by_number.items())}


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

    note_fields = _parse_review_note_fields(cast(Mapping[object, object], raw_answer))
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


def _parse_review_note_fields(
    raw_answer: Mapping[object, object],
) -> dict[int, str]:
    """Parse nonempty note fields from one review answer.

    Arguments:
        raw_answer: unchecked review answer mapping
    Returns:
        nonempty notes keyed by one-based local subtitle index
    """
    note_fields: dict[int, str] = {}
    for key, value in raw_answer.items():
        if not isinstance(key, str):
            continue
        match = re.fullmatch(r"note_(\d+)", key)
        if match is None or not isinstance(value, str) or not value.strip():
            continue
        note_fields[int(match.group(1))] = value.strip()
    return note_fields


def _parse_srt(srt_path: Path) -> dict[int, _SrtEvent]:
    """Parse an SRT file without normalizing subtitle text.

    Arguments:
        srt_path: SRT file path
    Returns:
        SRT events keyed by subtitle number
    Raises:
        ValueError: if the SRT structure is invalid
    """
    text = srt_path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    blocks = [block for block in re.split(r"\n{2,}", text.strip("\n")) if block]
    events: dict[int, _SrtEvent] = {}
    for block_index, block in enumerate(blocks, 1):
        lines = block.split("\n")
        if len(lines) < 2:
            raise ValueError(f"Invalid SRT block {block_index}: {srt_path}")
        try:
            number = int(lines[0])
        except ValueError as exc:
            raise ValueError(
                f"Invalid subtitle number in SRT block {block_index}: {srt_path}"
            ) from exc
        if number in events:
            raise ValueError(f"Duplicate subtitle number {number}: {srt_path}")
        events[number] = _SrtEvent(
            number=number,
            timing=lines[1],
            text="\n".join(lines[2:]),
        )
    return events


def _validate_index_range(first_index: int | None, last_index: int | None) -> None:
    """Validate inclusive 1-indexed subtitle range bounds.

    Arguments:
        first_index: first 1-indexed subtitle number to include, inclusive
        last_index: last 1-indexed subtitle number to include, inclusive
    Raises:
        ValueError: if either bound is invalid
    """
    if first_index is not None and first_index < 1:
        raise ValueError("--first-index must be a positive 1-indexed subtitle number")
    if last_index is not None and last_index < 1:
        raise ValueError("--last-index must be a positive 1-indexed subtitle number")
    if first_index is not None and last_index is not None and first_index > last_index:
        raise ValueError("--first-index must be less than or equal to --last-index")
