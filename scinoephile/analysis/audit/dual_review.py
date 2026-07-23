#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit parallel dual-script subtitle review workflows."""

from __future__ import annotations

from collections.abc import Sequence

from scinoephile.core.llms import TestCase
from scinoephile.core.subtitles import Series

from .review import (
    DualReviewAuditFilter,
    ReviewAuditComparison,
    ReviewAuditPair,
    audit_review,
)

__all__ = ["audit_dual_review"]


def audit_dual_review(
    *,
    traditional: Series,
    traditional_reviewed: Series,
    traditional_simplified: Series,
    traditional_simplified_reviewed: Series,
    simplified: Series,
    simplified_reviewed: Series,
    traditional_review_cases: Sequence[TestCase] = (),
    traditional_simplified_review_cases: Sequence[TestCase] = (),
    simplified_review_cases: Sequence[TestCase] = (),
    row_filter: DualReviewAuditFilter = DualReviewAuditFilter.changes,
    characters: Sequence[str] = (),
    first_index: int | None = None,
    last_index: int | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
) -> str:
    """Audit parallel simplified and traditional-to-simplified review paths.

    Arguments:
        traditional: traditional-script review input
        traditional_reviewed: traditional-script reviewed subtitles
        traditional_simplified: simplified traditional-script subtitles
        traditional_simplified_reviewed: reviewed simplified traditional-script
            subtitles
        simplified: simplified-script review input
        simplified_reviewed: simplified-script reviewed subtitles
        traditional_review_cases: traditional review test cases
        traditional_simplified_review_cases: traditional simplification review test
            cases
        simplified_review_cases: simplified review test cases
        row_filter: row status filter
        characters: individual characters whose occurrence limits included rows
        first_index: first 1-indexed subtitle number to include, inclusive
        last_index: last 1-indexed subtitle number to include, inclusive
        first_block: first 1-indexed workflow block number to include, inclusive
        last_block: last 1-indexed workflow block number to include, inclusive
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if review test cases do not match the subtitle series
    """
    return audit_review(
        reviews=(
            ReviewAuditPair(
                label="Simplified",
                original=simplified,
                reviewed=simplified_reviewed,
                review_cases=simplified_review_cases,
            ),
            ReviewAuditPair(
                label="Traditional",
                original=traditional,
                reviewed=traditional_reviewed,
                review_cases=traditional_review_cases,
            ),
            ReviewAuditPair(
                label="Traditional simplification",
                original=traditional_simplified,
                reviewed=traditional_simplified_reviewed,
                review_cases=traditional_simplified_review_cases,
            ),
        ),
        comparisons=(
            ReviewAuditComparison(
                column_label="Simplified vs Traditional->Simplified",
                summary_label="Final text",
                left=simplified_reviewed,
                right=traditional_simplified_reviewed,
            ),
        ),
        row_filter=row_filter,
        characters=characters,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )
