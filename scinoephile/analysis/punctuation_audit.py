#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit transcription punctuation decisions and format them as Markdown."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from enum import StrEnum

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.core.text import remove_punc_and_whitespace
from scinoephile.llms.punctuation import PunctuationTestCase

__all__ = [
    "PunctuationAuditFilter",
    "audit_punctuation",
]


class PunctuationAuditFilter(StrEnum):
    """Row filters supported by a transcription punctuation audit."""

    all = "all"
    """Include every logged punctuation decision."""

    changes = "changes"
    """Include only decisions that changed punctuation or whitespace."""


class _PunctuationResult(StrEnum):
    """Result types used to summarize punctuation audit rows."""

    changed = "changed"
    unchanged = "unchanged"
    unanswered = "unanswered"


def audit_punctuation(
    reference: Series,
    target: Series,
    test_cases: Sequence[PunctuationTestCase],
    *,
    row_filter: PunctuationAuditFilter = PunctuationAuditFilter.all,
    first_index: int | None = None,
    last_index: int | None = None,
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

    rows: list[tuple[int, int, str]] = []
    changes = 0
    unchanged = 0
    unanswered = 0
    logged_cases = 0
    for test_case_index, test_case in enumerate(test_cases, 1):
        candidates = candidate_indexes_by_case[test_case_index - 1]
        if not candidates:
            continue
        if not any(
            (first_index is None or candidate + 1 >= first_index)
            and (last_index is None or candidate + 1 <= last_index)
            for candidate in candidates
        ):
            continue
        index = _get_case_index(
            candidates,
            direct_indexes,
            test_case_index=test_case_index,
        )
        if (first_index is not None and index + 1 < first_index) or (
            last_index is not None and index + 1 > last_index
        ):
            continue

        logged_cases += 1
        row, result = _format_case_row(test_case, index)
        if result is _PunctuationResult.unanswered:
            unanswered += 1
        elif result is _PunctuationResult.unchanged:
            unchanged += 1
        else:
            changes += 1

        if (
            row_filter is PunctuationAuditFilter.changes
            and result is not _PunctuationResult.changed
        ):
            continue
        rows.append((index, test_case_index, row))

    rows.sort(key=lambda item: (item[0], item[1]))
    lines = [
        "# Transcription Punctuation Audit",
        "",
        "## Summary",
        "",
        f"- logged cases: {logged_cases}",
        f"- punctuation changes: {changes}",
        f"- unchanged answers: {unchanged}",
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
            "| Index | Reference | Input | Output | Notes | Verified |",
            "|---:|---|---|---|---|:---:|",
            *(row for _, _, row in rows),
        )
    )
    return "\n".join(lines) + "\n"


def _format_case_row(
    test_case: PunctuationTestCase,
    index: int,
) -> tuple[str, _PunctuationResult]:
    """Format one punctuation case as a Markdown table row.

    Arguments:
        test_case: punctuation case to format
        index: zero-indexed reference subtitle position
    Returns:
        Markdown row and its result type
    """
    input_text = "".join(test_case.query.subtitles)
    answer = test_case.answer
    if answer is None:
        output = "(unanswered)"
        result = _PunctuationResult.unanswered
    elif answer.output == input_text:
        output = ""
        result = _PunctuationResult.unchanged
    else:
        output = answer.output
        result = _PunctuationResult.changed

    cells = (
        str(index + 1),
        test_case.query.guide,
        "\n".join(test_case.query.subtitles),
        output,
        "",
        "✓" if test_case.verified else "",
    )
    row = f"| {' | '.join(_escape_cell(cell) for cell in cells)} |"
    return row, result


def _get_case_index(
    candidates: Sequence[int],
    direct_indexes: Sequence[int | None],
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
    index = direct_indexes[test_case_index - 1]
    if index is None:
        index = _get_contextual_index(
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
    superseded_guides = _get_superseded_guides(
        reference_indexes_by_text,
        test_cases,
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


def _get_superseded_guides(
    reference_indexes_by_text: dict[str, list[int]],
    test_cases: Sequence[PunctuationTestCase],
) -> set[str]:
    """Get historical guide texts replaced by current logged cases.

    Test-case persistence retains queries that are no longer encountered. Link
    guide texts through their target inputs so a current query identifies
    earlier cases superseded by guide-text revisions.

    Arguments:
        reference_indexes_by_text: current reference positions keyed by text
        test_cases: logged punctuation test cases
    Returns:
        historical guide texts superseded by current logged cases
    """
    inputs_by_guide: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    current_inputs: set[tuple[str, ...]] = set()
    for test_case in test_cases:
        guide = test_case.query.guide
        inputs = tuple(test_case.query.subtitles)
        inputs_by_guide[guide].add(inputs)
        if guide in reference_indexes_by_text:
            current_inputs.add(inputs)

    superseded_guides: set[str] = set()
    changed = True
    while changed:
        changed = False
        for guide, inputs in inputs_by_guide.items():
            if guide in reference_indexes_by_text or guide in superseded_guides:
                continue
            if inputs.isdisjoint(current_inputs):
                continue
            superseded_guides.add(guide)
            current_inputs.update(inputs)
            changed = True
    return superseded_guides


def _escape_cell(value: str) -> str:
    """Escape one Markdown table cell.

    Arguments:
        value: cell text
    Returns:
        escaped cell text
    """
    return value.replace("\\N", "\n").replace("\n", "<br>").replace("|", "\\|")


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


def _get_contextual_index(
    candidates: Sequence[int],
    direct_indexes: Sequence[int | None],
    test_case_index: int,
) -> int | None:
    """Resolve repeated reference text from neighboring logged cases.

    Arguments:
        candidates: possible zero-indexed reference subtitle positions
        direct_indexes: indexes resolved directly for all logged cases
        test_case_index: zero-indexed position of the case being resolved
    Returns:
        uniquely resolved reference index, or None if ambiguity remains
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

    narrowed_candidates = list(candidates)
    if (
        previous_index is not None
        and next_index is not None
        and previous_index <= next_index
    ):
        narrowed_candidates = [
            candidate
            for candidate in candidates
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
