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
            verified=True,
        ),
    )

    changed_report = audit_delineation(
        reference,
        test_cases,
        row_filter=DelineationAuditFilter.changes,
    )
    unverified_report = audit_delineation(
        reference,
        test_cases,
        row_filter=DelineationAuditFilter.unverified,
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
    assert "- reference subtitle range: 1 through 2" in ranged_report
    assert "- table rows: 1" in ranged_report
    assert "| 1<br>2 |" in ranged_report
    assert "| 2<br>3 |" not in ranged_report
    assert "- row filter: unverified" in unverified_report
    assert "- table rows: 1" in unverified_report
    assert "| 1<br>2 |" in unverified_report
    assert "| 2<br>3 |" not in unverified_report


def test_audit_delineation_filters_reference_blocks():
    """Test block bounds select only boundaries within matching guide blocks."""
    reference = Series(
        events=[
            Subtitle(start=0, end=1000, text="一"),
            Subtitle(start=1000, end=2000, text="二"),
            Subtitle(start=6000, end=7000, text="三"),
            Subtitle(start=7000, end=8000, text="四"),
        ]
    )
    test_cases = (
        DelineationTestCase(
            query=DelineationQuery(
                reference_one="一",
                reference_two="二",
                target_one="甲",
            ),
            answer=DelineationAnswer(),
        ),
        DelineationTestCase(
            query=DelineationQuery(
                reference_one="三",
                reference_two="四",
                target_one="乙",
            ),
            answer=DelineationAnswer(),
        ),
    )

    report = audit_delineation(
        reference,
        test_cases,
        first_block=2,
        last_block=2,
    )

    assert "- block range: 2 through 2" in report
    assert "| 1<br>2 |" not in report
    assert "| 3<br>4 |" in report


def test_audit_delineation_rejects_invalid_range():
    """Test direct callers receive a domain error for an invalid range."""
    with raises(ScinoephileError, match="First index must be at least 1"):
        audit_delineation(_get_series("參考一", "參考二"), (), first_index=0)
    with raises(ScinoephileError, match="First block must be at least 1"):
        audit_delineation(_get_series("參考一", "參考二"), (), first_block=0)


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


def test_audit_delineation_ignores_superseded_reference_revision():
    """Test retained cases using corrected reference text are ignored."""
    reference = _get_series("參考一", "更正參考二", "參考三")
    historical_case = DelineationTestCase(
        query=DelineationQuery(
            reference_one="參考一",
            reference_two="舊參考二",
            target_one="舊甲",
            target_two="舊乙",
        ),
        answer=DelineationAnswer(),
    )
    later_historical_case = DelineationTestCase(
        query=DelineationQuery(
            reference_one="參考一",
            reference_two="舊參考二",
            target_one="甲",
            target_two="乙",
        ),
        answer=DelineationAnswer(),
    )
    current_case = DelineationTestCase(
        query=DelineationQuery(
            reference_one="參考一",
            reference_two="更正參考二",
            target_one="甲",
            target_two="乙",
        ),
        answer=DelineationAnswer(),
    )
    test_cases = (historical_case, later_historical_case, current_case)

    report = audit_delineation(reference, test_cases)
    excluded_report = audit_delineation(
        reference,
        test_cases,
        first_index=3,
        last_index=3,
    )

    assert "- logged cases: 1" in report
    assert "舊參考二" not in report
    assert "| 1<br>2 | 參考一<br>更正參考二 | 甲<br>乙 |" in report
    assert "- logged cases: 0" in excluded_report


def test_audit_delineation_resolves_repeated_reference_pair_from_context():
    """Test neighboring cases resolve a repeated reference pair."""
    reference = _get_series("之前", "重複一", "重複二", "之後", "重複一", "重複二")
    test_cases = (
        DelineationTestCase(
            query=DelineationQuery(
                reference_one="之前",
                reference_two="重複一",
                target_one="甲",
                target_two="乙",
            ),
            answer=DelineationAnswer(),
        ),
        DelineationTestCase(
            query=DelineationQuery(
                reference_one="重複一",
                reference_two="重複二",
                target_one="乙",
                target_two="丙",
            ),
            answer=DelineationAnswer(),
        ),
        DelineationTestCase(
            query=DelineationQuery(
                reference_one="重複二",
                reference_two="之後",
                target_one="丙",
                target_two="丁",
            ),
            answer=DelineationAnswer(),
        ),
    )

    report = audit_delineation(reference, test_cases)

    assert "| 2<br>3 | 重複一<br>重複二 | 乙<br>丙 |" in report
    assert "| 5<br>6 | 重複一<br>重複二 | 乙<br>丙 |" not in report


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
