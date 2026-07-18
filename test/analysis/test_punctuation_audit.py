#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for transcription punctuation audit reports."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.punctuation_audit import (
    PunctuationAuditFilter,
    audit_punctuation,
)
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.punctuation import (
    PunctuationAnswer,
    PunctuationQuery,
    PunctuationTestCase,
)


def test_audit_punctuation_formats_changed_and_unchanged_rows():
    """Test changed and unchanged answers are rendered consistently."""
    reference = _get_series("參|考一", "參考二")
    target = _get_series("甲，乙丙", "丁")
    test_cases = (
        PunctuationTestCase(
            query=PunctuationQuery(
                guide="參|考一",
                subtitles=["甲", "乙丙"],
            ),
            answer=PunctuationAnswer(output="甲，乙丙"),
            verified=True,
        ),
        PunctuationTestCase(
            query=PunctuationQuery(guide="參考二", subtitles=["丁"]),
            answer=PunctuationAnswer(output="丁"),
        ),
    )

    report = audit_punctuation(reference, target, test_cases)

    assert "- logged cases: 2" in report
    assert "- punctuation changes: 1" in report
    assert "- unchanged answers: 1" in report
    assert "- unanswered cases: 0" in report
    assert "| Index | Reference | Input | Output | Notes | Verified |" in report
    assert "| 1 | 參\\|考一 | 甲<br>乙丙 | 甲，乙丙 |  | ✓ |" in report
    assert "| 2 | 參考二 | 丁 |  |  |  |" in report


def test_audit_punctuation_formats_unanswered_case():
    """Test an unanswered logged case is identified without inventing output."""
    test_case = PunctuationTestCase(
        query=PunctuationQuery(guide="參考", subtitles=["原文"])
    )

    report = audit_punctuation(
        _get_series("參考"),
        _get_series("原文"),
        (test_case,),
    )

    assert "- unanswered cases: 1" in report
    assert "| 1 | 參考 | 原文 | (unanswered) |  |  |" in report


def test_audit_punctuation_filters_rows_and_subtitle_range():
    """Test row status and inclusive subtitle-range filters."""
    reference = _get_series("參考一", "參考二", "參考三")
    target = _get_series("甲，乙", "丙", "丁")
    test_cases = (
        PunctuationTestCase(
            query=PunctuationQuery(guide="參考一", subtitles=["甲", "乙"]),
            answer=PunctuationAnswer(output="甲，乙"),
        ),
        PunctuationTestCase(
            query=PunctuationQuery(guide="參考二", subtitles=["丙"]),
            answer=PunctuationAnswer(output="丙"),
        ),
    )

    changed_report = audit_punctuation(
        reference,
        target,
        test_cases,
        row_filter=PunctuationAuditFilter.changes,
    )
    ranged_report = audit_punctuation(
        reference,
        target,
        test_cases,
        first_index=2,
        last_index=3,
    )

    assert "- logged cases: 2" in changed_report
    assert "- row filter: changes" in changed_report
    assert "- table rows: 1" in changed_report
    assert "| 1 |" in changed_report
    assert "| 2 |" not in changed_report
    assert "- logged cases: 1" in ranged_report
    assert "- subtitle range: 1-indexed numbers 2 through 3" in ranged_report
    assert "- table rows: 1" in ranged_report
    assert "| 1 |" not in ranged_report
    assert "| 2 |" in ranged_report


def test_audit_punctuation_resolves_repeated_reference_from_target():
    """Test target characters disambiguate repeated reference text."""
    reference = _get_series("重複", "其他", "重複")
    target = _get_series("甲", "中", "乙！")
    test_case = PunctuationTestCase(
        query=PunctuationQuery(guide="重複", subtitles=["乙"]),
        answer=PunctuationAnswer(output="乙！"),
    )

    report = audit_punctuation(reference, target, (test_case,))

    assert "| 3 | 重複 | 乙 | 乙！ |" in report


def test_audit_punctuation_resolves_repeated_reference_from_longest_target():
    """Test the longest contained target text resolves a repeated reference."""
    reference = _get_series("開始", "開始")
    target = _get_series("開始啊", "開始")
    test_case = PunctuationTestCase(
        query=PunctuationQuery(guide="開始", subtitles=["啊", "開始啊"]),
        answer=PunctuationAnswer(output="啊，開始啊。"),
    )

    report = audit_punctuation(reference, target, (test_case,))

    assert "| 1 | 開始 | 啊<br>開始啊 | 啊，開始啊。 |" in report


def test_audit_punctuation_resolves_repeated_reference_from_context():
    """Test neighboring cases disambiguate repeated reference text."""
    reference = _get_series("之前", "重複", "之後", "重複")
    target = _get_series("前", "同", "後", "同")
    test_cases = (
        PunctuationTestCase(
            query=PunctuationQuery(guide="之前", subtitles=["前"]),
            answer=PunctuationAnswer(output="前"),
        ),
        PunctuationTestCase(
            query=PunctuationQuery(guide="重複", subtitles=["同"]),
            answer=PunctuationAnswer(output="同"),
        ),
        PunctuationTestCase(
            query=PunctuationQuery(guide="之後", subtitles=["後"]),
            answer=PunctuationAnswer(output="後"),
        ),
    )

    report = audit_punctuation(reference, target, test_cases)

    assert "| 2 | 重複 | 同 |" in report
    assert "| 4 | 重複 | 同 |" not in report


def test_audit_punctuation_resolves_repeated_reference_before_range_filtering():
    """Test a range cannot force a repeated case onto the wrong subtitle."""
    reference = _get_series("前一", "重複", "中間", "之前", "重複", "之後")
    target = _get_series("甲", "同", "乙", "前", "同", "後")
    test_cases = (
        PunctuationTestCase(
            query=PunctuationQuery(guide="之前", subtitles=["前"]),
            answer=PunctuationAnswer(output="前"),
        ),
        PunctuationTestCase(
            query=PunctuationQuery(guide="重複", subtitles=["同"]),
            answer=PunctuationAnswer(output="同"),
        ),
        PunctuationTestCase(
            query=PunctuationQuery(guide="之後", subtitles=["後"]),
            answer=PunctuationAnswer(output="後"),
        ),
    )

    report = audit_punctuation(
        reference,
        target,
        test_cases,
        first_index=1,
        last_index=2,
    )

    assert "- logged cases: 0" in report
    assert "- table rows: 0" in report
    assert "| 2 | 重複 | 同 |" not in report


def test_audit_punctuation_ignores_ambiguity_outside_range():
    """Test repeated references wholly outside the range need not be resolved."""
    reference = _get_series("範圍內", "重複", "重複")
    target = _get_series("乙", "甲", "甲")
    test_case = PunctuationTestCase(
        query=PunctuationQuery(guide="重複", subtitles=["甲"]),
        answer=PunctuationAnswer(output="甲"),
    )

    report = audit_punctuation(
        reference,
        target,
        (test_case,),
        first_index=1,
        last_index=1,
    )

    assert "- logged cases: 0" in report
    assert "- table rows: 0" in report


def test_audit_punctuation_rejects_unmatched_reference():
    """Test a logged reference absent from the series cannot be indexed."""
    test_case = PunctuationTestCase(
        query=PunctuationQuery(guide="不同", subtitles=["甲"])
    )

    with raises(ScinoephileError, match="test case 1 reference subtitle was not found"):
        audit_punctuation(
            _get_series("參考"),
            _get_series("甲"),
            (test_case,),
        )


def test_audit_punctuation_ignores_superseded_reference_revision():
    """Test a retained case using corrected reference text is ignored."""
    reference = _get_series("更正參考")
    target = _get_series("甲，乙")
    historical_case = PunctuationTestCase(
        query=PunctuationQuery(guide="舊參考", subtitles=["甲", "乙"]),
        answer=PunctuationAnswer(output="甲，乙"),
    )
    current_case = PunctuationTestCase(
        query=PunctuationQuery(guide="更正參考", subtitles=["甲", "乙"]),
        answer=PunctuationAnswer(output="甲，乙"),
    )
    test_cases = (historical_case, current_case)

    report = audit_punctuation(reference, target, test_cases)
    excluded_report = audit_punctuation(
        reference,
        target,
        test_cases,
        first_index=2,
        last_index=2,
    )

    assert "- logged cases: 1" in report
    assert "舊參考" not in report
    assert "| 1 | 更正參考 | 甲<br>乙 | 甲，乙 |" in report
    assert "- logged cases: 0" in excluded_report


def test_audit_punctuation_rejects_ambiguous_reference():
    """Test repeated references without distinguishing context are rejected."""
    test_case = PunctuationTestCase(
        query=PunctuationQuery(guide="重複", subtitles=["甲"]),
        answer=PunctuationAnswer(output="甲"),
    )

    with raises(
        ScinoephileError,
        match="test case 1 is ambiguous.*1, 3",
    ):
        audit_punctuation(
            _get_series("重複", "其他", "重複"),
            _get_series("甲", "中", "甲"),
            (test_case,),
        )


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
