#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle block views and pagination shared by the local editors."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["SubtitleBlock", "get_block_page"]

_PAGE_SIZE = 5


@dataclass(frozen=True)
class SubtitleBlock[Row]:
    """A complete subtitle block and the rows matching the active filters."""

    number: int
    """Stable one-based block number."""
    first_index: int
    """First one-based subtitle position in the complete block."""
    last_index: int
    """Last one-based subtitle position in the complete block."""
    rows: list[Row]
    """Visible rows or their indexes in the source track."""
    start: int
    """Start time of the complete block in milliseconds."""
    end: int
    """End time of the complete block in milliseconds."""

    @property
    def count(self) -> int:
        """Total subtitle count before filtering."""
        return self.last_index - self.first_index + 1


def get_block_page[Row](
    blocks: list[SubtitleBlock[Row]],
    *,
    after: int = 0,
    through: int | None = None,
    append: bool = False,
) -> tuple[list[SubtitleBlock[Row]], int, bool]:
    """Select a batch or a loaded prefix using stable source block numbers.

    Arguments:
        blocks: matching blocks in source order
        after: last loaded block before a new batch
        through: inclusive cursor for an existing loaded prefix
        append: whether to return only the new batch after the cursor
    Returns:
        visible blocks, last loaded block number, and whether more matches follow
    """
    visible = [block for block in blocks if block.number > after][:_PAGE_SIZE]
    last_block = after
    if through is not None:
        last_block = through
    elif visible:
        last_block = visible[-1].number
    if through is not None or not append:
        visible = [block for block in blocks if block.number <= last_block]
    return visible, last_block, any(block.number > last_block for block in blocks)
