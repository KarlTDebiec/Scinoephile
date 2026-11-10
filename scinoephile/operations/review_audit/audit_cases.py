#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Map audit test cases to the subtitle blocks they describe."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from scinoephile.core import Language
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.lang.eng.review_audit import ReviewAuditPromptEng
from scinoephile.llms.review_audit import (
    ReviewAuditFinding,
    ReviewAuditManager,
    ReviewAuditQuery,
    ReviewAuditSubtitle,
    ReviewAuditTestCase,
)

from .rows import AuditRow, AuditStatus

__all__ = [
    "apply_audit_case",
    "build_audit_case",
    "get_audit_query",
    "load_audit_cases",
    "merge_audit_case",
]


def apply_audit_case(
    block: list[AuditRow], case: ReviewAuditTestCase | None
) -> list[AuditRow]:
    """Copy audit findings onto the subtitle rows they were based on.

    The language, subtitle numbers, original text, proofread text, and
    proofreading notes must match across the entire block. Rows without a
    matching finding are marked unaudited.

    Arguments:
        block: current subtitle rows, in source order
        case: audit results and the subtitles they describe, if available
    Returns:
        copies of the rows with audit findings, notes, and verification updated
    """
    findings: dict[int, ReviewAuditFinding] = {}
    verified = False
    if case is not None and case.answer is not None:
        if case.query.key == get_audit_query(block).key:
            findings = {finding.index: finding for finding in case.answer.findings}
            verified = case.verified
    updated = []
    for row in block:
        finding = findings.get(row.index)
        if finding is None:
            updated.append(
                replace(row, finding=AuditStatus.unaudited, notes="", verified=False)
            )
        else:
            updated.append(
                replace(
                    row,
                    finding=AuditStatus(finding.status),
                    notes=finding.note,
                    verified=verified,
                )
            )
    return updated


def build_audit_case(block: list[AuditRow]) -> ReviewAuditTestCase:
    """Turn the findings entered for a subtitle block into an audit test case.

    Arguments:
        block: current subtitle rows and their findings in source order
    Returns:
        audit case, with a draft answer if findings are incomplete
    """
    findings = [
        {"index": row.index, "status": row.finding.value, "note": row.notes.strip()}
        for row in block
        if row.finding != AuditStatus.unaudited
    ]
    data = {
        "query": get_audit_query(block).model_dump(),
        "verified": all(row.verified for row in block),
    }
    if findings:
        data["answer"] = {"findings": findings}
        data["draft"] = len(findings) < len(block)
    case_cls = ReviewAuditManager.get_test_case_cls(ReviewAuditPromptEng)
    return case_cls.model_validate(data)


def get_audit_query(block: list[AuditRow] | tuple[AuditRow, ...]) -> ReviewAuditQuery:
    """Collect the subtitle text and proofreading notes for an audit.

    The same fields identify saved findings for the block.

    Arguments:
        block: all subtitle rows in the block, in source order
    Returns:
        query with the language, subtitle numbers, original and proofread text,
        and proofreading notes
    """
    return ReviewAuditQuery(
        language=block[0].language,
        subtitles=[
            ReviewAuditSubtitle(
                index=row.index,
                original=row.original,
                proofread=row.reviewed,
                note=row.review_note,
            )
            for row in block
        ],
    )


def load_audit_cases(
    json_path: Path,
) -> tuple[dict[int, ReviewAuditTestCase], Language | None]:
    """Read saved audit results and their subtitle language from JSON.

    Arguments:
        json_path: project audit test-case file
    Returns:
        cases keyed by first subtitle index and the language, if known
    Raises:
        ValueError: if the cases use different or unsupported languages
    """
    if not json_path.exists():
        return {}, None
    cases = load_test_cases_from_json(
        json_path, ReviewAuditManager, ReviewAuditPromptEng
    )
    languages = {case.query.language for case in cases}
    if len(languages) > 1:
        raise ValueError("Audit cases must use one subtitle language")
    language = None
    if languages:
        language = Language(languages.pop())
    return {case.query.subtitles[0].index: case for case in cases}, language


def merge_audit_case(
    block: tuple[AuditRow, ...],
    case: ReviewAuditTestCase,
    previous: ReviewAuditTestCase | None,
    *,
    rerun: bool,
) -> tuple[list[AuditRow], ReviewAuditTestCase]:
    """Apply a new audit answer to a subtitle block.

    When resuming an audit, keep manual findings from a matching draft.
    If the new answer matches a previously verified answer, keep its verification.

    Arguments:
        block: reserved subtitle rows in source order
        case: completed audit case matching the block
        previous: saved audit case for the block, if any
        rerun: whether to replace manual draft findings
    Returns:
        updated rows and the audit case to save
    """
    if previous is not None and previous.query.key != case.query.key:
        previous = None
    updated = apply_audit_case(list(block), case)
    if not rerun and previous is not None and previous.draft:
        updated = [
            before if before.finding != AuditStatus.unaudited else after
            for before, after in zip(block, updated, strict=True)
        ]
        case = build_audit_case(updated)
    elif previous is not None and previous.verified and previous.answer == case.answer:
        case = case.model_copy(update={"verified": True, "few_shot": previous.few_shot})
        updated = [replace(row, verified=True) for row in updated]
    return updated, case
