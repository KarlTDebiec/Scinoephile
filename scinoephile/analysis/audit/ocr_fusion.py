#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit OCR-fusion decisions and format the results as Markdown."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import are_series_one_to_one

from .utils import (
    escape_table_cell,
    format_block_range,
    format_index_range,
    get_selected_event_indexes,
)

__all__ = [
    "OcrFusionAuditFilter",
    "audit_ocr_fusion",
]


@dataclass(frozen=True, kw_only=True)
class _OcrFusionRow:
    """One OCR-fusion subtitle displayed in the audit report."""

    changed: bool
    """Whether the two OCR sources differ."""
    discrepancy: bool
    """Whether fused and validated text differ."""
    markdown: str
    """Formatted Markdown table row."""
    requires_llm: bool
    """Whether the row required an OCR-fusion LLM decision."""
    verified: bool
    """Whether the associated LLM case is verified."""


@dataclass(frozen=True, kw_only=True)
class _OcrFusionDecision:
    """Resolved decision metadata for one fused subtitle."""

    case_index: int | None
    """One-based JSON case position, if the LLM was used."""
    difficulty: int
    """Difficulty of the associated LLM case."""
    note: str
    """Logged or automatic note for the fused output."""
    requires_llm: bool
    """Whether the source pair required an LLM decision."""
    verified: bool
    """Whether the associated LLM case is verified."""


class _OcrFusionAnswer(Protocol):
    """OCR-fusion answer fields required for audit reporting."""

    @property
    def note(self) -> str:
        """Note recorded for the fusion decision."""
        ...

    @property
    def output(self) -> str:
        """Selected fused subtitle text."""
        ...


class _OcrFusionQuery(Protocol):
    """OCR-fusion query fields required for audit reporting."""

    @property
    def source_one(self) -> str:
        """Text from the first OCR source."""
        ...

    @property
    def source_two(self) -> str:
        """Text from the second OCR source."""
        ...


class _OcrFusionTestCase(Protocol):
    """OCR-fusion test-case fields required for audit reporting."""

    @property
    def answer(self) -> _OcrFusionAnswer | None:
        """Optional decision answer."""
        ...

    @property
    def difficulty(self) -> int:
        """Decision difficulty."""
        ...

    @property
    def query(self) -> _OcrFusionQuery:
        """OCR source texts."""
        ...

    @property
    def verified(self) -> bool:
        """Whether the decision has been reviewed."""
        ...


class OcrFusionAuditFilter(StrEnum):
    """Row filters supported by an OCR-fusion audit."""

    all = "all"
    """Include every fused subtitle."""

    changes = "changes"
    """Include only subtitles whose OCR sources differ."""

    discrepancies = "discrepancies"
    """Include only subtitles that differ from the validated track."""

    unverified = "unverified"
    """Include only LLM decisions not marked as verified."""


def audit_ocr_fusion(
    source_one: Series,
    source_two: Series,
    fused: Series,
    test_cases: Sequence[_OcrFusionTestCase] | None = None,
    *,
    validated: Series | None = None,
    row_filter: OcrFusionAuditFilter = OcrFusionAuditFilter.changes,
    first_index: int | None = None,
    last_index: int | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
) -> str:
    """Audit OCR-fusion output against its sources and optional validated truth.

    Arguments:
        source_one: first OCR subtitle series provided for fusion
        source_two: second OCR subtitle series provided for fusion
        fused: OCR-fusion output subtitle series
        test_cases: optional logged OCR-fusion test cases
        validated: optional validated subtitle series used as ground truth
        row_filter: row status filter
        first_index: first 1-indexed fused subtitle number to include
        last_index: last 1-indexed fused subtitle number to include
        first_block: first 1-indexed fused block number to include
        last_block: last 1-indexed fused block number to include
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if ranges, series alignment, or logged decisions are invalid
    """
    if row_filter is OcrFusionAuditFilter.discrepancies and validated is None:
        raise ScinoephileError(
            "OCR-fusion discrepancy filtering requires a validated subtitle track"
        )

    selected_positions = get_selected_event_indexes(
        fused,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )

    _validate_alignment(source_one, source_two, "Source two")
    _validate_alignment(source_one, fused, "Fused")
    if validated is not None:
        _validate_alignment(source_one, validated, "Validated")

    has_decision_log = test_cases is not None
    cases_by_key: dict[tuple[str, str], tuple[int, _OcrFusionTestCase]] = {}
    for case_index, test_case in enumerate(test_cases or (), 1):
        key = (test_case.query.source_one, test_case.query.source_two)
        cases_by_key[key] = (case_index, test_case)

    all_rows: list[_OcrFusionRow] = []
    for position in sorted(selected_positions):
        index = position + 1
        source_one_text = source_one.events[position].text_with_newline
        source_two_text = source_two.events[position].text_with_newline
        fused_text = fused.events[position].text_with_newline
        validated_text = None
        if validated is not None:
            validated_text = validated.events[position].text_with_newline

        decision = _get_decision(
            index,
            source_one_text,
            source_two_text,
            fused_text,
            cases_by_key,
            has_decision_log=has_decision_log,
        )
        discrepancy = validated_text is not None and fused_text != validated_text
        cells = (
            str(index),
            str(decision.case_index) if decision.case_index is not None else "—",
            str(decision.difficulty) if decision.case_index is not None else "—",
            source_one_text or "—",
            source_two_text or "—",
            fused_text or "—",
            validated_text if validated_text else "—",
        )
        if has_decision_log:
            cells += (
                decision.note,
                "✓" if decision.requires_llm and decision.verified else "",
            )
        markdown_cells = " | ".join(escape_table_cell(cell) for cell in cells)
        all_rows.append(
            _OcrFusionRow(
                changed=source_one_text != source_two_text,
                discrepancy=discrepancy,
                markdown=f"| {markdown_cells} |",
                requires_llm=decision.requires_llm,
                verified=decision.verified,
            )
        )

    rows = _filter_rows(all_rows, row_filter)
    llm_rows = [row for row in all_rows if row.requires_llm]
    lines = [
        "# OCR Fusion Audit",
        "",
        "## Summary",
        "",
        f"- subtitles: {len(all_rows)}",
        f"- source disagreements: {sum(row.changed for row in all_rows)}",
        f"- LLM decisions: {len(llm_rows)}",
        f"- validated track: {'included' if validated is not None else 'omitted'}",
        f"- validated discrepancies: {sum(row.discrepancy for row in all_rows)}",
        f"- row filter: {row_filter.value}",
    ]
    if has_decision_log:
        verified_llm_rows = sum(row.verified for row in llm_rows)
        unverified_llm_rows = sum(not row.verified for row in llm_rows)
        lines.extend(
            (
                f"- verified LLM decisions: {verified_llm_rows}",
                f"- unverified LLM decisions: {unverified_llm_rows}",
            )
        )
    else:
        lines.append("- decision log: omitted")
    range_summary = format_index_range(
        first_index,
        last_index,
        track_name="fused",
    )
    if range_summary is not None:
        lines.append(range_summary)
    block_range_summary = format_block_range(first_block, last_block)
    if block_range_summary is not None:
        lines.append(block_range_summary)
    column_labels = [
        "Index",
        "Case",
        "Difficulty",
        "Source one",
        "Source two",
        "Fused",
        "Validated",
    ]
    column_separators = ["---:", "---:", "---:", "---", "---", "---", "---"]
    if has_decision_log:
        column_labels.extend(("Notes", "Verified"))
        column_separators.extend(("---", ":---:"))
    lines.extend(
        (
            f"- table rows: {len(rows)}",
            "",
            "## Audit Table",
            "",
            f"| {' | '.join(column_labels)} |",
            f"|{'|'.join(column_separators)}|",
            *(row.markdown for row in rows),
        )
    )
    return "\n".join(lines) + "\n"


def _filter_rows(
    rows: Sequence[_OcrFusionRow],
    row_filter: OcrFusionAuditFilter,
) -> list[_OcrFusionRow]:
    """Filter OCR-fusion rows by their status.

    Arguments:
        rows: eligible rows
        row_filter: active row filter
    Returns:
        filtered rows
    """
    if row_filter is OcrFusionAuditFilter.all:
        return list(rows)
    if row_filter is OcrFusionAuditFilter.changes:
        return [row for row in rows if row.changed]
    if row_filter is OcrFusionAuditFilter.discrepancies:
        return [row for row in rows if row.discrepancy]
    return [row for row in rows if row.requires_llm and not row.verified]


def _get_automatic_output(source_one_text: str, source_two_text: str) -> str:
    """Get the deterministic fusion output for a pair not sent to the LLM.

    Arguments:
        source_one_text: first source text
        source_two_text: second source text
    Returns:
        automatic fused text
    """
    if source_one_text:
        return source_one_text
    return source_two_text


def _get_automatic_note(source_one_text: str, source_two_text: str) -> str:
    """Describe the deterministic fusion decision for a source pair.

    Arguments:
        source_one_text: first source text
        source_two_text: second source text
    Returns:
        automatic decision note
    """
    if not source_one_text and not source_two_text:
        return "Both sources empty"
    if source_one_text == source_two_text:
        return "Sources identical"
    if source_one_text:
        return "Source two empty"
    return "Source one empty"


def _get_decision(
    index: int,
    source_one_text: str,
    source_two_text: str,
    fused_text: str,
    cases_by_key: dict[tuple[str, str], tuple[int, _OcrFusionTestCase]],
    *,
    has_decision_log: bool,
) -> _OcrFusionDecision:
    """Resolve and validate one automatic or LLM fusion decision.

    Arguments:
        index: one-based fused subtitle index
        source_one_text: first source text
        source_two_text: second source text
        fused_text: fused output text
        cases_by_key: latest logged case keyed by source text pair
        has_decision_log: whether a decision log was supplied
    Returns:
        resolved decision metadata
    Raises:
        ScinoephileError: if the fused output lacks or conflicts with its decision
    """
    requires_llm = bool(
        source_one_text and source_two_text and source_one_text != source_two_text
    )
    if not requires_llm:
        expected_output = _get_automatic_output(source_one_text, source_two_text)
        if expected_output != fused_text:
            raise ScinoephileError(
                "Unable to audit OCR fusion: fused subtitle "
                f"{index} does not match the automatic fusion result"
            )
        return _OcrFusionDecision(
            case_index=None,
            difficulty=0,
            note=_get_automatic_note(source_one_text, source_two_text),
            requires_llm=False,
            verified=True,
        )

    case_data = cases_by_key.get((source_one_text, source_two_text))
    if case_data is None:
        if not has_decision_log:
            return _OcrFusionDecision(
                case_index=None,
                difficulty=0,
                note="",
                requires_llm=True,
                verified=False,
            )
        raise ScinoephileError(
            f"Unable to audit OCR fusion: no logged test case matches subtitle {index}"
        )
    case_index, test_case = case_data
    answer = test_case.answer
    note = "(unanswered)"
    if answer is not None:
        note = answer.note
        if answer.output != fused_text:
            raise ScinoephileError(
                "Unable to audit OCR fusion: fused subtitle "
                f"{index} does not match test case {case_index} output"
            )
    return _OcrFusionDecision(
        case_index=case_index,
        difficulty=test_case.difficulty,
        note=note,
        requires_llm=True,
        verified=test_case.verified,
    )


def _validate_alignment(reference: Series, candidate: Series, label: str):
    """Validate exact one-to-one timing alignment against a reference series.

    Arguments:
        reference: reference subtitle series
        candidate: candidate subtitle series
        label: candidate label used in errors
    Raises:
        ScinoephileError: if the candidate is not exactly one-to-one aligned
    """
    if not are_series_one_to_one(reference, candidate):
        raise ScinoephileError(
            f"{label} subtitle series must be one-to-one timing-aligned with source one"
        )
