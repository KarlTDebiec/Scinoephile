#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Filters for regular, guided, and dual subtitle review audits."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from .utils import format_block_range, format_index_range, validate_audit_range

__all__ = [
    "STANDARD_REVIEW_AUDIT_FILTERS",
    "ReviewAuditFilter",
    "ReviewAuditFilterGroup",
]


class ReviewAuditFilter(StrEnum):
    """Row filters supported by a subtitle review audit."""

    all = "all"
    """Include every eligible row."""

    changes = "changes"
    """Include rows with review edits or final discrepancies, if compared."""

    discrepancies = "discrepancies"
    """Include only final discrepancies between review paths."""

    unverified = "unverified"
    """Include only rows from cases not marked as verified."""


STANDARD_REVIEW_AUDIT_FILTERS = (
    ReviewAuditFilter.all,
    ReviewAuditFilter.changes,
    ReviewAuditFilter.unverified,
)
"""Row filters for review audits without a final comparison."""


@dataclass(frozen=True, kw_only=True)
class ReviewAuditFilterGroup:
    """Row, character, and range filters shared by review audit reports."""

    row_filter: ReviewAuditFilter = ReviewAuditFilter.changes
    """Row filter selected for the review workflow."""
    character_filter: tuple[str, ...] = ()
    """Characters to match in the subtitle text."""
    first_index: int | None = None
    """First included one-based subtitle index."""
    last_index: int | None = None
    """Last included one-based subtitle index."""
    first_block: int | None = None
    """First included one-based workflow block number."""
    last_block: int | None = None
    """Last included one-based workflow block number."""

    def __post_init__(self):
        """Validate the bounds before applying them to a review."""
        validate_audit_range(
            self.first_index, self.last_index, self.first_block, self.last_block
        )

    def get_summary_items(self, *, index_track_name: str | None = None) -> list[str]:
        """Describe the active filters for the report summary.

        Arguments:
            index_track_name: optional name of the indexed subtitle track
        Returns:
            report summary items describing the filters
        """
        items = [f"row filter: {self.row_filter.value}"]
        if self.character_filter:
            items.append(f"character filter: {', '.join(self.character_filter)}")
        index_range = format_index_range(
            self.first_index, self.last_index, track_name=index_track_name
        )
        if index_range is not None:
            items.append(index_range)
        block_range = format_block_range(self.first_block, self.last_block)
        if block_range is not None:
            items.append(block_range)
        return items

    def matches_characters(self, texts: Iterable[str]) -> bool:
        """Check whether any of the supplied texts matches the character filter.

        Arguments:
            texts: subtitle texts to search for each row
        Returns:
            whether the filter is empty or any character occurs in the texts
        """
        return not self.character_filter or any(
            character in text for text in texts for character in self.character_filter
        )
