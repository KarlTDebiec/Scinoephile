#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit transcription punctuation decisions and format them as Markdown."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.core.text import remove_punc_and_whitespace
from scinoephile.llms.punctuation import PunctuationTestCase

from .utils import (
    AuditFilter,
    AuditResult,
    format_audit_report,
    get_selected_event_indexes,
    get_superseded_keys,
    resolve_contextual_index,
)

__all__ = ["audit_punctuation"]


def audit_punctuation(
    reference: Series,
    target: Series,
    test_cases: Sequence[PunctuationTestCase],
    *,
    row_filter: AuditFilter = AuditFilter.all,
    first_index: int | None = None,
    last_index: int | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
) -> str:
    """Audit logged punctuation decisions against their reference subtitles.

    The target series is used only to disambiguate repeated reference text.

    Arguments:
        reference: reference subtitle series used to guide punctuation
        target: punctuated target series aligned to the reference by timing
        test_cases: logged punctuation test cases
        row_filter: row status filter
        first_index: first 1-indexed reference subtitle number to include
        last_index: last 1-indexed reference subtitle number to include
        first_block: first 1-indexed reference block number to include
        last_block: last 1-indexed reference block number to include
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if a logged case cannot be matched uniquely
    """
    reference_indexes_by_text: dict[str, list[int]] = defaultdict(list)
    for index, subtitle in enumerate(reference):
        reference_indexes_by_text[subtitle.text].append(index)

    target_text_by_reference_index = _get_target_text_by_reference_index(
        reference,
        target,
    )
    candidate_indexes_by_case, direct_indexes = _get_case_indexes(
        reference_indexes_by_text,
        target_text_by_reference_index,
        test_cases,
    )
    selected_reference_indexes = get_selected_event_indexes(
        reference,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )

    rows: list[tuple[int, int, tuple[str, ...]]] = []
    changes = 0
    unchanged = 0
    unanswered = 0
    logged_cases = 0
    for test_case_index, test_case in enumerate(test_cases, 1):
        candidates = candidate_indexes_by_case[test_case_index - 1]
        if not candidates:
            continue
        if selected_reference_indexes.isdisjoint(candidates):
            continue
        index = _get_case_index(
            candidates,
            direct_indexes,
            test_case_index=test_case_index,
        )
        if index not in selected_reference_indexes:
            continue

        logged_cases += 1
        row, result = _format_case_row(test_case, index)
        if result is AuditResult.unanswered:
            unanswered += 1
        elif result is AuditResult.unchanged:
            unchanged += 1
        else:
            changes += 1

        if (
            row_filter is AuditFilter.changes and result is not AuditResult.changed
        ) or (row_filter is AuditFilter.unverified and test_case.verified):
            continue
        rows.append((index, test_case_index, row))

    rows.sort(key=lambda item: (item[0], item[1]))
    return format_audit_report(
        title="Transcription Punctuation Audit",
        summary_items=(
            f"logged cases: {logged_cases}",
            f"punctuation changes: {changes}",
            f"unchanged answers: {unchanged}",
            f"unanswered cases: {unanswered}",
            f"row filter: {row_filter.value}",
        ),
        columns=(
            ("Index", "right"),
            ("Reference", "left"),
            ("Input", "left"),
            ("Output", "left"),
            ("Notes", "left"),
            ("Verified", "center"),
        ),
        rows=[row for _, _, row in rows],
        first_index=first_index,
        last_index=last_index,
        index_track_name="reference",
        first_block=first_block,
        last_block=last_block,
    )


def _format_case_row(
    test_case: PunctuationTestCase,
    index: int,
) -> tuple[tuple[str, ...], AuditResult]:
    """Format one punctuation case as semantic table data.

    Arguments:
        test_case: punctuation case to format
        index: zero-indexed reference subtitle position
    Returns:
        semantic table cells and their result type
    """
    input_text = "".join(test_case.query.subtitles)
    answer = test_case.answer
    if answer is None:
        output = "(unanswered)"
        result = AuditResult.unanswered
    elif answer.output == input_text:
        output = ""
        result = AuditResult.unchanged
    else:
        output = answer.output
        result = AuditResult.changed

    verified_marker = ""
    if test_case.verified:
        verified_marker = "✓"
    cells = (
        str(index + 1),
        test_case.query.guide,
        "\n".join(test_case.query.subtitles),
        output,
        "",
        verified_marker,
    )
    return cells, result


def _get_case_index(
    candidates: Sequence[int],
    direct_indexes: list[int | None],
    *,
    test_case_index: int,
) -> int:
    """Resolve the reference index for one punctuation test case.

    Arguments:
        candidates: possible zero-indexed reference subtitle positions
        direct_indexes: indexes resolved directly for all logged cases
        test_case_index: one-indexed position of the case being resolved
    Returns:
        resolved zero-indexed reference subtitle position
    Raises:
        ScinoephileError: if the case remains ambiguous
    """
    index = resolve_contextual_index(
        candidates,
        direct_indexes,
        test_case_index - 1,
    )
    if index is not None:
        return index

    indexes = ", ".join(str(candidate + 1) for candidate in candidates)
    raise ScinoephileError(
        "Unable to audit transcription punctuation: "
        f"test case {test_case_index} is ambiguous; it matches subtitle "
        f"indexes {indexes}"
    )


def _get_case_indexes(
    reference_indexes_by_text: dict[str, list[int]],
    target_text_by_reference_index: dict[int, str],
    test_cases: Sequence[PunctuationTestCase],
) -> tuple[list[list[int]], list[int | None]]:
    """Get candidate and directly resolved reference indexes for all cases.

    Arguments:
        reference_indexes_by_text: reference positions keyed by subtitle text
        target_text_by_reference_index: target text aligned to reference positions
        test_cases: logged punctuation test cases
    Returns:
        candidate indexes and directly resolved indexes for each case
    Raises:
        ScinoephileError: if a case's reference subtitle is absent
    """
    inputs_by_guide: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for test_case in test_cases:
        inputs_by_guide[test_case.query.guide].add(tuple(test_case.query.subtitles))
    superseded_guides = get_superseded_keys(
        reference_indexes_by_text,
        inputs_by_guide,
    )
    candidate_indexes_by_case: list[list[int]] = []
    direct_indexes: list[int | None] = []
    for test_case_index, test_case in enumerate(test_cases, 1):
        matches = reference_indexes_by_text.get(test_case.query.guide, [])
        if not matches:
            if test_case.query.guide in superseded_guides:
                candidate_indexes_by_case.append([])
                direct_indexes.append(None)
                continue
            raise ScinoephileError(
                "Unable to audit transcription punctuation: "
                f"test case {test_case_index} reference subtitle was not found"
            )
        candidates = list(matches)
        candidate_indexes_by_case.append(candidates)

        direct_index = None
        if len(candidates) == 1:
            direct_index = candidates[0]
        elif candidates:
            input_chars = remove_punc_and_whitespace("".join(test_case.query.subtitles))
            target_chars_by_index = {
                index: remove_punc_and_whitespace(
                    target_text_by_reference_index.get(index, "")
                )
                for index in candidates
            }
            target_matches = [
                index
                for index, target_chars in target_chars_by_index.items()
                if target_chars == input_chars
            ]
            if len(target_matches) == 1:
                direct_index = target_matches[0]
            else:
                contained_target_lengths = {
                    index: len(target_chars)
                    for index, target_chars in target_chars_by_index.items()
                    if target_chars and target_chars in input_chars
                }
                if contained_target_lengths:
                    maximum_length = max(contained_target_lengths.values())
                    longest_matches = [
                        index
                        for index, length in contained_target_lengths.items()
                        if length == maximum_length
                    ]
                    if len(longest_matches) == 1:
                        direct_index = longest_matches[0]
        direct_indexes.append(direct_index)
    return candidate_indexes_by_case, direct_indexes


def _get_target_text_by_reference_index(
    reference: Series,
    target: Series,
) -> dict[int, str]:
    """Align target text to reference indexes by exact timing.

    Arguments:
        reference: reference subtitle series
        target: punctuated target subtitle series
    Returns:
        concatenated target text keyed by zero-indexed reference position
    """
    target_texts_by_timing: dict[tuple[int, int], list[str]] = defaultdict(list)
    for subtitle in target:
        target_texts_by_timing[(subtitle.start, subtitle.end)].append(subtitle.text)
    return {
        index: "".join(target_texts_by_timing.get((subtitle.start, subtitle.end), []))
        for index, subtitle in enumerate(reference)
    }
