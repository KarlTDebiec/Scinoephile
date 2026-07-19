#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for guided subtitle review audit reports."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.guided_review_audit import (
    GuidedReviewAuditFilter,
    audit_guided_review,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.guided_review import GuidedReviewTestCase


def test_audit_guided_review_formats_and_sorts_subtitles():
    """Test sparse revisions and notes are rendered in subtitle order."""
    target, guide = _get_series_pair()
    first_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [
                    {"index": 1, "text": "甲|乙"},
                    {"index": 2, "text": "丙"},
                ],
                "guides": [{"index": 1, "text": "參考一"}],
            },
            "answer": {
                "revisions": [{"index": 2, "text": "修訂丙", "note": "correction"}]
            },
        }
    )
    second_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "丁"}],
                "guides": [{"index": 1, "text": "參考二"}],
            },
            "answer": {"revisions": []},
            "verified": True,
        }
    )

    report = audit_guided_review(target, guide, (second_case, first_case))

    assert "- subtitles: 3" in report
    assert "- revised subtitles: 1" in report
    assert "- unchanged subtitles: 2" in report
    assert "- unanswered subtitles: 0" in report
    assert "- verified subtitles: 1" in report
    assert "- unverified subtitles: 2" in report
    assert "| Index | Block | Guide | Target / revision | Notes | Verified |" in report
    first_row = "| 1 | 1 | 參考一 | 甲\\|乙 |  |  |"
    second_row = "| 2 | 1 | 參考一 | 丙<br>修訂丙 |  |  |"
    third_row = "| 3 | 2 | 參考二 | 丁 |  | ✓ |"
    assert report.index(first_row) < report.index(second_row) < report.index(third_row)


def test_audit_guided_review_formats_unanswered_case():
    """Test an absent answer is distinct from an explicit no-revision answer."""
    target = Series(events=[Subtitle(start=0, end=1000, text="原文")])
    guide = Series(events=[Subtitle(start=0, end=1000, text="參考")])
    test_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "原文"}],
                "guides": [{"index": 1, "text": "參考"}],
            }
        }
    )

    report = audit_guided_review(target, guide, (test_case,))

    assert "- revised subtitles: 0" in report
    assert "- unchanged subtitles: 0" in report
    assert "- unanswered subtitles: 1" in report
    assert "| 1 | 1 | 參考 | 原文<br>(unanswered) |  |  |" in report


def test_audit_guided_review_rejects_invalid_range():
    """Test direct callers receive a domain error for an invalid range."""
    target, guide = _get_series_pair()

    with raises(ScinoephileError, match="First index must be at least 1"):
        audit_guided_review(target, guide, (), first_index=0)


def test_audit_guided_review_filters_rows_and_target_range():
    """Test status filters and exact inclusive target ranges."""
    target, guide = _get_series_pair()
    test_cases = (
        GuidedReviewTestCase.model_validate(
            {
                "query": {
                    "targets": [
                        {"index": 1, "text": "甲|乙"},
                        {"index": 2, "text": "丙"},
                    ],
                    "guides": [{"index": 1, "text": "參考一"}],
                },
                "answer": {
                    "revisions": [{"index": 2, "text": "修訂丙", "note": "correction"}]
                },
            }
        ),
        GuidedReviewTestCase.model_validate(
            {
                "query": {
                    "targets": [{"index": 1, "text": "丁"}],
                    "guides": [{"index": 1, "text": "參考二"}],
                },
                "answer": {"revisions": []},
                "verified": True,
            }
        ),
    )

    changed_report = audit_guided_review(
        target,
        guide,
        test_cases,
        row_filter=GuidedReviewAuditFilter.changes,
    )
    unverified_report = audit_guided_review(
        target,
        guide,
        test_cases,
        row_filter=GuidedReviewAuditFilter.unverified,
    )
    ranged_report = audit_guided_review(
        target,
        guide,
        test_cases,
        first_index=3,
        last_index=3,
    )
    second_report = audit_guided_review(
        target,
        guide,
        test_cases,
        first_index=2,
        last_index=2,
    )
    block_report = audit_guided_review(
        target,
        guide,
        test_cases,
        first_block=2,
        last_block=2,
    )

    assert "- row filter: changes" in changed_report
    assert "- table rows: 1" in changed_report
    assert "| 2 | 1 | 參考一 | 丙<br>修訂丙 |  |  |" in changed_report
    assert "- row filter: unverified" in unverified_report
    assert "- table rows: 2" in unverified_report
    assert "| 1 | 1 | 參考一 | 甲\\|乙 |  |  |" in unverified_report
    assert "| 2 | 1 | 參考一 | 丙<br>修訂丙 |  |  |" in unverified_report
    assert "- subtitles: 1" in ranged_report
    assert "- target subtitle range: 3 through 3" in ranged_report
    assert "- table rows: 1" in ranged_report
    assert "| 3 | 2 | 參考二 | 丁 |  | ✓ |" in ranged_report
    assert "- subtitles: 1" in second_report
    assert "- target subtitle range: 2 through 2" in second_report
    assert "| 2 | 1 | 參考一 | 丙<br>修訂丙 |  |  |" in second_report
    assert "- block range: 2 through 2" in block_report
    assert "| 1 | 1 |" not in block_report
    assert "| 2 | 1 |" not in block_report
    assert "| 3 | 2 | 參考二 | 丁 |  | ✓ |" in block_report


def test_audit_guided_review_uses_latest_case_per_subtitle():
    """Test repeated logged cases emit only their latest decision."""
    target = Series(events=[Subtitle(start=0, end=1000, text="原文")])
    guide = Series(events=[Subtitle(start=0, end=1000, text="參考")])
    revised_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "原文"}],
                "guides": [{"index": 1, "text": "參考"}],
            },
            "answer": {
                "revisions": [{"index": 1, "text": "舊修訂", "note": "old correction"}]
            },
        }
    )
    unchanged_case = GuidedReviewTestCase.model_validate(
        {
            "query": revised_case.query.model_dump(),
            "answer": {"revisions": []},
            "verified": True,
        }
    )

    report = audit_guided_review(target, guide, (revised_case, unchanged_case))

    assert "- subtitles: 1" in report
    assert "- revised subtitles: 0" in report
    assert "- unchanged subtitles: 1" in report
    assert "- verified subtitles: 1" in report
    assert "- table rows: 1" in report
    assert "舊修訂" not in report
    assert "| 1 | 1 | 參考 | 原文 |  | ✓ |" in report


def test_audit_guided_review_ignores_superseded_segmentation_case():
    """Test a current case supersedes a stale case with old segmentation."""
    target = Series(
        events=[
            Subtitle(start=0, end=1000, text="甲"),
            Subtitle(start=1100, end=2000, text="乙丙"),
        ]
    )
    guide = Series(events=[Subtitle(start=0, end=2000, text="參考")])
    stale_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [
                    {"index": 1, "text": "甲"},
                    {"index": 2, "text": "乙"},
                    {"index": 3, "text": "丙"},
                ],
                "guides": [{"index": 1, "text": "參考"}],
            },
            "answer": {"revisions": []},
        }
    )
    current_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [
                    {"index": 1, "text": "甲"},
                    {"index": 2, "text": "乙丙"},
                ],
                "guides": [{"index": 1, "text": "參考"}],
            },
            "answer": {
                "revisions": [{"index": 2, "text": "修訂乙丙", "note": "correction"}]
            },
        }
    )

    report = audit_guided_review(target, guide, (stale_case, current_case))

    assert "| 1 | 1 | 參考 | 甲 |  |  |" in report
    assert "| 2 | 1 | 參考 | 乙丙<br>修訂乙丙 |  |  |" in report


def test_audit_guided_review_ignores_superseded_guide_revision():
    """Test a current guide correction supersedes the historical case."""
    target = Series(events=[Subtitle(start=0, end=1000, text="目標")])
    guide = Series(events=[Subtitle(start=0, end=1000, text="已更正參考")])
    stale_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "目標"}],
                "guides": [{"index": 1, "text": "舊參考"}],
            },
            "answer": {"revisions": [{"index": 1, "text": "舊修訂", "note": "old"}]},
        }
    )
    current_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "目標"}],
                "guides": [{"index": 1, "text": "已更正參考"}],
            },
            "answer": {
                "revisions": [{"index": 1, "text": "新修訂", "note": "current"}]
            },
        }
    )

    report = audit_guided_review(target, guide, (stale_case, current_case))

    assert "舊修訂" not in report
    assert "| 1 | 1 | 已更正參考 | 目標<br>新修訂 |  |  |" in report


def test_audit_guided_review_matches_after_punctuation_changes():
    """Test source punctuation changes do not obscure the reviewed input."""
    target = Series(events=[Subtitle(start=0, end=1000, text="原文！")])
    guide = Series(events=[Subtitle(start=0, end=1000, text="參考")])
    test_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "原文。"}],
                "guides": [{"index": 1, "text": "參考"}],
            },
            "answer": {"revisions": []},
        }
    )

    report = audit_guided_review(target, guide, (test_case,))

    assert "| 1 | 1 | 參考 | 原文。 |  |  |" in report


def test_audit_guided_review_allows_unaffected_range_before_changed_segmentation():
    """Test a range before later segmentation drift remains auditable."""
    target = Series(
        events=[
            Subtitle(start=0, end=1000, text="甲"),
            Subtitle(start=1100, end=2000, text="乙丙"),
        ]
    )
    guide = Series(events=[Subtitle(start=0, end=2000, text="參考")])
    test_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [
                    {"index": 1, "text": "甲"},
                    {"index": 2, "text": "乙"},
                    {"index": 3, "text": "丙"},
                ],
                "guides": [{"index": 1, "text": "參考"}],
            },
            "answer": {"revisions": []},
        }
    )

    report = audit_guided_review(
        target,
        guide,
        (test_case,),
        first_index=1,
        last_index=1,
    )

    assert "- table rows: 1" in report
    assert "| 1 | 1 | 參考 | 甲 |  |  |" in report


def test_audit_guided_review_rejects_selected_changed_segmentation():
    """Test selected rows cannot use stale target segmentation."""
    target = Series(
        events=[
            Subtitle(start=0, end=1000, text="甲"),
            Subtitle(start=1100, end=2000, text="乙丙"),
        ]
    )
    guide = Series(events=[Subtitle(start=0, end=2000, text="參考")])
    test_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [
                    {"index": 1, "text": "甲"},
                    {"index": 2, "text": "乙"},
                    {"index": 3, "text": "丙"},
                ],
                "guides": [{"index": 1, "text": "參考"}],
            },
            "answer": {"revisions": []},
        }
    )

    with raises(
        ScinoephileError, match="segmentation no longer matches subtitle index 2"
    ):
        audit_guided_review(
            target,
            guide,
            (test_case,),
            first_index=2,
            last_index=2,
        )


def test_audit_guided_review_ignores_unmatched_case_outside_range():
    """Test changed later block grouping does not prevent a partial audit."""
    target = Series(
        events=[
            Subtitle(start=0, end=1000, text="甲"),
            Subtitle(start=6000, end=7000, text="乙"),
        ]
    )
    guide = Series(
        events=[
            Subtitle(start=0, end=1000, text="參考一"),
            Subtitle(start=6000, end=6500, text="參考二"),
            Subtitle(start=6500, end=7000, text="新增參考"),
        ]
    )
    test_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "乙"}],
                "guides": [{"index": 1, "text": "參考二"}],
            },
            "answer": {"revisions": []},
        }
    )

    report = audit_guided_review(
        target,
        guide,
        (test_case,),
        first_index=1,
        last_index=1,
    )

    assert "- subtitles: 0" in report
    assert "- table rows: 0" in report


def test_audit_guided_review_allows_range_beyond_target():
    """Test an empty oversized range does not index beyond the target series."""
    target = Series(events=[Subtitle(start=0, end=1000, text="目前")])
    guide = Series(events=[Subtitle(start=0, end=1000, text="目前參考")])
    stale_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "舊文"}],
                "guides": [{"index": 1, "text": "舊參考"}],
            }
        }
    )

    report = audit_guided_review(
        target,
        guide,
        (stale_case,),
        first_index=2,
        last_index=2,
    )

    assert "- subtitles: 0" in report
    assert "- target subtitle range: 2 through 2" in report
    assert "- table rows: 0" in report


def test_audit_guided_review_rejects_changed_selected_target():
    """Test a selected target changed beyond punctuation cannot be indexed."""
    target = Series(events=[Subtitle(start=0, end=1000, text="原文")])
    guide = Series(events=[Subtitle(start=0, end=1000, text="參考")])
    test_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "不同"}],
                "guides": [{"index": 1, "text": "參考"}],
            }
        }
    )

    with raises(
        ScinoephileError, match="segmentation no longer matches subtitle index 1"
    ):
        audit_guided_review(target, guide, (test_case,))


def test_audit_guided_review_rejects_ambiguous_case():
    """Test repeated target and guide blocks cannot receive misleading indexes."""
    target = Series(
        events=[
            Subtitle(start=0, end=1000, text="原文"),
            Subtitle(start=6000, end=7000, text="原文"),
        ]
    )
    guide = Series(
        events=[
            Subtitle(start=0, end=1000, text="參考"),
            Subtitle(start=6000, end=7000, text="參考"),
        ]
    )
    test_case = GuidedReviewTestCase.model_validate(
        {
            "query": {
                "targets": [{"index": 1, "text": "原文"}],
                "guides": [{"index": 1, "text": "參考"}],
            }
        }
    )

    with raises(ScinoephileError, match="test case 1 is ambiguous.*1, 2"):
        audit_guided_review(target, guide, (test_case,))

    report = audit_guided_review(
        target,
        guide,
        (test_case,),
        first_block=2,
        last_block=2,
    )
    assert "| 2 | 2 | 參考 | 原文<br>(unanswered) |" in report


def _get_series_pair() -> tuple[Series, Series]:
    """Construct target and guide series containing two aligned blocks.

    Returns:
        target and guide subtitle series
    """
    target = Series(
        events=[
            Subtitle(start=0, end=1000, text="甲|乙"),
            Subtitle(start=1100, end=2000, text="丙"),
            Subtitle(start=6000, end=7000, text="丁"),
        ]
    )
    guide = Series(
        events=[
            Subtitle(start=0, end=2000, text="參考一"),
            Subtitle(start=6000, end=7000, text="參考二"),
        ]
    )
    return target, guide
