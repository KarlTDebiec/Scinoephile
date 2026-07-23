#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit OCR-fusion decisions and format the results as Markdown."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import are_series_one_to_one
from scinoephile.llms.ocr_fusion import OcrFusionTestCase

from .utils import (
    AuditColumn,
    format_audit_report,
    format_verification_marker,
    get_selected_event_indexes,
)

__all__ = [
    "OcrFusionAuditFilter",
    "audit_ocr_fusion",
]


class OcrFusionAuditFilter(StrEnum):
    """Row filters supported by an OCR-fusion audit."""

    all = "all"
    """Include every eligible row."""

    changes = "changes"
    """Include rows whose OCR sources differ."""

    discrepancies = "discrepancies"
    """Include rows whose fused and validated text differ."""

    unverified = "unverified"
    """Include unverified rows that required an LLM decision."""


@dataclass(frozen=True, kw_only=True)
class _OcrFusionRow:
    """One OCR-fusion subtitle displayed in the audit report."""

    changed: bool
    """Whether the two OCR sources differ."""
    discrepancy: bool
    """Whether fused and validated text differ."""
    cells: tuple[str, ...]
    """Semantic audit table cell values."""
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


def audit_ocr_fusion(
    source_one: Series,
    source_two: Series,
    fused: Series,
    test_cases: Sequence[OcrFusionTestCase] | None = None,
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
    cases_by_key: dict[tuple[str, str], tuple[int, OcrFusionTestCase]] = {}
    for case_index, test_case in enumerate(test_cases or (), 1):
        key = (test_case.query.source_one, test_case.query.source_two)
        cases_by_key[key] = (case_index, test_case)

    # Resolve the semantic data for every selected subtitle row
    all_rows = [
        _get_row(
            position,
            source_one,
            source_two,
            fused,
            cases_by_key,
            has_decision_log=has_decision_log,
            validated=validated,
        )
        for position in sorted(selected_positions)
    ]

    # Filter rows and summarize the complete selected data
    rows = _filter_rows(all_rows, row_filter)
    llm_rows = [row for row in all_rows if row.requires_llm]
    validated_track = "omitted"
    if validated is not None:
        validated_track = "included"
    summary_items = [
        f"subtitles: {len(all_rows)}",
        f"source disagreements: {sum(row.changed for row in all_rows)}",
        f"validated track: {validated_track}",
        f"validated discrepancies: {sum(row.discrepancy for row in all_rows)}",
        f"row filter: {row_filter.value}",
    ]
    if has_decision_log:
        verified_llm_rows = sum(row.verified for row in llm_rows)
        unverified_llm_rows = sum(not row.verified for row in llm_rows)
        summary_items.extend(
            (
                f"LLM decisions: {len(llm_rows)}",
                f"verified LLM decisions: {verified_llm_rows}",
                f"unverified LLM decisions: {unverified_llm_rows}",
            )
        )
    else:
        summary_items.extend(
            (
                f"LLM-required rows: {len(llm_rows)}",
                "decision log: omitted",
            )
        )
    columns: list[AuditColumn] = [
        ("Subtitle", "right"),
        ("Case", "right"),
        ("Difficulty", "right"),
        ("Source one", "left"),
        ("Source two", "left"),
        ("Fused", "left"),
        ("Validated", "left"),
        ("Notes", "left"),
    ]
    if has_decision_log:
        columns.append(("Verified", "center"))
    return format_audit_report(
        title="OCR Fusion Audit",
        summary_items=summary_items,
        columns=columns,
        rows=[row.cells for row in rows],
        first_index=first_index,
        last_index=last_index,
        index_track_name="fused",
        first_block=first_block,
        last_block=last_block,
    )


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


def _get_decision(
    index: int,
    source_one_text: str,
    source_two_text: str,
    fused_text: str,
    cases_by_key: dict[tuple[str, str], tuple[int, OcrFusionTestCase]],
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


def _get_row(
    position: int,
    source_one: Series,
    source_two: Series,
    fused: Series,
    cases_by_key: dict[tuple[str, str], tuple[int, OcrFusionTestCase]],
    *,
    has_decision_log: bool,
    validated: Series | None,
) -> _OcrFusionRow:
    """Resolve one OCR-fusion subtitle into semantic report data.

    Arguments:
        position: zero-based fused subtitle position
        source_one: first OCR subtitle series
        source_two: second OCR subtitle series
        fused: OCR-fusion output subtitle series
        cases_by_key: latest logged case keyed by source text pair
        has_decision_log: whether a decision log was supplied
        validated: optional validated subtitle series
    Returns:
        semantic audit row
    """
    index = position + 1
    source_one_text = source_one.events[position].text_with_newline
    source_two_text = source_two.events[position].text_with_newline
    fused_text = fused.events[position].text_with_newline
    validated_text = None
    if validated is not None:
        validated_text = validated.events[position].text_with_newline

    # Resolve the automatic or logged decision and its display metadata
    decision = _get_decision(
        index,
        source_one_text,
        source_two_text,
        fused_text,
        cases_by_key,
        has_decision_log=has_decision_log,
    )
    case_index = "—"
    difficulty = "—"
    if decision.case_index is not None:
        case_index = str(decision.case_index)
        difficulty = str(decision.difficulty)
    validated_display = "—"
    if validated_text:
        validated_display = validated_text

    # Keep the Notes column available even when no decision log was supplied
    cells = (
        str(index),
        case_index,
        difficulty,
        source_one_text or "—",
        source_two_text or "—",
        fused_text or "—",
        validated_display,
        decision.note,
    )
    if has_decision_log:
        verified: bool | None = None
        if decision.requires_llm:
            verified = decision.verified
        verified_marker = format_verification_marker(verified)
        cells += (verified_marker,)

    return _OcrFusionRow(
        changed=source_one_text != source_two_text,
        cells=cells,
        discrepancy=validated_text is not None and fused_text != validated_text,
        requires_llm=decision.requires_llm,
        verified=decision.verified,
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
