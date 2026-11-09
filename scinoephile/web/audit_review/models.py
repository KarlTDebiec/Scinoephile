#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Rows, filters, and view models for subtitle review audits."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from enum import StrEnum

from scinoephile.analysis.alignment import pairwise

__all__ = ["AuditBlock", "AuditFilters", "AuditPage", "AuditRow", "AuditStatus"]


class AuditStatus(StrEnum):
    """Explicit verdict for an independent proofreading audit."""

    unaudited = "unaudited"
    """No audit verdict has been recorded."""
    review = "review"
    """The subtitle needs human review."""
    ok = "ok"
    """The audit found no issue."""


@dataclass(frozen=True)
class AuditFilters:
    """Bookmarkable audit filters."""

    verification: str = "all"
    """all, verified, or unverified audit progress."""
    changes: str = "all"
    """all, changed, or unchanged subtitle text."""
    finding: str = "all"
    """all, unaudited, review, or ok audit statuses."""
    q: str = ""
    """Unicode text search or an exact block selector such as block 160."""

    def counts(self, rows: list[AuditRow]) -> dict[str, dict[str, int]]:
        """Count each option with search and the other status filters applied.

        Arguments:
            rows: complete current subtitle snapshot, before pagination
        Returns:
            option counts keyed by filter name and option value
        """
        self.validate()
        counts: dict[str, dict[str, int]] = {}
        for name in ("changes", "finding", "verification"):
            other_filters = replace(self, **{name: "all"})
            matching = [row for row in rows if other_filters.matches(row)]
            if name == "changes":
                changed = sum(row.changed for row in matching)
                options = {"changed": changed, "unchanged": len(matching) - changed}
            elif name == "verification":
                verified = sum(row.verified for row in matching)
                options = {"verified": verified, "unverified": len(matching) - verified}
            else:
                options = {
                    status: sum(row.finding == status for row in matching)
                    for status in AuditStatus
                }
            counts[name] = {"all": len(matching), **options}
        return counts

    def matches(self, row: AuditRow) -> bool:
        """Check whether one row matches these filters.

        Arguments:
            row: current audit row
        Returns:
            whether the row matches
        """
        if not {
            "all": True,
            "verified": row.verified,
            "unverified": not row.verified,
        }.get(self.verification, False):
            return False
        if not {"all": True, "changed": row.changed, "unchanged": not row.changed}.get(
            self.changes, False
        ):
            return False
        if self.finding not in {"all", row.finding}:
            return False
        block = re.fullmatch(r"block\s*[:#]?\s*(\d+)", self.q.strip(), re.IGNORECASE)
        if block is not None:
            return row.block_number == int(block[1])
        searchable = (
            f"{row.index} {row.original} {row.reviewed} {row.notes} {row.review_note}"
        )
        return self.q.casefold() in searchable.casefold()

    def validate(self):
        """Reject unsupported filter values.

        Raises:
            ValueError: if a filter is unsupported
        """
        for value, choices in (
            (self.verification, {"all", "verified", "unverified"}),
            (self.changes, {"all", "changed", "unchanged"}),
            (self.finding, {"all", *AuditStatus}),
        ):
            if value not in choices:
                raise ValueError(f"Unknown audit filter: {value}")


@dataclass(frozen=True)
class AuditRow:
    """A subtitle pair, provenance, and its independent human audit state."""

    key: str
    """Content identity; changed inputs get fresh audit progress."""
    track_id: str
    """Track identifier."""
    label: str
    """Track display label."""
    language: str
    """Subtitle language tag."""
    index: int
    """One-based subtitle number."""
    start: int
    """Start time in milliseconds."""
    end: int
    """End time in milliseconds."""
    original: str
    """Validated source text."""
    reviewed: str
    """Proposed proofread text."""
    review_note: str
    """Read-only model explanation."""
    notes: str
    """Independent audit notes."""
    finding: AuditStatus = AuditStatus.unaudited
    """Independent audit verdict."""
    verified: bool = False
    """Human audit progress, independent of proofreading JSON verification."""
    version: int = 0
    """Optimistic concurrency version."""

    shared_indexes: tuple[int, ...] = ()
    """One-based subtitle indexes sharing this JSON decision."""

    block_number: int = 0
    """Stable one-based proofreading block number."""

    @property
    def changed(self) -> bool:
        """Whether proofreading changed this subtitle."""
        return self.original != self.reviewed

    @property
    def differences(self) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
        """CLI-compatible pairwise diff spans with safely escaped text."""
        if self.original == self.reviewed:
            return [(self.original, "match")], [(self.reviewed, "match")]
        original: list[tuple[str, str]] = []
        reviewed: list[tuple[str, str]] = []
        for column in pairwise.Alignment(self.original, self.reviewed).columns:
            kind = column.operation.name.lower()
            for character, spans in ((column.one, original), (column.two, reviewed)):
                if character is None:
                    continue
                if spans and spans[-1][1] == kind:
                    spans[-1] = (spans[-1][0] + character, kind)
                else:
                    spans.append((character, kind))
        return original, reviewed

    @property
    def time_label(self) -> str:
        """Start and end times including milliseconds."""
        return f"{_format_time(self.start)} – {_format_time(self.end)}"


@dataclass(frozen=True)
class AuditBlock:
    """A complete proofreading query group and its visible filtered rows."""

    number: int
    """Stable one-based block number in the complete subtitle track."""
    first_index: int
    """First one-based subtitle index in the complete block."""
    last_index: int
    """Last one-based subtitle index in the complete block."""
    rows: list[AuditRow]
    """Rows matching the active filters."""
    start: int
    """Start of the complete block in milliseconds."""
    end: int
    """End of the complete block in milliseconds."""

    @property
    def count(self) -> int:
        """Total subtitle count before filtering."""
        return self.last_index - self.first_index + 1

    @property
    def time_label(self) -> str:
        """Full block time range in whole seconds, including hidden rows."""
        start = _format_time(self.start, include_milliseconds=False)
        end = _format_time(self.end, include_milliseconds=False)
        return f"{start} – {end}"


@dataclass(frozen=True)
class AuditPage:
    """A bounded batch or loaded prefix and project-wide progress counts."""

    all_rows: list[AuditRow]
    """Complete row snapshot from which this page was built."""
    rows: list[AuditRow]
    """Visible rows."""
    blocks: list[AuditBlock]
    """Loaded matching query groups, with filtered rows inside."""
    filters: AuditFilters
    """Normalized filters."""
    total: int
    """Total current source rows."""
    verified: int
    """Verified current source rows."""
    matching: int
    """Rows matching all filters, including unloaded blocks."""
    verification_token: str
    """Digest of the full filtered selection and its row versions."""
    filter_counts: dict[str, dict[str, int]]
    """Dependent option counts before pagination."""
    last_block: int
    """Stable source block cursor through which rows have loaded."""
    has_more: bool
    """Whether more matching blocks follow the loaded cursor."""


def _format_time(milliseconds: int, *, include_milliseconds: bool = True) -> str:
    """Format a subtitle timestamp with optional millisecond precision.

    Arguments:
        milliseconds: subtitle timestamp
        include_milliseconds: whether to append fractional seconds
    Returns:
        hours, minutes, seconds and milliseconds
    """
    seconds, remainder = divmod(milliseconds, 1000)
    formatted = f"{seconds // 3600:02d}:{seconds // 60 % 60:02d}:{seconds % 60:02d}"
    if include_milliseconds:
        formatted += f".{remainder:03d}"
    return formatted
