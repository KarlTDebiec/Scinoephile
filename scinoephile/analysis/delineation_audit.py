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

    candidate_indexes_by_case, direct_indexes = _get_case_indexes(
        pair_indexes,
        test_cases,
        first_index=first_index,
        last_index=last_index,
    )

    rows: list[tuple[int, str]] = []
    shifts = 0
    no_shifts = 0
    unanswered = 0
    logged_cases = 0
    for test_case_index, test_case in enumerate(test_cases, 1):
        candidate_indexes = candidate_indexes_by_case[test_case_index - 1]
        if not candidate_indexes:
            continue
        index = _get_case_index(
            candidate_indexes,
            direct_indexes,
            test_case_index=test_case_index,
        )
        query = test_case.query
        first_subtitle_index = index + 1
        second_subtitle_index = index + 2
        logged_cases += 1

        input_target = (query.target_one, query.target_two)
        answer = test_case.answer
        if answer is None:
            output = "(unanswered)"
            unanswered += 1
            boundary_shifted = False
        elif answer.output_one or answer.output_two:
            output = _format_pair(answer.output_one, answer.output_two)
            shifts += 1
            boundary_shifted = True
        else:
            output = ""
            no_shifts += 1
            boundary_shifted = False

        if row_filter is DelineationAuditFilter.changes and not boundary_shifted:
            continue

        cells = (
            f"{first_subtitle_index}\n{second_subtitle_index}",
            _format_pair(query.reference_one, query.reference_two),
            _format_pair(*input_target),
            output,
            "",
            "✓" if test_case.verified else "",
        )
        rows.append(
            (
                first_subtitle_index,
                f"| {' | '.join(_escape_cell(cell) for cell in cells)} |",
            )
        )

    rows.sort(key=lambda item: item[0])

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
            f"- table rows: {len(rows)}",
            "",
            "## Audit Table",
            "",
            "| Indexes | Reference | Input | Output | Notes | Verified |",
            "|---:|---|---|---|---|:---:|",
            *(row for _, row in rows),
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


def _get_case_index(
    candidate_indexes: Sequence[int],
    direct_indexes: Sequence[int | None],
    *,
    test_case_index: int,
) -> int:
    """Resolve one delineation case's reference-pair index.

    Arguments:
        candidate_indexes: possible zero-indexed reference-pair positions
        direct_indexes: directly resolved indexes for every logged case
        test_case_index: one-indexed test case position
    Returns:
        uniquely resolved zero-indexed reference-pair position
    Raises:
        ScinoephileError: if a case remains ambiguous
    """
    direct_index = direct_indexes[test_case_index - 1]
    if direct_index is not None:
        return direct_index

    contextual_index = _get_contextual_index(
        candidate_indexes,
        direct_indexes,
        test_case_index - 1,
    )
    if contextual_index is not None:
        return contextual_index

    indexes = ", ".join(str(index + 1) for index in candidate_indexes)
    raise ScinoephileError(
        "Unable to audit transcription delineation: "
        f"test case {test_case_index} reference pair is ambiguous; "
        f"it begins at subtitle indexes {indexes}"
    )


def _get_case_indexes(
    pair_indexes: dict[tuple[str, str], list[int]],
    test_cases: Sequence[DelineationTestCase],
    *,
    first_index: int | None,
    last_index: int | None,
) -> tuple[list[list[int]], list[int | None]]:
    """Get candidate and directly resolved indexes for logged cases.

    Arguments:
        pair_indexes: reference-pair positions keyed by subtitle text
        test_cases: logged delineation test cases
        first_index: first 1-indexed reference subtitle number to include
        last_index: last 1-indexed reference subtitle number to include
    Returns:
        candidate and directly resolved indexes for every logged case
    Raises:
        ScinoephileError: if a logged reference pair is absent
    """
    candidate_indexes_by_case: list[list[int]] = []
    direct_indexes: list[int | None] = []
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

        candidate_indexes = [
            index
            for index in matches
            if (first_index is None or index + 1 >= first_index)
            and (last_index is None or index + 2 <= last_index)
        ]
        candidate_indexes_by_case.append(candidate_indexes)
        direct_index = None
        if len(candidate_indexes) == 1:
            direct_index = candidate_indexes[0]
        direct_indexes.append(direct_index)
    return candidate_indexes_by_case, direct_indexes


def _get_contextual_index(
    candidate_indexes: Sequence[int],
    direct_indexes: Sequence[int | None],
    test_case_index: int,
) -> int | None:
    """Resolve a repeated reference pair from neighboring logged cases.

    Arguments:
        candidate_indexes: possible zero-indexed reference-pair positions
        direct_indexes: directly resolved indexes for every logged case
        test_case_index: zero-indexed test case position
    Returns:
        uniquely resolved reference-pair position, or None if ambiguity remains
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
