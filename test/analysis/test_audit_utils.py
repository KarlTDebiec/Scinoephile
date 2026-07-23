#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for shared audit-report helpers."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.audit.utils import (
    AuditFilter,
    format_audit_report,
    format_verification_marker,
    resolve_contextual_index,
)
from scinoephile.core.exceptions import ScinoephileError


def test_audit_filter_has_common_options():
    """Test the shared audit filter exposes the common row options."""
    assert tuple(AuditFilter) == (
        AuditFilter.all,
        AuditFilter.changes,
        AuditFilter.unverified,
    )


def test_format_audit_report_formats_block_range():
    """Test shared report framing includes an optional block range."""
    report = format_audit_report(
        title="Example Audit",
        summary_items=(),
        columns=(("Index", "right"),),
        rows=(),
        first_block=4,
    )

    assert "- block range: from 4" in report


def test_format_audit_report_formats_ranges_and_table():
    """Test shared report framing includes optional ranges and table rows."""
    report = format_audit_report(
        title="Example Audit",
        summary_items=("cases: 1",),
        columns=(("Index", "right"), ("Text | value", "left")),
        rows=(("2", "example|line\nnext"),),
        first_index=2,
        last_index=3,
        index_track_name="target",
    )

    assert report == (
        "# Example Audit\n"
        "\n"
        "## Summary\n"
        "\n"
        "- cases: 1\n"
        "- target subtitle range: 2 through 3\n"
        "- table rows: 1\n"
        "\n"
        "## Audit Table\n"
        "\n"
        "| Index | Text \\| value |\n"
        "|---:|---|\n"
        "| 2 | example\\|line<br>next |\n"
    )


def test_format_audit_report_rejects_invalid_semantic_data():
    """Test report ranges, column alignments, and row widths are validated."""
    with raises(ScinoephileError, match="ranges are mutually exclusive"):
        format_audit_report(
            title="Example Audit",
            summary_items=(),
            columns=(("Index", "right"),),
            rows=(),
            first_index=1,
            first_block=1,
        )

    with raises(ValueError, match="Unsupported table column alignment"):
        format_audit_report(
            title="Example Audit",
            summary_items=(),
            columns=(("Index", "diagonal"),),  # ty: ignore[invalid-argument-type]
            rows=(),
        )

    with raises(ValueError, match="Table row 1 has 1 cells; expected 2"):
        format_audit_report(
            title="Example Audit",
            summary_items=(),
            columns=(("Index", "right"), ("Text", "left")),
            rows=(("1",),),
        )


def test_format_verification_marker_formats_semantic_state():
    """Test verification states use the shared report markers."""
    assert format_verification_marker(True) == "✓"
    assert format_verification_marker(False) == ""
    assert format_verification_marker(None) == "—"


def test_resolve_contextual_index_memoizes_contextual_match():
    """Test a contextual match is retained for resolving later cases."""
    resolved_indexes = [0, None, 4]

    index = resolve_contextual_index((1, 3), resolved_indexes, 1)

    assert index == 1
    assert resolved_indexes == [0, 1, 4]


def test_resolve_contextual_index_retains_ambiguity_without_anchors():
    """Test repeated candidates remain unresolved without neighboring anchors."""
    resolved_indexes = [None, None, None]

    index = resolve_contextual_index((1, 3), resolved_indexes, 1)

    assert index is None
    assert resolved_indexes == [None, None, None]


def test_resolve_contextual_index_returns_direct_index():
    """Test a directly resolved index is returned without modification."""
    resolved_indexes = [2, None]

    index = resolve_contextual_index((1, 2), resolved_indexes, 0)

    assert index == 2
    assert resolved_indexes == [2, None]
