#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Selection checks and updates for bulk subtitle verification."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
from itertools import groupby
from operator import attrgetter

from .filters import AuditFilters
from .rows import AuditRow, AuditStatus

__all__ = ["VerificationSelection", "get_verification_selection"]


@dataclass(frozen=True)
class VerificationSelection:
    """Complete visible blocks eligible for verification."""

    blocks: tuple[tuple[AuditRow, ...], ...]
    """Eligible blocks, with rows in source order."""
    proofreading: bool
    """Whether these blocks were selected for proofreading verification."""

    @property
    def token(self) -> str:
        """Digest of the eligible row identities and versions."""
        versions = [(row.key, row.version) for block in self.blocks for row in block]
        return sha256(repr((self.proofreading, versions)).encode()).hexdigest()


def get_verification_selection(
    rows: Iterable[AuditRow], filters: AuditFilters, *, through: int, proofreading: bool
) -> VerificationSelection:
    """Select complete visible blocks eligible for verification.

    Arguments:
        rows: complete editor rows in source order
        filters: filters for displayed subtitles
        through: last loaded block number
        proofreading: select proofreading cases instead of audit cases
    Returns:
        visible blocks whose corresponding cases can be approved
    """
    filters.validate()
    selected = []
    for number, group in groupby(rows, key=attrgetter("block_number")):
        if number > through:
            break
        block = tuple(group)
        if not all(filters.matches(row) for row in block):
            continue
        if proofreading:
            eligible = any(not row.proofreading_verified for row in block)
        else:
            eligible = all(
                not row.verified and row.finding != AuditStatus.unaudited
                for row in block
            )
        if eligible:
            selected.append(block)
    return VerificationSelection(tuple(selected), proofreading)
