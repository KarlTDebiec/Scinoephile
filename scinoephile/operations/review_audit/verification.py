#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Selection checks and updates for bulk subtitle verification."""

from __future__ import annotations

from collections.abc import Iterable
from hashlib import sha256
from itertools import groupby
from operator import attrgetter

from .filters import AuditFilters
from .rows import AuditRow, AuditStatus

__all__ = ["get_verification_rows", "get_verification_token"]


def get_verification_rows(
    rows: Iterable[AuditRow], filters: AuditFilters
) -> list[AuditRow]:
    """Select complete, unverified audit blocks whose rows all match the filters.

    Arguments:
        rows: current editor rows in source order
        filters: filters used to select rows for bulk verification
    Returns:
        every row in each eligible block, in source order
    """
    filters.validate()
    selected = []
    for _, group in groupby(rows, key=attrgetter("block_number")):
        block = list(group)
        if all(
            not row.verified
            and row.finding != AuditStatus.unaudited
            and filters.matches(row)
            for row in block
        ):
            selected.extend(block)
    return selected


def get_verification_token(rows: Iterable[AuditRow]) -> str:
    """Identify the matching row versions for bulk verification.

    Arguments:
        rows: rows matching the current filters in source order
    Returns:
        digest of the matching row identities and versions
    """
    selection = [(row.key, row.version) for row in rows]
    return sha256(repr(selection).encode()).hexdigest()
