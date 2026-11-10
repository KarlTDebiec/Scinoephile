#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Paginate audit rows and prepare them for the browser workspace."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import groupby
from operator import attrgetter
from urllib.parse import urlencode

from scinoephile.analysis.alignment import pairwise
from scinoephile.core.dependencies.web import import_flask
from scinoephile.core.timing import format_time_ms
from scinoephile.operations.review_audit.filters import AuditFilters
from scinoephile.operations.review_audit.project import ReviewAuditProject
from scinoephile.operations.review_audit.rows import AuditRow
from scinoephile.operations.review_audit.verification import (
    VerificationSelection,
    get_verification_selection,
)

__all__ = [
    "AuditBlock",
    "AuditPage",
    "get_audit_page",
    "get_row_differences",
    "get_row_time_label",
    "get_view_context",
]

_PAGE_SIZE = 5
"""Maximum number of complete matching blocks in a new batch."""


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
        start = format_time_ms(self.start)
        end = format_time_ms(self.end)
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
    verification: dict[str, VerificationSelection]
    """Complete visible verification candidates for each operation."""
    filter_counts: dict[str, dict[str, int]]
    """Dependent option counts before pagination."""
    last_block: int
    """Stable source block cursor through which rows have loaded."""
    has_more: bool
    """Whether more matching blocks follow the loaded cursor."""


def get_audit_page(
    rows: list[AuditRow],
    filters: AuditFilters,
    *,
    after: int = 0,
    through: int | None = None,
    append: bool = True,
) -> AuditPage:
    """Build a block batch or an already loaded prefix from one row snapshot.

    Arguments:
        rows: complete snapshot in source order
        filters: requested filters
        after: stable source block cursor before a new batch
        through: inclusive cursor for an already loaded prefix, or None for a batch
        append: whether to return only new blocks after the cursor
    Returns:
        loaded blocks and complete filtered progress counts
    """
    filters.validate()
    matching = []
    blocks = []
    for number, group in groupby(rows, key=attrgetter("block_number")):
        block_rows = list(group)
        visible = [row for row in block_rows if filters.matches(row)]
        if not visible:
            continue
        matching.extend(visible)
        blocks.append(
            AuditBlock(
                number=number,
                first_index=block_rows[0].index,
                last_index=block_rows[-1].index,
                rows=visible,
                start=block_rows[0].start,
                end=max(row.end for row in block_rows),
            )
        )
    visible_blocks = [block for block in blocks if block.number > after][:_PAGE_SIZE]
    last_block = after
    if through is not None:
        visible_blocks = [block for block in blocks if block.number <= through]
        last_block = through
    elif visible_blocks:
        last_block = visible_blocks[-1].number
    if not append:
        visible_blocks = [block for block in blocks if block.number <= last_block]
    verification = {
        operation: get_verification_selection(
            rows, filters, through=last_block, proofreading=proofreading
        )
        for operation, proofreading in (("proofreading", True), ("audit", False))
    }
    return AuditPage(
        all_rows=rows,
        rows=[row for block in visible_blocks for row in block.rows],
        blocks=visible_blocks,
        filters=filters,
        total=len(rows),
        verified=sum(row.verified for row in rows),
        matching=len(matching),
        verification=verification,
        filter_counts=filters.counts(rows),
        last_block=last_block,
        has_more=any(block.number > last_block for block in blocks),
    )


def get_row_differences(
    row: AuditRow,
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Calculate the text spans rendered in a subtitle diff.

    Arguments:
        row: original and proofread subtitle texts
    Returns:
        original and proofread spans with their alignment operations
    """
    if row.original == row.reviewed:
        return [(row.original, "match")], [(row.reviewed, "match")]
    original: list[tuple[str, str]] = []
    reviewed: list[tuple[str, str]] = []
    for column in pairwise.Alignment(row.original, row.reviewed).columns:
        kind = column.operation.name.lower()
        for character, spans in ((column.one, original), (column.two, reviewed)):
            if character is None:
                continue
            if spans and spans[-1][1] == kind:
                spans[-1] = (spans[-1][0] + character, kind)
            else:
                spans.append((character, kind))
    return original, reviewed


def get_row_time_label(row: AuditRow) -> str:
    """Format the start and end of a subtitle for the workspace.

    Arguments:
        row: subtitle row with millisecond timestamps
    Returns:
        subtitle range including milliseconds
    """
    start = format_time_ms(row.start, include_milliseconds=True)
    end = format_time_ms(row.end, include_milliseconds=True)
    return f"{start} – {end}"


def get_view_context(
    audit: ReviewAuditProject,
    filters: AuditFilters,
    *,
    page: AuditPage | None = None,
    append: bool = False,
) -> dict[str, object]:
    """Build a bounded view, stable next cursor, and native save context.

    Arguments:
        audit: open review audit project
        filters: requested filter state
        page: existing page snapshot when rendering a save response
        append: whether to render only new blocks for an incremental load
    Returns:
        template context
    """
    flask = import_flask()
    if page is None:
        through = None
        if flask.request.args.get("through"):
            through = max(0, int(flask.request.args["through"]))
        after = max(0, int(flask.request.args.get("after", "0")))
        page = get_audit_page(
            audit.rows(), filters, after=after, through=through, append=append
        )
    values = asdict(page.filters)
    has_output = audit.outfile_path.exists()
    return {
        "has_output": has_output,
        "editing_blocked": not has_output or audit.job_running,
        "input_changed": audit.input_changed,
        "page": page,
        "filters": page.filters,
        "query": urlencode(dict(values, through=page.last_block)),
        "next_url": f"/?{urlencode(dict(values, after=page.last_block))}",
    }
