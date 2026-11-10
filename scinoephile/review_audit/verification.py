#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Selection checks and updates for bulk subtitle verification."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from hashlib import sha256

from .filters import AuditFilters
from .rows import AuditRow

__all__ = ["get_verification_token", "prepare_bulk_verification"]


def get_verification_token(rows: Iterable[AuditRow]) -> str:
    """Identify the matching row versions for bulk verification.

    Arguments:
        rows: rows matching the current filters in source order
    Returns:
        digest of the matching row identities and versions
    """
    selection = [(row.key, row.version) for row in rows]
    return sha256(repr(selection).encode()).hexdigest()


def prepare_bulk_verification(
    rows: Iterable[AuditRow], filters: AuditFilters, token: str
) -> list[AuditRow]:
    """Prepare verified rows after checking the full filtered selection.

    Arguments:
        rows: current editor rows in source order
        filters: filters used to select rows for bulk verification
        token: selection digest submitted with the verification request
    Returns:
        newly verified rows with incremented versions
    Raises:
        ValueError: if the selection is stale or an audit note is invalid
    """
    filters.validate()
    matching = [row for row in rows if filters.matches(row)]
    if token != get_verification_token(matching):
        raise ValueError("The matching subtitles changed. Reload before verifying.")
    verified = []
    for row in matching:
        if not row.verified:
            row.finding.validate_notes(row.notes)
            verified.append(replace(row, verified=True, version=row.version + 1))
    return verified
