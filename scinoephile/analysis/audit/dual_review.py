#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit parallel dual-script subtitle review workflows."""

from __future__ import annotations

from collections.abc import Sequence

from scinoephile.core.llms import TestCase
from scinoephile.core.subtitles import Series

from .review import audit_review
from .review_filters import ReviewAuditFilterGroup
from .review_inputs import ReviewAuditComparison, ReviewAuditPair

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
    filters: ReviewAuditFilterGroup = ReviewAuditFilterGroup(),
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
        filters: row, character, and range filters
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
        filters=filters,
    )
