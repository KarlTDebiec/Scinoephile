#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit transcription delineation decisions and format them as Markdown."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Collection, Sequence

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.llms.delineation import DelineationTestCase

from .utils import (
    AuditFilter,
    AuditResult,
    escape_table_cell,
    format_audit_report,
    get_selected_event_indexes,
    get_superseded_keys,
    resolve_contextual_index,
)

__all__ = ["audit_delineation"]


def audit_delineation(
    reference: Series,
    test_cases: Sequence[DelineationTestCase],
    *,
    row_filter: AuditFilter = AuditFilter.all,
    first_index: int | None = None,
    last_index: int | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
) -> str:
    """Audit logged transcription boundary decisions against their reference.

    Arguments:
        reference: reference subtitle series used to guide transcription
        test_cases: logged delineation test cases
        row_filter: row status filter
        first_index: first 1-indexed reference subtitle number to include
        last_index: last 1-indexed reference subtitle number to include
        first_block: first 1-indexed reference block number to include
        last_block: last 1-indexed reference block number to include
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if a logged reference pair cannot be matched uniquely
    """
    pair_indexes: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index in range(len(reference) - 1):
        pair = (reference[index].text, reference[index + 1].text)
        pair_indexes[pair].append(index)

    selected_reference_indexes = get_selected_event_indexes(
        reference,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )
    candidate_indexes_by_case, direct_indexes = _get_case_indexes(
        pair_indexes,
        test_cases,
    )

    rows: list[tuple[int, str]] = []
    shifts = 0
    no_shifts = 0
    unanswered = 0
    logged_cases = 0
    for test_case_index, test_case in enumerate(test_cases, 1):
        # Resolve against all occurrences before filtering to the requested range
        index = _get_selected_case_index(
            candidate_indexes_by_case[test_case_index - 1],
            direct_indexes,
            selected_reference_indexes,
            test_case_index=test_case_index,
        )
        if index is None:
            continue
        query = test_case.query
        first_subtitle_index = index + 1
        second_subtitle_index = index + 2
        logged_cases += 1

        input_target = (query.target_one, query.target_two)
        answer = test_case.answer
        if answer is None:
            output = "(unanswered)"
            unanswered += 1
            result = AuditResult.unanswered
        elif answer.output_one or answer.output_two:
            output = _format_pair(answer.output_one, answer.output_two)
            shifts += 1
            result = AuditResult.changed
        else:
            output = ""
            no_shifts += 1
            result = AuditResult.unchanged

        if (
            row_filter is AuditFilter.changes and result is not AuditResult.changed
        ) or (row_filter is AuditFilter.unverified and test_case.verified):
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
                f"| {' | '.join(escape_table_cell(cell) for cell in cells)} |",
            )
        )

    rows.sort(key=lambda item: item[0])

    return format_audit_report(
        title="Transcription Delineation Audit",
        summary_lines=(
            f"- logged cases: {logged_cases}",
            f"- boundary shifts: {shifts}",
            f"- no-shift answers: {no_shifts}",
            f"- unanswered cases: {unanswered}",
            f"- row filter: {row_filter.value}",
        ),
        column_labels=(
            "Indexes",
            "Reference",
            "Input",
            "Output",
            "Notes",
            "Verified",
        ),
        column_separators=("---:", "---", "---", "---", "---", ":---:"),
        rows=[row for _, row in rows],
        first_index=first_index,
        last_index=last_index,
        index_track_name="reference",
        first_block=first_block,
        last_block=last_block,
    )


def _format_pair(one: str, two: str) -> str:
    """Stack a pair of subtitle texts for one table cell.

    Arguments:
        one: first subtitle text
        two: second subtitle text
    Returns:
        subtitle texts separated by a newline
    """
    return f"{one or '—'}\n{two or '—'}"


def _get_case_index(
    candidate_indexes: Sequence[int],
    direct_indexes: list[int | None],
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
    index = resolve_contextual_index(
        candidate_indexes,
        direct_indexes,
        test_case_index - 1,
    )
    if index is not None:
        return index

    indexes = ", ".join(str(index + 1) for index in candidate_indexes)
    raise ScinoephileError(
        "Unable to audit transcription delineation: "
        f"test case {test_case_index} reference pair is ambiguous; "
        f"it begins at subtitle indexes {indexes}"
    )


def _get_case_indexes(
    pair_indexes: dict[tuple[str, str], list[int]],
    test_cases: Sequence[DelineationTestCase],
) -> tuple[list[list[int]], list[int | None]]:
    """Get candidate and directly resolved indexes for logged cases.

    Arguments:
        pair_indexes: reference-pair positions keyed by subtitle text
        test_cases: logged delineation test cases
    Returns:
        candidate and directly resolved indexes for every logged case
    Raises:
        ScinoephileError: if a logged reference pair is absent
    """
    target_pairs_by_reference_pair: dict[
        tuple[str, str],
        set[tuple[str, str]],
    ] = defaultdict(set)
    for test_case in test_cases:
        query = test_case.query
        reference_pair = (query.reference_one, query.reference_two)
        target_pair = (query.target_one, query.target_two)
        target_pairs_by_reference_pair[reference_pair].add(target_pair)
    superseded_pairs = get_superseded_keys(
        pair_indexes,
        target_pairs_by_reference_pair,
    )
    candidate_indexes_by_case: list[list[int]] = []
    direct_indexes: list[int | None] = []
    for test_case_index, test_case in enumerate(test_cases, 1):
        query = test_case.query
        pair = (query.reference_one, query.reference_two)
        matches = pair_indexes.get(pair, [])
        if not matches:
            if pair in superseded_pairs:
                candidate_indexes_by_case.append([])
                direct_indexes.append(None)
                continue
            raise ScinoephileError(
                "Unable to audit transcription delineation: "
                f"test case {test_case_index} reference pair was not found in "
                "reference subtitles"
            )

        candidate_indexes = list(matches)
        candidate_indexes_by_case.append(candidate_indexes)
        direct_index = None
        if len(candidate_indexes) == 1:
            direct_index = candidate_indexes[0]
        direct_indexes.append(direct_index)
    return candidate_indexes_by_case, direct_indexes


def _get_selected_case_index(
    candidate_indexes: Sequence[int],
    direct_indexes: list[int | None],
    selected_reference_indexes: Collection[int],
    *,
    test_case_index: int,
) -> int | None:
    """Resolve one case globally and retain it only when selected.

    Arguments:
        candidate_indexes: possible zero-indexed reference-pair positions
        direct_indexes: directly resolved indexes for every logged case
        selected_reference_indexes: selected zero-based reference subtitle indexes
        test_case_index: one-indexed test case position
    Returns:
        selected reference-pair position, or None if outside the requested range
    """
    selected_candidate_indexes = {
        index
        for index in candidate_indexes
        if index in selected_reference_indexes
        and index + 1 in selected_reference_indexes
    }
    if not selected_candidate_indexes:
        return None

    index = _get_case_index(
        candidate_indexes,
        direct_indexes,
        test_case_index=test_case_index,
    )
    if index not in selected_candidate_indexes:
        return None
    return index
