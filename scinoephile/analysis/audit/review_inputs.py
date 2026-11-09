#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle tracks and decision logs passed to review audits."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from scinoephile.core.subtitles import Series
from scinoephile.llms.review import ReviewTestCase

__all__ = ["ReviewAuditBeforeAfterPair", "ReviewAuditSeriesPair"]


@dataclass(frozen=True, kw_only=True)
class ReviewAuditSeriesPair:
    """One final comparison between outputs of an audit workflow."""

    column_label: str
    """Human-readable label used for the report table column."""
    summary_label: str
    """Human-readable label used before "discrepancies" in the summary."""
    one: Series
    """First subtitle series in the comparison."""
    two: Series
    """Second subtitle series in the comparison."""


@dataclass(frozen=True, kw_only=True)
class ReviewAuditBeforeAfterPair:
    """One subtitle review's input, output, and optional notes.

    A pair is the reusable unit shared by single-review, sequential, and parallel
    audit workflows.
    """

    label: str
    """Human-readable label used in the report, without the word "review"."""
    original: Series
    """Subtitle series before review."""
    reviewed: Series
    """Subtitle series after review."""
    review_cases: Sequence[ReviewTestCase] = ()
    """Optional review test cases containing revision notes."""
