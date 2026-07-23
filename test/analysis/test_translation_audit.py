#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for standard and guided translation audit reports."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.audit.guided_translation import audit_guided_translation
from scinoephile.analysis.audit.translation import audit_translation
from scinoephile.analysis.audit.utils import VerificationAuditFilter
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.guided_translation import GuidedTranslationTestCase
from scinoephile.llms.translation import TranslationTestCase


def test_audit_translation_formats_standard_blocks_and_unanswered_case():
    """Test standard translation rows retain global, local, case, and block indexes."""
    source = _get_series((0, "甲"), (1000, "乙"), (6000, "丙"))
    test_cases = (
        TranslationTestCase.model_validate(
            {
                "query": {
                    "subtitles": [
                        {"index": 1, "text": "甲"},
                        {"index": 2, "text": "乙"},
                    ]
                },
                "answer": {
                    "outputs": [
                        {"index": 1, "text": "A"},
                        {"index": 2, "text": "B"},
                    ]
                },
                "verified": True,
            }
        ),
        TranslationTestCase.model_validate(
            {"query": {"subtitles": [{"index": 1, "text": "丙"}]}}
        ),
    )

    report = audit_translation(source, test_cases)
    unverified_report = audit_translation(
        source,
        test_cases,
        row_filter=VerificationAuditFilter.unverified,
    )
    block_report = audit_translation(
        source,
        test_cases,
        first_block=2,
        last_block=2,
    )

    assert report.startswith("# Standard Translation Audit\n")
    assert "- logged cases: 2" in report
    assert "- translated subtitles: 2" in report
    assert "- unanswered subtitles: 1" in report
    assert "| S 1<br>Q 1 | C 1<br>B 1 | 0 | 甲 | — | A |  | ✓ |" in report
    assert "| S 3<br>Q 1 | C 2<br>B 2 | 0 | 丙 | — | (unanswered) |" in report
    assert "- table rows: 1" in unverified_report
    assert "| S 3<br>Q 1 |" in unverified_report
    assert "- block range: 2 through 2" in block_report
    assert "| S 1<br>Q 1 |" not in block_report
    assert "| S 3<br>Q 1 |" in block_report


def test_audit_guided_translation_formats_guide_and_filters_range():
    """Test guided translation displays guide context and filters its range."""
    source = _get_series((0, "甲"), (1000, "乙"))
    guide = _get_series((0, "Guide one"), (1000, "Guide two"))
    test_case = GuidedTranslationTestCase.model_validate(
        {
            "query": {
                "subtitles": [
                    {"index": 1, "text": "甲"},
                    {"index": 2, "text": "乙"},
                ],
                "guides": [
                    {"index": 1, "text": "Guide one"},
                    {"index": 2, "text": "Guide two"},
                ],
            },
            "answer": {
                "outputs": [
                    {"index": 1, "text": "A"},
                    {"index": 2, "text": "B"},
                ]
            },
            "difficulty": 2,
        }
    )

    report = audit_guided_translation(
        source,
        guide,
        (test_case,),
        first_index=2,
        last_index=2,
    )

    assert report.startswith("# Guided Translation Audit\n")
    assert "- source subtitle range: 2 through 2" in report
    assert "- table rows: 1" in report
    assert (
        "| S 2<br>Q 2 | C 1<br>B 1 | 2 | 乙 | "
        "G 1: Guide one<br>G 2: Guide two | B |  |  |"
    ) in report


def test_audit_translation_formats_empty_output():
    """Test an empty answered output remains visible and separately counted."""
    source = _get_series((0, "甲"))
    test_case = TranslationTestCase.model_validate(
        {
            "query": {"subtitles": [{"index": 1, "text": "甲"}]},
            "answer": {"outputs": [{"index": 1, "text": ""}]},
        }
    )

    report = audit_translation(source, (test_case,))

    assert "- translated subtitles: 0" in report
    assert "- empty translations: 1" in report
    assert "- unanswered subtitles: 0" in report
    assert "| S 1<br>Q 1 | C 1<br>B 1 | 0 | 甲 | — | (empty) |" in report


def test_audit_translation_rejects_ambiguous_repeated_block():
    """Test repeated current blocks require a range that selects only one."""
    source = _get_series((0, "重複"), (6000, "重複"))
    test_case = TranslationTestCase.model_validate(
        {
            "query": {"subtitles": [{"index": 1, "text": "重複"}]},
            "answer": {"outputs": [{"index": 1, "text": "Repeated"}]},
        }
    )

    with raises(ScinoephileError, match="blocks 1, 2 have identical"):
        audit_translation(source, (test_case,))

    second_block_report = audit_translation(
        source,
        (test_case,),
        first_block=2,
        last_block=2,
    )
    assert "| S 2<br>Q 1 | C 1<br>B 2 |" in second_block_report


def test_audit_translation_uses_latest_case_and_rejects_invalid_selection():
    """Test latest-case selection and direct API validation."""
    source = _get_series((0, "甲"))
    old_case = TranslationTestCase.model_validate(
        {
            "query": {"subtitles": [{"index": 1, "text": "甲"}]},
            "answer": {"outputs": [{"index": 1, "text": "Old"}]},
        }
    )
    new_case = TranslationTestCase.model_validate(
        {
            "query": old_case.query.model_dump(),
            "answer": {"outputs": [{"index": 1, "text": "New"}]},
            "verified": True,
        }
    )

    report = audit_translation(source, (old_case, new_case))

    assert "C 1" not in report
    assert "| S 1<br>Q 1 | C 2<br>B 1 |" in report
    assert "New" in report
    assert "Old" not in report
    with raises(ScinoephileError, match="First index must be at least 1"):
        audit_translation(source, (new_case,), first_index=0)
    with raises(ScinoephileError, match="no matching logged test case"):
        audit_translation(source, ())
    with raises(
        ScinoephileError,
        match="Subtitle-index and block ranges are mutually exclusive",
    ):
        audit_translation(
            source,
            (new_case,),
            first_index=1,
            first_block=1,
        )


def _get_series(*events: tuple[int, str]) -> Series:
    """Build a subtitle series from start times and text.

    Arguments:
        *events: subtitle start and text pairs
    Returns:
        subtitle series
    """
    return Series(
        events=[
            Subtitle(start=start, end=start + 500, text=text) for start, text in events
        ]
    )
