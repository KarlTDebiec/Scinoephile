#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of aligned subtitle diff audits."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.aligned_diff_audit import (
    AlignedDiffAuditFilter,
    audit_aligned_diff,
)
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle


def test_audit_aligned_diff_defaults_to_changes_with_optional_tracks():
    """Test changed aligned rows and their timing-matched ancillary text."""
    original = _get_series((0, 500, "甲原"), (1000, 1500, "相同"))
    transcription = _get_series((0, 500, "甲錯"), (1000, 1500, "相同"))
    reference = _get_series((0, 500, "甲正"), (1000, 1500, "相同"))
    guide = _get_series(
        (0, 500, "指南一"),
        (1000, 1500, "指南二"),
    )

    report = audit_aligned_diff(transcription, reference, guide, original=original)

    assert report.startswith("# Aligned Subtitle Diff Audit\n")
    assert "- original: included" in report
    assert "- guide: included" in report
    assert "- differing rows: 1" in report
    assert "- equal rows: 1" in report
    assert "- row filter: changes" in report
    assert "- table rows: 1" in report
    assert "| Indexes | Alignment | Notes |" in report
    assert (
        "| T 1<br>R 1 | <pre>O │ 甲原<br>T │ 甲錯<br>R │ 甲正<br>G │ 指南一</pre> |  |"
        in report
    )
    assert "指南二" not in report


def test_audit_aligned_diff_all_includes_equal_multiline_event():
    """Test equal rows and multiline text retain subtitle event indices."""
    transcription = _get_series((0, 500, "甲\\N乙"), (1000, 1500, "相同"))
    reference = _get_series((0, 500, "甲\\N丙"), (1000, 1500, "相同"))

    report = audit_aligned_diff(
        transcription,
        reference,
        row_filter=AlignedDiffAuditFilter.all,
    )

    assert "- table rows: 3" in report
    assert report.count("| T 1<br>R 1 |") == 2
    assert "| T 2<br>R 2 | <pre>T │ 相同<br>R │ 相同</pre> |  |" in report


def test_audit_aligned_diff_range_includes_reference_only_insertions():
    """Test reference insertions overlapping the transcription range are included."""
    transcription = _get_series(
        (0, 500, "相同一"),
        (1000, 2000, "相同二"),
    )
    reference = _get_series(
        (0, 500, "相同一"),
        (1200, 1300, "新增"),
        (1500, 2000, "相同二"),
    )

    report = audit_aligned_diff(
        transcription,
        reference,
        row_filter=AlignedDiffAuditFilter.all,
        first_index=2,
        last_index=2,
    )

    assert "- transcription subtitle range: 2 through 2" in report
    assert "- table rows: 2" in report
    assert "| T —<br>R 2 | <pre>T │ <br>R │ 新增</pre> |  |" in report
    assert "| T 2<br>R 3 | <pre>T │ 相同二<br>R │ 相同二</pre> |  |" in report
    assert "T 1" not in report


def test_audit_aligned_diff_rejects_combined_block_and_subtitle_ranges():
    """Test block and subtitle range selection is mutually exclusive."""
    transcription = _get_series(
        (0, 500, "第一"),
        (1000, 1500, "第二"),
        (6000, 6500, "第三錯"),
    )
    reference = _get_series(
        (0, 500, "第一"),
        (1000, 1500, "第二"),
        (6000, 6500, "第三正"),
    )

    with raises(ScinoephileError, match="ranges are mutually exclusive"):
        audit_aligned_diff(
            transcription,
            reference,
            first_index=2,
            first_block=2,
            last_block=2,
        )


def test_audit_aligned_diff_rejects_invalid_range_and_track_alignment():
    """Test invalid ranges and guide timings raise user-facing errors."""
    transcription = _get_series((0, 500, "甲"))
    reference = _get_series((0, 500, "乙"))
    guide = _get_series((501, 1000, "指南"))

    with raises(ScinoephileError, match="less than or equal"):
        audit_aligned_diff(
            transcription,
            reference,
            first_index=2,
            last_index=1,
        )
    with raises(ScinoephileError, match="First block must be at least 1"):
        audit_aligned_diff(transcription, reference, first_block=0)
    with raises(ScinoephileError, match="no exact timing match"):
        audit_aligned_diff(transcription, reference, guide)
    guide_with_extra_subtitle = _get_series(
        (0, 500, "指南"),
        (501, 1000, "額外指南"),
    )
    with raises(ScinoephileError, match="at guide index 2"):
        audit_aligned_diff(transcription, reference, guide_with_extra_subtitle)
    original_report = audit_aligned_diff(
        transcription,
        reference,
        original=guide,
    )
    assert "<pre>O │ <br>T │ 甲<br>R │ 乙</pre>" in original_report


def _get_series(*events: tuple[int, int, str]) -> Series:
    """Build a subtitle series from start, end, and text tuples.

    Arguments:
        *events: subtitle start, end, and text tuples
    Returns:
        subtitle series
    """
    return Series(
        events=[
            Subtitle(start=start, end=end, text=text) for start, end, text in events
        ]
    )
