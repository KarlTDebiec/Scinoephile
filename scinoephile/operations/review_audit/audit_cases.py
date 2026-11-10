#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Build and load audit test cases and copy their findings onto subtitle rows."""

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
    "apply_audit_findings_to_rows",
    "build_audit_query",
    "build_audit_test_case",
    "load_audit_test_cases",
    "merge_audit_findings",
]


def apply_audit_findings_to_rows(
    block: list[AuditRow], case: ReviewAuditTestCase | None
) -> list[AuditRow]:
    """Copy matching audit findings onto the rows for one subtitle block.

    The language, subtitle numbers, original text, proofread text, and
    proofreading notes must match across the whole block. For any row without
    a matching finding, mark it unaudited and clear its audit note and verification.

    Arguments:
        block: all rows in the subtitle block, in source order
        case: audit test case, or None to clear the findings for the whole block
    Returns:
        copies of the subtitle rows with updated audit fields
    """
    findings: dict[int, ReviewAuditFinding] = {}
    verified = False
    if case is not None and case.answer is not None:
        if case.query.key == build_audit_query(block).key:
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


def build_audit_query(block: list[AuditRow] | tuple[AuditRow, ...]) -> ReviewAuditQuery:
    """Build the input for auditing one subtitle block.

    The same input is used to check whether saved findings still apply.

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


def build_audit_test_case(block: list[AuditRow]) -> ReviewAuditTestCase:
    """Build a test case from a subtitle block and its current audit findings.

    The test case has a draft answer when only some rows have findings.
    A block without findings has no answer.

    Arguments:
        block: all rows in the subtitle block, in source order
    Returns:
        test case containing the audit query, any findings, and verification
    """
    findings = [
        {"index": row.index, "status": row.finding.value, "note": row.notes.strip()}
        for row in block
        if row.finding != AuditStatus.unaudited
    ]
    data = {
        "query": build_audit_query(block).model_dump(),
        "verified": all(row.verified for row in block),
    }
    if findings:
        data["answer"] = {"findings": findings}
        data["draft"] = len(findings) < len(block)
    case_cls = ReviewAuditManager.get_test_case_cls(ReviewAuditPromptEng)
    return case_cls.model_validate(data)


def load_audit_test_cases(
    json_path: Path,
) -> tuple[dict[int, ReviewAuditTestCase], Language | None]:
    """Read audit test cases and their subtitle language from JSON.

    Arguments:
        json_path: path to the audit JSON file
    Returns:
        test cases keyed by the first subtitle number in each block, and their
        language. A missing file or an empty JSON array gives an empty dictionary
        and None
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


def merge_audit_findings(
    block: tuple[AuditRow, ...],
    case: ReviewAuditTestCase,
    previous: ReviewAuditTestCase | None,
    *,
    rerun: bool,
) -> tuple[list[AuditRow], ReviewAuditTestCase]:
    """Combine new audit findings with any findings already saved for the block.

    When resuming, keep findings from a matching manual draft and fill in the
    missing ones. Carry over verification and few-shot status when the audit
    input and answer match a previously verified case.

    Arguments:
        block: all rows in the subtitle block, in source order
        case: new test case with a complete answer for the block
        previous: previously saved test case for the block, if any
        rerun: whether to replace manual draft findings with the new findings
    Returns:
        updated subtitle rows and the test case to save
    """
    if previous is not None and previous.query.key != case.query.key:
        previous = None
    updated = apply_audit_findings_to_rows(list(block), case)
    if not rerun and previous is not None and previous.draft:
        updated = [
            before if before.finding != AuditStatus.unaudited else after
            for before, after in zip(block, updated, strict=True)
        ]
        case = build_audit_test_case(updated)
    elif previous is not None and previous.verified and previous.answer == case.answer:
        case = case.model_copy(update={"verified": True, "few_shot": previous.few_shot})
        updated = [replace(row, verified=True) for row in updated]
    return updated, case
