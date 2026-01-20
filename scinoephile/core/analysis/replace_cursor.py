#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cursor for unequal replace processing."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["ReplaceCursor"]


@dataclass
class ReplaceCursor:
    """Tracks cursor state while processing unequal replace blocks.

    Arguments:
        one_blk: indices for the first block
        two_blk: indices for the second block
        i: current index within the first block
        j: current index within the second block
        last_was_split: whether the last action was a split
        should_return: whether the outer loop should return early
    """

    one_blk: list[int]
    two_blk: list[int]
    i: int = 0
    j: int = 0
    last_was_split: bool = False
    should_return: bool = False

    @property
    def one_idx(self) -> int:
        """Current index in the first block."""
        return self.one_blk[self.i]

    @property
    def two_idx(self) -> int:
        """Current index in the second block."""
        return self.two_blk[self.j]

    def advance(self, *, n_one: int, n_two: int, last_was_split: bool | None = None):
        """Advance cursor indices.

        Arguments:
            n_one: number of indices to advance in the first block
            n_two: number of indices to advance in the second block
            last_was_split: updated split state when provided
        """
        self.i += n_one
        self.j += n_two
        if last_was_split is not None:
            self.last_was_split = last_was_split

    def mark_return(self):
        """Mark the cursor for an early return."""
        self.should_return = True
