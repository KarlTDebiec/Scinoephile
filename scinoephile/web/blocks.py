#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle block views and pagination shared by the local editors."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

__all__ = ["SubtitleBlock", "get_block_insertions", "get_block_page"]

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


def get_block_insertions[Row, Key](
    blocks: list[SubtitleBlock[Row]],
    loaded_rows: Mapping[Key, int],
    *,
    row_key: Callable[[Row], Key],
    row_id_prefix: str,
) -> tuple[list[tuple[SubtitleBlock[Row], str]], dict[int, list[tuple[Row, str]]]]:
    """Find ordered out-of-band insertions for newly matching blocks and rows.

    Arguments:
        blocks: matching blocks in the loaded page, in source order
        loaded_rows: keys of rows already displayed and their block numbers
        row_key: function that obtains the stable key from a row
        row_id_prefix: prefix for row element IDs
    Returns:
        new blocks and new rows in existing blocks, paired with their swap directives
    """
    added_blocks = []
    added_rows = {}
    loaded_numbers = set(loaded_rows.values())
    next_block = "#load-more"
    # Anchor insertions to existing elements, then emit them in source order
    for block in reversed(blocks):
        if block.number not in loaded_numbers:
            added_blocks.append((block, f"beforebegin:{next_block}"))
            continue
        next_block = f"#block-{block.number}"
        swap = f"beforeend:#block-rows-{block.number}"
        rows = []
        for row in reversed(block.rows):
            key = row_key(row)
            if key in loaded_rows:
                swap = f"beforebegin:#{row_id_prefix}{key}"
            else:
                rows.append((row, swap))
        if rows:
            added_rows[block.number] = list(reversed(rows))
    return list(reversed(added_blocks)), dict(reversed(added_rows.items()))


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
