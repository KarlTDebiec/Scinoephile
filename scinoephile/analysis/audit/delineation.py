#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit transcription delineation decisions and format them as Markdown."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Collection, Sequence
from enum import StrEnum
from typing import cast

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.llms.block_delineation import BlockDelineationTestCase
from scinoephile.llms.delineation import DelineationTestCase

from .utils import (
    AuditResult,
    format_audit_report,
    format_verification_marker,
    get_reference_sequence_start_indexes,
    get_selected_event_indexes,
    get_superseded_keys,
    resolve_contextual_index,
)

__all__ = ["DelineationAuditFilter", "audit_delineation"]


class DelineationAuditFilter(StrEnum):
    """Row filters supported by a transcription delineation audit."""

    all = "all"
    """Include every eligible row."""

    changes = "changes"
    """Include only rows that shift a subtitle boundary."""

    unverified = "unverified"
    """Include only rows from cases not marked as verified."""


def audit_delineation(
    reference: Series,
    test_cases: Sequence[DelineationTestCase | BlockDelineationTestCase],
    *,
    row_filter: DelineationAuditFilter = DelineationAuditFilter.all,
    first_index: int | None = None,
    last_index: int | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
) -> str:
    """Audit logged transcription boundary decisions against their reference.

    Arguments:
        reference: reference subtitle series used to guide transcription
        test_cases: logged pairwise or block-level delineation test cases
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
    block_test_cases = [
        test_case
        for test_case in test_cases
        if isinstance(test_case, BlockDelineationTestCase)
    ]
    if block_test_cases:
        if len(block_test_cases) != len(test_cases):
            raise ScinoephileError(
                "Unable to audit transcription delineation: JSON mixes pairwise "
                "and block-level test cases"
            )
        return _audit_block_delineation(
            reference,
            block_test_cases,
            row_filter=row_filter,
            first_index=first_index,
            last_index=last_index,
            first_block=first_block,
            last_block=last_block,
        )

    pairwise_test_cases = cast("Sequence[DelineationTestCase]", test_cases)
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
        pair_indexes, pairwise_test_cases
    )

    rows: list[tuple[int, tuple[str, ...]]] = []
    shifts = 0
    no_shifts = 0
    unanswered = 0
    logged_cases = 0
    for test_case_index, test_case in enumerate(pairwise_test_cases, 1):
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
            row_filter is DelineationAuditFilter.changes
            and result is not AuditResult.changed
        ) or (row_filter is DelineationAuditFilter.unverified and test_case.verified):
            continue

        verified_marker = format_verification_marker(test_case.verified)
        cells = (
            f"{first_subtitle_index}\n{second_subtitle_index}",
            _format_pair(query.reference_one, query.reference_two),
            _format_pair(*input_target),
            output,
            "",
            verified_marker,
        )
        rows.append((first_subtitle_index, cells))

    rows.sort(key=lambda item: item[0])

    return format_audit_report(
        title="Transcription Delineation Audit",
        summary_items=(
            f"logged cases: {logged_cases}",
            f"boundary shifts: {shifts}",
            f"no-shift answers: {no_shifts}",
            f"unanswered cases: {unanswered}",
            f"row filter: {row_filter.value}",
        ),
        columns=(
            ("Indexes", "right"),
            ("Reference", "left"),
            ("Input", "left"),
            ("Output", "left"),
            ("Notes", "left"),
            ("Verified", "center"),
        ),
        rows=[row for _, row in rows],
        first_index=first_index,
        last_index=last_index,
        index_track_name="reference",
        first_block=first_block,
        last_block=last_block,
    )


def _audit_block_delineation(
    reference: Series,
    test_cases: Sequence[BlockDelineationTestCase],
    *,
    row_filter: DelineationAuditFilter,
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
) -> str:
    """Audit complete block-level delineation cases as sparse block decisions.

    Arguments:
        reference: reference subtitle series used to guide transcription
        test_cases: logged block-level delineation test cases
        row_filter: row status filter
        first_index: first 1-indexed reference subtitle number to include
        last_index: last 1-indexed reference subtitle number to include
        first_block: first 1-indexed reference block number to include
        last_block: last 1-indexed reference block number to include
    Returns:
        Markdown audit report with one row per block case
    Raises:
        ScinoephileError: if a logged guide block cannot be matched uniquely
    """
    start_indexes_by_case, direct_start_indexes = _get_block_delineation_start_indexes(
        reference, test_cases
    )
    selected_reference_indexes = get_selected_event_indexes(
        reference,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )
    rows, logged_cases, shifts, no_shifts, unanswered = _get_block_delineation_rows(
        test_cases,
        start_indexes_by_case,
        direct_start_indexes,
        selected_reference_indexes,
        row_filter,
    )
    rows.sort(key=lambda item: item[0])
    return format_audit_report(
        title="Transcription Delineation Audit",
        summary_items=(
            f"logged cases: {logged_cases}",
            f"changed answers: {shifts}",
            f"no-change answers: {no_shifts}",
            f"unanswered cases: {unanswered}",
            "block view: one row per case; Output lists reconstructed changes",
            f"row filter: {row_filter.value}",
        ),
        columns=(
            ("Indexes", "right"),
            ("Reference", "left"),
            ("Input", "left"),
            ("Output", "left"),
            ("Notes", "left"),
            ("Verified", "center"),
        ),
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
    one_display = one if one else "(empty)"
    two_display = two if two else "(empty)"
    return f"{one_display}\n{two_display}"


def _format_indexed_texts(texts: Sequence[str]) -> str:
    """Format block texts with one-based local indexes.

    Arguments:
        texts: block texts in index order
    Returns:
        newline-separated indexed texts
    """
    return "\n".join(
        f"{index}. {text if text else '(empty)'}" for index, text in enumerate(texts, 1)
    )


def _format_window_indexed_texts(
    texts: Sequence[str], owned_index_range: Collection[int]
) -> str:
    """Format window texts and distinguish owned indexes from context.

    Arguments:
        texts: window texts in local index order
        owned_index_range: one-based local indexes whose following boundaries are owned
    Returns:
        newline-separated indexed texts with ownership markers
    """
    return "\n".join(
        f"{index}. "
        f"{'[owns next boundary] ' if index in owned_index_range else '[context] '}"
        f"{text if text else '(empty)'}"
        for index, text in enumerate(texts, 1)
    )


def _format_block_window_cells(
    test_case: BlockDelineationTestCase,
    test_case_index: int,
    start_index: int,
    output: str,
) -> tuple[str, ...]:
    """Format one complete block or overlapping window row.

    Arguments:
        test_case: block delineation case
        test_case_index: one-based case number
        start_index: zero-based global reference start
        output: formatted sparse output
    Returns:
        six semantic audit table cells
    """
    query = test_case.query
    last_reference_index = start_index + len(query.guides) - 1
    reference_range = str(start_index + 1)
    if last_reference_index != start_index:
        reference_range = f"{start_index + 1}–{last_reference_index + 1}"

    owned_local_indexes = query.owned_index_range
    owned_start_index = start_index + owned_local_indexes.start - 1
    owned_end_index = start_index + owned_local_indexes.stop - 2
    owned_range = str(owned_start_index + 1)
    if owned_end_index != owned_start_index:
        owned_range = f"{owned_start_index + 1}–{owned_end_index + 1}"

    index_cell = f"Case {test_case_index}\nRefs {reference_range}"
    reference_texts = [guide.text for guide in query.guides]
    input_texts = [target.text for target in query.targets]
    if query.first_owned_index is not None:
        index_cell += f"\nOwns boundaries after refs {owned_range}"
        reference_cell = _format_window_indexed_texts(
            reference_texts, owned_local_indexes
        )
        input_cell = _format_window_indexed_texts(input_texts, owned_local_indexes)
    else:
        reference_cell = _format_indexed_texts(reference_texts)
        input_cell = _format_indexed_texts(input_texts)
    return (
        index_cell,
        reference_cell,
        input_cell,
        output,
        "",
        format_verification_marker(test_case.verified),
    )


def _get_block_case_start_index(
    candidate_start_indexes: Sequence[int],
    direct_start_indexes: list[int | None],
    *,
    test_case_index: int,
) -> int:
    """Resolve one block case's reference start index.

    Arguments:
        candidate_start_indexes: possible zero-indexed reference start positions
        direct_start_indexes: directly resolved starts for every logged case
        test_case_index: one-indexed test case position
    Returns:
        uniquely resolved zero-indexed reference start position
    Raises:
        ScinoephileError: if a block case remains ambiguous
    """
    start_index = resolve_contextual_index(
        candidate_start_indexes, direct_start_indexes, test_case_index - 1
    )
    if start_index is not None:
        return start_index

    indexes = ", ".join(str(index + 1) for index in candidate_start_indexes)
    raise ScinoephileError(
        "Unable to audit transcription delineation: "
        f"test case {test_case_index} guide block is ambiguous; "
        f"it begins at subtitle indexes {indexes}"
    )


def _get_block_delineation_rows(
    test_cases: Sequence[BlockDelineationTestCase],
    start_indexes_by_case: Sequence[Sequence[int]],
    direct_start_indexes: list[int | None],
    selected_reference_indexes: Collection[int],
    row_filter: DelineationAuditFilter,
) -> tuple[list[tuple[int, tuple[str, ...]]], int, int, int, int]:
    """Format block cases as sparse delineation audit rows.

    Arguments:
        test_cases: logged block-level delineation cases
        start_indexes_by_case: possible reference start positions for each case
        direct_start_indexes: directly resolved starts for every case
        selected_reference_indexes: reference positions selected for the report
        row_filter: row status filter
    Returns:
        rows and logged, changed, unchanged, and unanswered case counts
    """
    rows: list[tuple[int, tuple[str, ...]]] = []
    shifts = 0
    no_shifts = 0
    unanswered = 0
    logged_cases = 0
    for test_case_index, test_case in enumerate(test_cases, 1):
        owned_local_indexes = test_case.query.owned_index_range
        first_owned_offset = owned_local_indexes.start - 1
        last_owned_offset = owned_local_indexes.stop - 2
        selected_start_indexes = {
            start_index
            for start_index in start_indexes_by_case[test_case_index - 1]
            if all(
                reference_index in selected_reference_indexes
                for reference_index in range(
                    start_index + first_owned_offset,
                    start_index + last_owned_offset + 1,
                )
            )
        }
        if not selected_start_indexes:
            continue
        start_index = _get_block_case_start_index(
            start_indexes_by_case[test_case_index - 1],
            direct_start_indexes,
            test_case_index=test_case_index,
        )
        if start_index not in selected_start_indexes:
            continue

        logged_cases += 1
        answer = test_case.answer
        if answer is None:
            output = "(unanswered)"
            unanswered += 1
            result = AuditResult.unanswered
        elif answer.changes:
            input_texts = [target.text for target in test_case.query.targets]
            output_texts = test_case.get_output_texts()
            output = "\n".join(
                f"{index}. {output_text if output_text else '(empty)'}"
                for index, (input_text, output_text) in enumerate(
                    zip(input_texts, output_texts, strict=True), 1
                )
                if output_text != input_text
            )
            shifts += 1
            result = AuditResult.changed
        else:
            output = ""
            no_shifts += 1
            result = AuditResult.unchanged

        if (
            row_filter is DelineationAuditFilter.changes
            and result is not AuditResult.changed
        ) or (row_filter is DelineationAuditFilter.unverified and test_case.verified):
            continue

        cells = _format_block_window_cells(
            test_case, test_case_index, start_index, output
        )
        rows.append((start_index, cells))

    return rows, logged_cases, shifts, no_shifts, unanswered


def _get_block_delineation_start_indexes(
    reference: Series, test_cases: Sequence[BlockDelineationTestCase]
) -> tuple[list[list[int]], list[int | None]]:
    """Locate block delineation cases within the reference series.

    Arguments:
        reference: reference subtitle series used to guide transcription
        test_cases: logged block-level delineation cases
    Returns:
        candidate and directly resolved start indexes for every case
    Raises:
        ScinoephileError: if a logged guide block is absent
    """
    guide_sequences = [
        [guide.text for guide in test_case.query.guides] for test_case in test_cases
    ]
    start_indexes_by_case = get_reference_sequence_start_indexes(
        reference, guide_sequences
    )
    direct_start_indexes: list[int | None] = []
    for test_case_index, start_indexes in enumerate(start_indexes_by_case, 1):
        if not start_indexes:
            raise ScinoephileError(
                "Unable to audit transcription delineation: "
                f"test case {test_case_index} guide block was not found in "
                "reference subtitles"
            )
        direct_start_index = None
        if len(start_indexes) == 1:
            direct_start_index = start_indexes[0]
        direct_start_indexes.append(direct_start_index)
    return start_indexes_by_case, direct_start_indexes


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
        candidate_indexes, direct_indexes, test_case_index - 1
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
    target_pairs_by_reference_pair: dict[tuple[str, str], set[tuple[str, str]]] = (
        defaultdict(set)
    )
    for test_case in test_cases:
        query = test_case.query
        reference_pair = (query.reference_one, query.reference_two)
        target_pair = (query.target_one, query.target_two)
        target_pairs_by_reference_pair[reference_pair].add(target_pair)
    superseded_pairs = get_superseded_keys(pair_indexes, target_pairs_by_reference_pair)
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
        candidate_indexes, direct_indexes, test_case_index=test_case_index
    )
    if index not in selected_candidate_indexes:
        return None
    return index
