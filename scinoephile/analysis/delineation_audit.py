#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit transcription delineation decisions and format them as Markdown."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from enum import StrEnum

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.llms.delineation import DelineationTestCase

__all__ = [
    "DelineationAuditFilter",
    "audit_delineation",
]


class DelineationAuditFilter(StrEnum):
    """Row filters supported by a transcription delineation audit."""

    all = "all"
    """Include every logged boundary decision."""

    changes = "changes"
    """Include only decisions that shifted the target boundary."""


def audit_delineation(
    reference: Series,
    test_cases: Sequence[DelineationTestCase],
    *,
    row_filter: DelineationAuditFilter = DelineationAuditFilter.all,
    first_index: int | None = None,
    last_index: int | None = None,
) -> str:
    """Audit logged transcription boundary decisions against their reference.

    Arguments:
        reference: reference subtitle series used to guide transcription
        test_cases: logged delineation test cases
        row_filter: row status filter
        first_index: first 1-indexed reference subtitle number to include
        last_index: last 1-indexed reference subtitle number to include
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if a logged reference pair cannot be matched uniquely
    """
    pair_indexes: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index in range(len(reference) - 1):
        pair = (reference[index].text, reference[index + 1].text)
        pair_indexes[pair].append(index)

    row_lines: list[str] = []
    shifts = 0
    no_shifts = 0
    unanswered = 0
    logged_cases = 0
    for test_case_index, test_case in enumerate(test_cases, 1):
        query = test_case.query
        pair = (query.reference_one, query.reference_two)
        matches = pair_indexes.get(pair, [])
        if not matches:
            raise ScinoephileError(
                "Unable to audit transcription delineation: "
                f"test case {test_case_index} reference pair was not found in "
                "reference subtitles"
            )
        if len(matches) > 1:
            starts = ", ".join(str(index + 1) for index in matches)
            raise ScinoephileError(
                "Unable to audit transcription delineation: "
                f"test case {test_case_index} reference pair is ambiguous; "
                f"it begins at subtitle indexes {starts}"
            )

        index = matches[0]
        first_subtitle_index = index + 1
        second_subtitle_index = index + 2
        if first_index is not None and first_subtitle_index < first_index:
            continue
        if last_index is not None and second_subtitle_index > last_index:
            continue
        logged_cases += 1

        boundary_shifted = False
        if test_case.answer is None:
            output = "(unanswered)"
            unanswered += 1
        elif test_case.answer.output_one or test_case.answer.output_two:
            output = _format_pair(
                test_case.answer.output_one,
                test_case.answer.output_two,
            )
            shifts += 1
            boundary_shifted = True
        else:
            output = _format_pair(query.target_one, query.target_two)
            no_shifts += 1

        if row_filter is DelineationAuditFilter.changes and not boundary_shifted:
            continue

        cells = (
            f"{first_subtitle_index}\n{second_subtitle_index}",
            _format_pair(query.reference_one, query.reference_two),
            _format_pair(query.target_one, query.target_two),
            output,
        )
        row_lines.append(f"| {' | '.join(_escape_cell(cell) for cell in cells)} |")

    lines = [
        "# Transcription Delineation Audit",
        "",
        "## Summary",
        "",
        f"- logged cases: {logged_cases}",
        f"- boundary shifts: {shifts}",
        f"- no-shift answers: {no_shifts}",
        f"- unanswered cases: {unanswered}",
        f"- row filter: {row_filter.value}",
    ]
    range_summary = _format_subtitle_range(first_index, last_index)
    if range_summary is not None:
        lines.append(range_summary)
    lines.extend(
        (
            f"- table rows: {len(row_lines)}",
            "",
            "## Audit Table",
            "",
            (
                "| Subtitle indexes | Reference subtitles | Input target subtitles | "
                "Output target subtitles |"
            ),
            "|---:|---|---|---|",
            *row_lines,
        )
    )
    return "\n".join(lines) + "\n"


def _escape_cell(value: str) -> str:
    """Escape one Markdown table cell.

    Arguments:
        value: cell text
    Returns:
        escaped cell text
    """
    return value.replace("\\N", "\n").replace("\n", "<br>").replace("|", "\\|")


def _format_pair(one: str, two: str) -> str:
    """Stack a pair of subtitle texts for one table cell.

    Arguments:
        one: first subtitle text
        two: second subtitle text
    Returns:
        subtitle texts separated by a newline
    """
    return f"{one or '—'}\n{two or '—'}"


def _format_subtitle_range(
    first_index: int | None,
    last_index: int | None,
) -> str | None:
    """Format an optional subtitle range for the report summary.

    Arguments:
        first_index: first included 1-indexed subtitle number
        last_index: last included 1-indexed subtitle number
    Returns:
        formatted range summary, or None if the range is unbounded
    """
    if first_index is None and last_index is None:
        return None
    if first_index is None:
        return f"- subtitle range: 1-indexed numbers through {last_index}"
    if last_index is None:
        return f"- subtitle range: 1-indexed numbers from {first_index}"
    return f"- subtitle range: 1-indexed numbers {first_index} through {last_index}"
