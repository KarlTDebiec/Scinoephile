#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Selection and counts for review audit rows."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

from .rows import AuditRow, AuditStatus

__all__ = ["AuditFilters"]


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
