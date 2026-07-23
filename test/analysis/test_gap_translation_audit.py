#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for gap-translation audit reports."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.audit.gap_translation import audit_gap_translation
from scinoephile.analysis.audit.utils import VerificationAuditFilter
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.gap_translation import (
    GapTranslationAnswer,
    GapTranslationQuery,
    GapTranslationSubtitle,
    GapTranslationTestCase,
)


def test_audit_gap_translation_formats_answer_and_context():
    """Test one translated gap is rendered with global and local context."""
    target = _get_series(
        (0, 1000, "現有|一"),
        (2000, 3000, "現有三"),
    )
    guide = _get_series(
        (0, 1000, "參考一"),
        (1000, 2000, "參|考二"),
        (2000, 3000, "參考三"),
    )
    test_case = _get_test_case(
        targets=((1, "現有|一"), (3, "現有三")),
        guides=((1, "參考一"), (2, "參|考二"), (3, "參考三")),
        outputs=((2, "翻譯\n二"),),
        verified=True,
    )

    report = audit_gap_translation(target, guide, (test_case,))

    assert "- logged cases: 1" in report
    assert "- gaps: 1" in report
    assert "- translated gaps: 1" in report
    assert "- verified gaps: 1" in report
    assert (
        "| G 2<br>Q 2 | C 1<br>B 1 | 1 | 參\\|考二 | "
        "G 1: 現有\\|一<br>G 3: 現有三 | 翻譯<br>二 |  | ✓ |"
    ) in report


def test_audit_gap_translation_formats_empty_and_unanswered_gaps():
    """Test empty answers and missing answers remain distinguishable."""
    target = _get_series(
        (0, 1000, "現有一"),
        (6000, 7000, "現有三"),
    )
    guide = _get_series(
        (0, 1000, "參考一"),
        (1000, 2000, "參考二"),
        (6000, 7000, "參考三"),
        (7000, 8000, "參考四"),
    )
    test_cases = (
        _get_test_case(
            targets=((1, "現有一"),),
            guides=((1, "參考一"), (2, "參考二")),
            outputs=((2, ""),),
            verified=True,
        ),
        _get_test_case(
            targets=((1, "現有三"),),
            guides=((1, "參考三"), (2, "參考四")),
        ),
    )

    report = audit_gap_translation(target, guide, test_cases)
    unverified_report = audit_gap_translation(
        target,
        guide,
        test_cases,
        row_filter=VerificationAuditFilter.unverified,
    )
    ranged_report = audit_gap_translation(
        target,
        guide,
        test_cases,
        first_index=4,
        last_index=4,
    )
    block_report = audit_gap_translation(
        target,
        guide,
        test_cases,
        first_block=2,
        last_block=2,
    )

    assert "- empty translations: 1" in report
    assert "- unanswered gaps: 1" in report
    assert "| G 2<br>Q 2 | C 1<br>B 1 | 0 | 參考二 | G 1: 現有一 | (empty) |" in report
    assert (
        "| G 4<br>Q 2 | C 2<br>B 2 | 0 | 參考四 | G 3: 現有三 | "
        "(unanswered) |" in report
    )
    assert "- row filter: unverified" in unverified_report
    assert "- table rows: 1" in unverified_report
    assert "| G 2<br>Q 2 |" not in unverified_report
    assert "| G 4<br>Q 2 |" in unverified_report
    assert "- guide subtitle range: 4 through 4" in ranged_report
    assert "- logged cases: 1" in ranged_report
    assert "| G 4<br>Q 2 |" in ranged_report
    assert "- block range: 2 through 2" in block_report
    assert "| G 2<br>Q 2 |" not in block_report
    assert "| G 4<br>Q 2 |" in block_report


def test_audit_gap_translation_ignores_superseded_guide_revision():
    """Test a current query supersedes retained history with old guide text."""
    target = _get_series((0, 1000, "現有"))
    guide = _get_series(
        (0, 1000, "新參考一"),
        (1000, 2000, "新參考二"),
    )
    historical_case = _get_test_case(
        targets=((1, "現有"),),
        guides=((1, "舊參考一"), (2, "舊參考二")),
        outputs=((2, "舊翻譯"),),
    )
    current_case = _get_test_case(
        targets=((1, "現有"),),
        guides=((1, "新參考一"), (2, "新參考二")),
        outputs=((2, "新翻譯"),),
    )

    report = audit_gap_translation(
        target,
        guide,
        (historical_case, current_case),
    )

    assert "C 1" not in report
    assert "| G 2<br>Q 2 | C 2<br>B 1 |" in report
    assert "新翻譯" in report
    assert "舊翻譯" not in report


def test_audit_gap_translation_ignores_superseded_target_revision():
    """Test a current query supersedes retained history for the same guide block."""
    target = _get_series((0, 1000, "目前"))
    guide = _get_series(
        (0, 1000, "參考一"),
        (1000, 2000, "參考二"),
    )
    historical_case = _get_test_case(
        targets=((1, "舊文"),),
        guides=((1, "參考一"), (2, "參考二")),
        outputs=((2, "舊翻譯"),),
    )
    current_case = _get_test_case(
        targets=((1, "目前"),),
        guides=((1, "參考一"), (2, "參考二")),
        outputs=((2, "目前翻譯"),),
    )

    report = audit_gap_translation(
        target,
        guide,
        (historical_case, current_case),
    )

    assert "- logged cases: 1" in report
    assert "C 1" not in report
    assert "| G 2<br>Q 2 | C 2<br>B 1 |" in report
    assert "目前翻譯" in report
    assert "舊翻譯" not in report


def test_audit_gap_translation_rejects_invalid_range():
    """Test direct callers receive a domain error for an invalid range."""
    with raises(ScinoephileError, match="First index must be at least 1"):
        audit_gap_translation(Series(), Series(), (), first_index=0)

    with raises(ScinoephileError, match="First block must be at least 1"):
        audit_gap_translation(Series(), Series(), (), first_block=0)

    with raises(
        ScinoephileError,
        match="Subtitle-index and block ranges are mutually exclusive",
    ):
        audit_gap_translation(
            Series(),
            Series(),
            (),
            first_index=1,
            first_block=1,
        )


def test_audit_gap_translation_rejects_missing_current_case():
    """Test every selected current gap block requires a logged case."""
    target = _get_series(
        (0, 1000, "現有一"),
        (6000, 7000, "現有二"),
    )
    guide = _get_series(
        (0, 1000, "參考一"),
        (1000, 2000, "缺口一"),
        (6000, 7000, "參考二"),
        (7000, 8000, "缺口二"),
    )
    first_case = _get_test_case(
        targets=((1, "現有一"),),
        guides=((1, "參考一"), (2, "缺口一")),
        outputs=((2, "翻譯一"),),
    )

    with raises(ScinoephileError, match="no matching logged test case: 2"):
        audit_gap_translation(target, guide, (first_case,))

    first_block_report = audit_gap_translation(
        target,
        guide,
        (first_case,),
        first_block=1,
        last_block=1,
    )
    assert "| G 2<br>Q 2 | C 1<br>B 1 |" in first_block_report


def test_audit_gap_translation_rejects_unmatched_case():
    """Test a logged case absent from current blocks is rejected."""
    test_case = _get_test_case(
        targets=((1, "現有"),),
        guides=((1, "不同一"), (2, "不同二")),
        outputs=((2, "翻譯"),),
    )

    with raises(ScinoephileError, match="test case 1 was not found"):
        audit_gap_translation(
            _get_series((0, 1000, "現有")),
            _get_series((0, 1000, "參考一"), (1000, 2000, "參考二")),
            (test_case,),
        )


def test_audit_gap_translation_reuses_case_for_repeated_blocks():
    """Test one deduplicated case applies to every identical current block."""
    target = _get_series(
        (0, 1000, "現有"),
        (6000, 7000, "現有"),
    )
    guide = _get_series(
        (0, 1000, "重複一"),
        (1000, 2000, "重複二"),
        (6000, 7000, "重複一"),
        (7000, 8000, "重複二"),
    )
    test_case = _get_test_case(
        targets=((1, "現有"),),
        guides=((1, "重複一"), (2, "重複二")),
        outputs=((2, "翻譯"),),
    )

    report = audit_gap_translation(target, guide, (test_case,))

    block_report = audit_gap_translation(
        target,
        guide,
        (test_case,),
        first_block=2,
        last_block=2,
    )
    assert "- logged cases: 1" in report
    assert "- gaps: 2" in report
    assert "| G 2<br>Q 2 | C 1<br>B 1 |" in report
    assert "| G 4<br>Q 2 | C 1<br>B 2 |" in report
    assert "| G 4<br>Q 2 | C 1<br>B 2 |" in block_report


def _get_series(*events: tuple[int, int, str]) -> Series:
    """Construct a subtitle series with explicit timing.

    Arguments:
        *events: start time, end time, and text by subtitle
    Returns:
        constructed subtitle series
    """
    return Series(
        events=[
            Subtitle(start=start, end=end, text=text) for start, end, text in events
        ]
    )


def _get_test_case(
    *,
    targets: tuple[tuple[int, str], ...],
    guides: tuple[tuple[int, str], ...],
    outputs: tuple[tuple[int, str], ...] | None = None,
    verified: bool = False,
) -> GapTranslationTestCase:
    """Construct one gap-translation test case.

    Arguments:
        targets: query-local indexes and existing target texts
        guides: query-local indexes and guide texts
        outputs: optional query-local indexes and translated texts
        verified: whether the complete case is verified
    Returns:
        constructed gap-translation test case
    """
    answer = None
    if outputs is not None:
        answer = GapTranslationAnswer(
            outputs=[
                GapTranslationSubtitle(index=index, text=text)
                for index, text in outputs
            ]
        )
    return GapTranslationTestCase(
        query=GapTranslationQuery(
            targets=[
                GapTranslationSubtitle(index=index, text=text)
                for index, text in targets
            ],
            guides=[
                GapTranslationSubtitle(index=index, text=text) for index, text in guides
            ],
        ),
        answer=answer,
        verified=verified,
    )
