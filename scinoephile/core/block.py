#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Block of subtitles within a Series."""

from __future__ import annotations

from collections.abc import Iterator
from functools import cached_property
from typing import TYPE_CHECKING

from scinoephile.core.subtitle import Subtitle

if TYPE_CHECKING:
    from scinoephile.core.series import Series


class Block:
    """Block of subtitles within a Series."""

    def __init__(self, series: Series, start_idx: int, end_idx: int) -> None:
        """Initialize."""
        self._series = series
        self.start_idx = start_idx
        self.end_idx = end_idx

    def __getitem__(self, idx: int) -> Series:
        """Get block at index.

        Arguments:
            idx: Index of subtitle to get
        Returns:
            Subtitle at index
        """
        if not isinstance(idx, int):
            raise TypeError(f"Index must be an int, not {type(idx).__name__}")
        if not self.start_idx <= idx <= self.end_idx:
            raise IndexError(
                f"Index {idx} out of range for block {self.start_idx}-{self.end_idx}"
            )
        return self._series.events[idx - 1]

    def __iter__(self) -> Iterator[Subtitle]:
        """Iterate over subtitles in the block.

        Returns:
            Iterator over subtitles in the block
        """
        return iter(self._series.slice(self.start_idx - 1, self.end_idx).events)

    def __len__(self) -> int:
        """Get number of subtitles in block.

        Returns:
            Number of subtitles in block
        """
        return self.end_idx - self.start_idx + 1

    def __repr__(self) -> str:
        """Get string representation."""
        return (
            f"{self.__class__.__name__}("
            f"start_idx={self.start_idx}, "
            f"end_idx={self.end_idx}, "
            f"start={self.start}, "
            f"end={self.end})"
        )

    @cached_property
    def end(self) -> int:
        """End time of block."""
        return self._series.events[self.end_idx - 1].end

    @cached_property
    def events(self) -> list[Subtitle]:
        """List of subtitles in the block."""
        return self._series.slice(self.start_idx - 1, self.end_idx).events

    @cached_property
    def start(self) -> int:
        """Start time of block."""
        return self._series.events[self.start_idx - 1].start
