#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for shared audit-report helpers."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.audit.delineation import DelineationAuditFilter
from scinoephile.analysis.audit.punctuation import PunctuationAuditFilter
from scinoephile.analysis.audit.review import ReviewAuditFilter
from scinoephile.analysis.audit.utils import (
    AuditFilter,
    format_audit_report,
    resolve_contextual_index,
)


def test_workflow_audit_filters_share_one_enum():
    """Test compatible workflow filter exports reuse the shared enum."""
    assert DelineationAuditFilter is AuditFilter
    assert PunctuationAuditFilter is AuditFilter
    assert ReviewAuditFilter is AuditFilter


def test_format_audit_report_formats_ranges_and_table():
    """Test shared report framing includes optional ranges and table rows."""
    report = format_audit_report(
        title="Example Audit",
        summary_lines=("- cases: 1",),
        column_labels=("Index", "Text"),
        column_separators=("---:", "---"),
        rows=("| 2 | example |",),
        first_index=2,
        last_index=3,
        index_track_name="target",
        first_block=4,
    )

    assert report == (
        "# Example Audit\n"
        "\n"
        "## Summary\n"
        "\n"
        "- cases: 1\n"
        "- target subtitle range: 2 through 3\n"
        "- block range: from 4\n"
        "- table rows: 1\n"
        "\n"
        "## Audit Table\n"
        "\n"
        "| Index | Text |\n"
        "|---:|---|\n"
        "| 2 | example |\n"
    )


def test_format_audit_report_rejects_mismatched_table_columns():
    """Test table labels and separators must describe the same columns."""
    with raises(ValueError, match="same length"):
        format_audit_report(
            title="Example Audit",
            summary_lines=(),
            column_labels=("Index", "Text"),
            column_separators=("---:",),
            rows=(),
        )


def test_resolve_contextual_index_returns_direct_index():
    """Test a directly resolved index is returned without modification."""
    resolved_indexes = [2, None]

    index = resolve_contextual_index((1, 2), resolved_indexes, 0)

    assert index == 2
    assert resolved_indexes == [2, None]


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
