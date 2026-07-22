#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for OCR-fusion audit reports."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.audit.ocr_fusion import (
    OcrFusionAuditFilter,
    audit_ocr_fusion,
)
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.ocr_fusion import OcrFusionTestCase


def test_audit_ocr_fusion_formats_llm_decision_and_validated_discrepancy():
    """Test LLM metadata and optional validated truth are shown together."""
    source_one = _get_series("相同", "甲錯")
    source_two = _get_series("相同", "甲正")
    fused = _get_series("相同", "甲正")
    validated = _get_series("相同", "甲真")
    test_case = OcrFusionTestCase.model_validate(
        {
            "query": {"source_one": "甲錯", "source_two": "甲正"},
            "answer": {"output": "甲正", "note": "Used source two."},
            "difficulty": 2,
            "verified": True,
        }
    )

    report = audit_ocr_fusion(
        source_one,
        source_two,
        fused,
        (test_case,),
        validated=validated,
    )
    discrepancy_report = audit_ocr_fusion(
        source_one,
        source_two,
        fused,
        (test_case,),
        validated=validated,
        row_filter=OcrFusionAuditFilter.discrepancies,
    )

    assert report.startswith("# OCR Fusion Audit\n")
    assert "- source disagreements: 1" in report
    assert "- validated discrepancies: 1" in report
    assert "- row filter: changes" in report
    assert (
        "| Index | Case | Difficulty | Source one | Source two | Fused | "
        "Validated | Notes | Verified |" in report
    )
    assert "| 2 | 1 | 2 | 甲錯 | 甲正 | 甲正 | 甲真 | Used source two. | ✓ |" in report
    assert "- row filter: discrepancies" in discrepancy_report
    assert "- table rows: 1" in discrepancy_report


def test_audit_ocr_fusion_filters_unverified_and_automatic_rows():
    """Test automatic rows and unanswered LLM cases remain distinguishable."""
    source_one = _get_series("相同", "只有一", "甲")
    source_two = _get_series("相同", "", "乙")
    fused = _get_series("相同", "只有一", "甲")
    test_case = OcrFusionTestCase.model_validate(
        {"query": {"source_one": "甲", "source_two": "乙"}}
    )

    report = audit_ocr_fusion(
        source_one,
        source_two,
        fused,
        (test_case,),
        row_filter=OcrFusionAuditFilter.all,
    )
    unverified_report = audit_ocr_fusion(
        source_one,
        source_two,
        fused,
        (test_case,),
        row_filter=OcrFusionAuditFilter.unverified,
    )

    assert "| 1 | — | — | 相同 | 相同 | 相同 | — | Sources identical |" in report
    assert "| 2 | — | — | 只有一 | — | 只有一 | — | Source two empty |" in report
    assert "| 3 | 1 | 1 | 甲 | 乙 | 甲 | — | (unanswered) |" in report
    assert "- table rows: 1" in unverified_report
    assert "| 3 | 1 |" in unverified_report


def test_audit_ocr_fusion_omits_log_columns_without_test_cases():
    """Test source and fused output can be audited without a decision log."""
    source_one = _get_series("甲錯")
    source_two = _get_series("甲正")
    fused = _get_series("甲正")

    report = audit_ocr_fusion(
        source_one,
        source_two,
        fused,
        row_filter=OcrFusionAuditFilter.all,
    )

    assert "- decision log: omitted" in report
    assert (
        "| Index | Case | Difficulty | Source one | Source two | Fused | Validated |"
        in report
    )
    assert "| 1 | — | — | 甲錯 | 甲正 | 甲正 | — |" in report
    assert "Notes" not in report
    assert "Verified" not in report


def test_audit_ocr_fusion_filters_fused_blocks():
    """Test block bounds select fused rows separated by long pauses."""
    source_one = Series(
        events=[
            Subtitle(start=0, end=500, text="相同一"),
            Subtitle(start=6000, end=6500, text="相同二"),
        ]
    )
    source_two = Series(
        events=[
            Subtitle(start=0, end=500, text="相同一"),
            Subtitle(start=6000, end=6500, text="相同二"),
        ]
    )
    fused = Series(
        events=[
            Subtitle(start=0, end=500, text="相同一"),
            Subtitle(start=6000, end=6500, text="相同二"),
        ]
    )

    report = audit_ocr_fusion(
        source_one,
        source_two,
        fused,
        (),
        row_filter=OcrFusionAuditFilter.all,
        first_block=2,
        last_block=2,
    )

    assert "- block range: 2 through 2" in report
    assert "| 1 | — |" not in report
    assert "| 2 | — |" in report


def test_audit_ocr_fusion_rejects_invalid_inputs():
    """Test invalid ranges, alignment, and missing truth raise domain errors."""
    one = _get_series("甲")
    two = _get_series("乙")
    test_case = OcrFusionTestCase.model_validate(
        {
            "query": {"source_one": "甲", "source_two": "乙"},
            "answer": {"output": "甲", "note": "Used source one."},
        }
    )

    with raises(ScinoephileError, match="First index must be at least 1"):
        audit_ocr_fusion(one, two, one, (test_case,), first_index=0)
    with raises(ScinoephileError, match="First block must be at least 1"):
        audit_ocr_fusion(one, two, one, (test_case,), first_block=0)
    with raises(ScinoephileError, match="mutually exclusive"):
        audit_ocr_fusion(
            one,
            two,
            one,
            (test_case,),
            first_index=1,
            first_block=1,
        )
    with raises(ScinoephileError, match="requires a validated"):
        audit_ocr_fusion(
            one,
            two,
            one,
            (test_case,),
            row_filter=OcrFusionAuditFilter.discrepancies,
        )

    misaligned = Series(events=[Subtitle(start=1000, end=1500, text="甲")])
    with raises(ScinoephileError, match="one-to-one timing-aligned"):
        audit_ocr_fusion(one, two, misaligned, (test_case,))


def _get_series(*texts: str) -> Series:
    """Build an exactly timed subtitle series.

    Arguments:
        *texts: subtitle texts
    Returns:
        subtitle series
    """
    return Series(
        events=[
            Subtitle(start=index * 1000, end=index * 1000 + 500, text=text)
            for index, text in enumerate(texts)
        ]
    )
