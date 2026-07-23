#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle review auditing."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.audit.review import (
    DualReviewAuditFilter,
    ReviewAuditFilter,
    ReviewAuditPair,
    audit_review,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.review import ReviewTestCase


def test_audit_review_filters_unverified_cases():
    """Test regular review audits select subtitles in unverified logged cases."""
    original = _get_series(("First", "Second", "Third"))
    reviewed = _get_series(("First revised", "Second", "Third"))
    unverified_case = ReviewTestCase.model_validate(
        {
            "query": {"subtitles": [{"index": 1, "text": "First"}]},
            "answer": {
                "revisions": [{"index": 1, "text": "First revised", "note": "Revised."}]
            },
        }
    )
    verified_case = ReviewTestCase.model_validate(
        {
            "query": {"subtitles": [{"index": 1, "text": "Second"}]},
            "answer": {"revisions": []},
            "verified": True,
        }
    )

    report = audit_review(
        reviews=(
            ReviewAuditPair(
                label="Test",
                original=original,
                reviewed=reviewed,
                review_cases=(unverified_case, verified_case),
            ),
        ),
        row_filter=ReviewAuditFilter.unverified,
    )

    assert "- row filter: unverified" in report
    assert "- table rows: 1" in report
    assert "| 1 | First<br>First revised | Test review: Revised. |  |" in report
    assert "| 2 |" not in report
    assert "| 3 |" not in report

    all_report = audit_review(
        reviews=(
            ReviewAuditPair(
                label="Test",
                original=original,
                reviewed=reviewed,
                review_cases=(unverified_case, verified_case),
            ),
        ),
        row_filter=ReviewAuditFilter.all,
    )
    assert "| 1 | First<br>First revised | Test review: Revised. |  |" in all_report
    assert "| 2 | Second |  | ✓ |" in all_report
    assert "| 3 | Third |  | — |" in all_report


def test_audit_review_ignores_retained_historical_cases():
    """Test source revisions do not make retained review history fatal."""
    original = _get_series(("Current input",))
    reviewed = _get_series(("Current output",))
    historical_case = ReviewTestCase.model_validate(
        {
            "query": {"subtitles": [{"index": 1, "text": "Historical input"}]},
            "answer": {
                "revisions": [
                    {
                        "index": 1,
                        "text": "Historical output",
                        "note": "Historical note.",
                    }
                ]
            },
        }
    )
    current_case = ReviewTestCase.model_validate(
        {
            "query": {"subtitles": [{"index": 1, "text": "Current input"}]},
            "answer": {
                "revisions": [
                    {"index": 1, "text": "Current output", "note": "Current note."}
                ]
            },
            "verified": True,
        }
    )

    report = audit_review(
        reviews=(
            ReviewAuditPair(
                label="Test",
                original=original,
                reviewed=reviewed,
                review_cases=(historical_case, current_case),
            ),
        ),
        row_filter=ReviewAuditFilter.all,
    )

    assert "Historical note." not in report
    assert "Test review: Current note." in report
    assert (
        "| 1 | Current input<br>Current output | Test review: Current note. | ✓ |"
        in report
    )


def test_audit_review_selects_blocks():
    """Test review audits select one workflow block at a time."""
    original = Series(
        events=[
            Subtitle(start=0, end=500, text="First"),
            Subtitle(start=1_000, end=1_500, text="Second"),
            Subtitle(start=5_000, end=5_500, text="Third"),
        ]
    )
    reviewed = Series(
        events=[
            Subtitle(start=0, end=500, text="First"),
            Subtitle(start=1_000, end=1_500, text="Second"),
            Subtitle(start=5_000, end=5_500, text="Third revised"),
        ]
    )
    reviews = (
        ReviewAuditPair(
            label="Test",
            original=original,
            reviewed=reviewed,
        ),
    )

    report = audit_review(
        reviews=reviews,
        row_filter=ReviewAuditFilter.all,
        first_block=2,
        last_block=2,
    )

    assert "- block range: 2 through 2" in report
    assert "| 1 |" not in report
    assert "| 2 |" not in report
    assert "| 3 | Third<br>Third revised |" in report

    with raises(ScinoephileError, match="mutually exclusive"):
        audit_review(
            reviews=reviews,
            first_index=1,
            first_block=2,
        )

    with raises(ScinoephileError, match="requires at least one comparison"):
        audit_review(
            reviews=reviews,
            row_filter=DualReviewAuditFilter.discrepancies,
        )


def test_audit_review_uses_latest_duplicate_case():
    """Test the latest duplicate review case controls notes and verification."""
    original = _get_series(("Input",))
    reviewed = _get_series(("Output",))
    historical_case = ReviewTestCase.model_validate(
        {
            "query": {"subtitles": [{"index": 1, "text": "Input"}]},
            "answer": {
                "revisions": [
                    {"index": 1, "text": "Output", "note": "Historical note."}
                ]
            },
        }
    )
    current_case = ReviewTestCase.model_validate(
        {
            "query": historical_case.query.model_dump(),
            "answer": {
                "revisions": [{"index": 1, "text": "Output", "note": "Current note."}]
            },
            "verified": True,
        }
    )
    reviews = (
        ReviewAuditPair(
            label="Test",
            original=original,
            reviewed=reviewed,
            review_cases=(historical_case, current_case),
        ),
    )

    report = audit_review(reviews=reviews, row_filter=ReviewAuditFilter.all)
    unverified_report = audit_review(
        reviews=reviews,
        row_filter=ReviewAuditFilter.unverified,
    )

    assert "Historical note." not in report
    assert "Test review: Current note." in report
    assert "| 1 | Input<br>Output | Test review: Current note. | ✓ |" in report
    assert "- table rows: 0" in unverified_report


def _get_series(texts: tuple[str, ...]) -> Series:
    """Get a subtitle series fixture.

    Arguments:
        texts: subtitle texts
    Returns:
        subtitle series
    """
    return Series(events=[Subtitle(text=text) for text in texts])
