#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for transcription delineation audit reports."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.delineation_audit import (
    DelineationAuditFilter,
    audit_delineation,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.delineation import (
    DelineationAnswer,
    DelineationQuery,
    DelineationTestCase,
)


def test_audit_delineation_formats_shift_and_no_shift_rows():
    """Test shifted and unchanged boundaries are rendered as stacked pairs."""
    reference = _get_series("參|考一", "參考二", "參考三")
    test_cases = (
        DelineationTestCase(
            query=DelineationQuery(
                reference_one="參|考一",
                reference_two="參考二",
                target_one="甲乙",
                target_two="丙",
            ),
            answer=DelineationAnswer(output_one="甲", output_two="乙丙"),
            verified=True,
        ),
        DelineationTestCase(
            query=DelineationQuery(
                reference_one="參考二",
                reference_two="參考三",
                target_one="丁",
            ),
            answer=DelineationAnswer(),
        ),
    )

    report = audit_delineation(reference, test_cases)

    assert "- logged cases: 2" in report
    assert "- boundary shifts: 1" in report
    assert "- no-shift answers: 1" in report
    assert "- unanswered cases: 0" in report
    assert "| Indexes | Reference | Input | Output | Notes | Verified |" in report
    assert "| 1<br>2 | 參\\|考一<br>參考二 | 甲乙<br>丙 | 甲<br>乙丙 |  | ✓ |" in report
    assert "| 2<br>3 | 參考二<br>參考三 | 丁<br>— |  |  |  |" in report


def test_audit_delineation_sorts_rows_and_omits_unchanged_output():
    """Test rows are index-sorted and unchanged output is omitted."""
    reference = _get_series("參考一", "參考二", "參考三")
    test_cases = (
        DelineationTestCase(
            query=DelineationQuery(
                reference_one="參考二",
                reference_two="參考三",
                target_one="丙",
                target_two="丁",
            ),
            answer=DelineationAnswer(),
        ),
        DelineationTestCase(
            query=DelineationQuery(
                reference_one="參考一",
                reference_two="參考二",
                target_one="甲",
                target_two="乙",
            ),
            answer=DelineationAnswer(),
        ),
    )

    report = audit_delineation(reference, test_cases)

    first_row = "| 1<br>2 | 參考一<br>參考二 | 甲<br>乙 |  |  |  |"
    second_row = "| 2<br>3 | 參考二<br>參考三 | 丙<br>丁 |  |  |  |"
    assert report.index(first_row) < report.index(second_row)
    assert "- boundary shifts: 0" in report
    assert "- no-shift answers: 2" in report


def test_audit_delineation_formats_unanswered_case():
    """Test an unanswered logged case is identified without inventing output."""
    test_case = DelineationTestCase(
        query=DelineationQuery(
            reference_one="參考一",
            reference_two="參考二",
            target_one="甲",
        )
    )

    report = audit_delineation(_get_series("參考一", "參考二"), (test_case,))

    assert "- unanswered cases: 1" in report
    assert "| 1<br>2 | 參考一<br>參考二 | 甲<br>— | (unanswered) |  |  |" in report


def test_audit_delineation_filters_rows_and_subtitle_range():
    """Test row status and inclusive subtitle-range filters."""
    reference = _get_series("參考一", "參考二", "參考三")
    test_cases = (
        DelineationTestCase(
            query=DelineationQuery(
                reference_one="參考一",
                reference_two="參考二",
                target_one="甲乙",
                target_two="丙",
            ),
            answer=DelineationAnswer(output_one="甲", output_two="乙丙"),
        ),
        DelineationTestCase(
            query=DelineationQuery(
                reference_one="參考二",
                reference_two="參考三",
                target_one="丁",
            ),
            answer=DelineationAnswer(),
        ),
    )

    changed_report = audit_delineation(
        reference,
        test_cases,
        row_filter=DelineationAuditFilter.changes,
    )
    ranged_report = audit_delineation(
        reference,
        test_cases,
        first_index=1,
        last_index=2,
    )

    assert "- logged cases: 2" in changed_report
    assert "- row filter: changes" in changed_report
    assert "- table rows: 1" in changed_report
    assert "| 1<br>2 |" in changed_report
    assert "| 2<br>3 |" not in changed_report
    assert "- logged cases: 1" in ranged_report
    assert "- subtitle range: 1-indexed numbers 1 through 2" in ranged_report
    assert "- table rows: 1" in ranged_report
    assert "| 1<br>2 |" in ranged_report
    assert "| 2<br>3 |" not in ranged_report


def test_audit_delineation_rejects_unmatched_reference_pair():
    """Test a logged pair absent from the reference cannot be indexed."""
    test_case = DelineationTestCase(
        query=DelineationQuery(
            reference_one="不同一",
            reference_two="不同二",
            target_one="甲",
        )
    )

    with raises(ScinoephileError, match="test case 1 reference pair was not found"):
        audit_delineation(_get_series("參考一", "參考二"), (test_case,))


def test_audit_delineation_rejects_ambiguous_reference_pair():
    """Test a repeated reference pair cannot be assigned misleading indexes."""
    test_case = DelineationTestCase(
        query=DelineationQuery(
            reference_one="參考一",
            reference_two="參考二",
            target_one="甲",
        )
    )

    with raises(
        ScinoephileError,
        match="test case 1 reference pair is ambiguous.*1, 3",
    ):
        audit_delineation(
            _get_series("參考一", "參考二", "參考一", "參考二"),
            (test_case,),
        )


def test_audit_delineation_scopes_ambiguity_to_subtitle_range():
    """Test repeated pairs are resolved only within the requested range."""
    reference = _get_series("參考一", "參考二", "參考一", "參考二")
    test_case = DelineationTestCase(
        query=DelineationQuery(
            reference_one="參考一",
            reference_two="參考二",
            target_one="甲",
        ),
        answer=DelineationAnswer(),
    )

    first_report = audit_delineation(
        reference,
        (test_case,),
        first_index=1,
        last_index=2,
    )
    excluded_report = audit_delineation(
        reference,
        (test_case,),
        first_index=5,
        last_index=6,
    )

    assert "| 1<br>2 |" in first_report
    assert "- logged cases: 0" in excluded_report
    assert "- table rows: 0" in excluded_report


def _get_series(*texts: str) -> Series:
    """Construct a subtitle series with the provided text.

    Arguments:
        *texts: subtitle text by event
    Returns:
        constructed subtitle series
    """
    return Series(
        events=[
            Subtitle(start=index * 1000, end=(index + 1) * 1000, text=text)
            for index, text in enumerate(texts)
        ]
    )
