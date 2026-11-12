#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Selection and counts for review audit rows."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace
from functools import cached_property

from scinoephile.core.subtitles.search import parse_block_query

from .rows import AuditRow, AuditStatus

__all__ = ["AuditFilters"]

_VERIFICATION_STATES = ("unverified", "verified")
"""Suffixes shared by proofreading and audit filter values."""

_PROOFREADING_STATES = ("unchanged", "changed")
"""Proofreading states in boolean change order."""


@dataclass(frozen=True)
class AuditFilters:
    """Bookmarkable proofreading, audit, and search filters."""

    proofreading: str = "all"
    """Proofreading change and verification status, or all."""
    audit: str = "all"
    """Audit finding and verification status, or all."""
    q: str = ""
    """Unicode text search or an exact block selector such as block 160."""

    def counts(self, rows: list[AuditRow]) -> dict[str, dict[str, int]]:
        """Count options with the other filter and search still applied.

        Arguments:
            rows: complete current subtitle snapshot, before pagination
        Returns:
            counts keyed by filter name and option value
        """
        self.validate()
        counts = {}
        for name, statuses, get_status in (
            ("proofreading", _PROOFREADING_STATES, _get_proofreading_status),
            ("audit", AuditStatus, _get_audit_status),
        ):
            other_filters = replace(self, **{name: "all"})
            options = dict.fromkeys(_get_options(statuses), 0)
            for row in rows:
                if other_filters.matches(row):
                    status, state = get_status(row)
                    options["all"] += 1
                    options[status] += 1
                    options[f"{status}-{state}"] += 1
            counts[name] = options
        return counts

    def matches(self, row: AuditRow) -> bool:
        """Check whether one row matches these filters.

        Arguments:
            row: current audit row
        Returns:
            whether the row matches
        """
        status, state = _get_proofreading_status(row)
        if self.proofreading not in ("all", status, f"{status}-{state}"):
            return False
        status, state = _get_audit_status(row)
        if self.audit not in ("all", status, f"{status}-{state}"):
            return False
        if self._block_number is not None:
            return row.block_number == self._block_number
        searchable = (
            f"{row.index} {row.original} {row.reviewed} {row.notes} {row.review_note}"
        )
        return self.q.casefold() in searchable.casefold()

    def validate(self):
        """Reject unsupported filter values.

        Raises:
            ValueError: if a filter is unsupported
        """
        for value, statuses in (
            (self.proofreading, _PROOFREADING_STATES),
            (self.audit, AuditStatus),
        ):
            if value not in _get_options(statuses):
                raise ValueError(f"Unknown audit filter: {value}")

    @cached_property
    def _block_number(self) -> int | None:
        """Block number to match, when the query selects a block."""
        return parse_block_query(self.q)


def _get_audit_status(row: AuditRow) -> tuple[str, str]:
    """Get the row's audit finding and verification.

    Arguments:
        row: current audit row
    Returns:
        audit status and verification state
    """
    return row.finding.value, _VERIFICATION_STATES[row.verified]


def _get_options(statuses: Iterable[str]) -> tuple[str, ...]:
    """Get selectable status and verification combinations.

    Arguments:
        statuses: operation-specific status values
    Returns:
        all, each status, and its two verification options
    """
    options = ["all"]
    for status in statuses:
        options.append(status)
        options.extend(f"{status}-{state}" for state in _VERIFICATION_STATES)
    return tuple(options)


def _get_proofreading_status(row: AuditRow) -> tuple[str, str]:
    """Get the row's proofreading change status and verification.

    Arguments:
        row: current audit row
    Returns:
        proofreading status and verification state
    """
    status = _PROOFREADING_STATES[row.changed]
    return status, _VERIFICATION_STATES[row.proofreading_verified]
