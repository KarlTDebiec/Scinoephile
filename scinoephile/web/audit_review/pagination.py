#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pagination for the review audit editor."""

from __future__ import annotations

from collections.abc import Sequence

from . import verification
from .models import AuditBlock, AuditFilters, AuditPage, AuditRow

__all__ = ["get_audit_page"]


def get_audit_page(
    rows: list[AuditRow],
    block_ranges: Sequence[tuple[int, int]],
    filters: AuditFilters,
    *,
    page_size: int,
    after: int,
    through: int | None,
) -> AuditPage:
    """Build one page from a snapshot of the audit rows and block ranges.

    Arguments:
        rows: complete snapshot in source order
        block_ranges: zero-based inclusive/exclusive ranges for the full track
        filters: requested filters
        page_size: maximum number of blocks in a new batch
        after: stable source block cursor before a new batch
        through: inclusive cursor for an already loaded prefix, or None for a batch
    Returns:
        loaded blocks and complete filtered progress counts
    """
    matching = [row for row in rows if filters.matches(row)]
    by_block: dict[int, list[AuditRow]] = {}
    for row in matching:
        by_block.setdefault(row.block_number, []).append(row)
    blocks = []
    for number, visible in by_block.items():
        first, last = block_ranges[number - 1]
        blocks.append(
            AuditBlock(
                number=number,
                first_index=first + 1,
                last_index=last,
                rows=visible,
                start=rows[first].start,
                end=max(row.end for row in rows[first:last]),
            )
        )
    visible_blocks = [block for block in blocks if block.number > after][:page_size]
    last_block = after
    if through is not None:
        visible_blocks = [block for block in blocks if block.number <= through]
        last_block = through
    elif visible_blocks:
        last_block = visible_blocks[-1].number
    return AuditPage(
        all_rows=rows,
        rows=[row for block in visible_blocks for row in block.rows],
        blocks=visible_blocks,
        filters=filters,
        total=len(rows),
        verified=sum(row.verified for row in rows),
        matching=len(matching),
        verification_token=verification.get_verification_token(matching),
        filter_counts=filters.counts(rows),
        last_block=last_block,
        has_more=any(block.number > last_block for block in blocks),
    )
