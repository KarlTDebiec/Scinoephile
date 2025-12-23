#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Block of subtitles within a Series."""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from .subtitle import Subtitle

if TYPE_CHECKING:
    from .series import Series

__all__ = ["Block"]


class Block:
    """Block of subtitles within a Series."""

    def __init__(self, series: Series, start_idx: int, end_idx: int):
        """Initialize."""
        self._series = series
        self.start_idx = start_idx
        self.end_idx = end_idx

    def __getitem__(self, idx: int) -> Subtitle:
        """Get block at index.

        Arguments:
            idx: index of subtitle to get
        Returns:
            Subtitle at index
        """
        if not isinstance(idx, int):
            raise TypeError(f"Index must be an int, not {type(idx).__name__}")
        if idx == 0:
            return self._series.events[self.start_idx]
        if idx < 0:
            idx += len(self)
            if idx < 0 or idx >= len(self):
                raise IndexError(
                    f"Index {idx} out of range for block of length {len(self)}"
                )
            return self._series.events[self.start_idx + idx]
        if idx >= len(self):
            raise IndexError(
                f"Index {idx} out of range for block of length {len(self)}"
            )
        return self._series.events[self.start_idx + idx]

    def __iter__(self) -> Iterator[Subtitle]:
        """Iterate over subtitles in the block.

        Returns:
            iterator over subtitles in the block
        """
        return iter(self._series.slice(self.start_idx, self.end_idx).events)

    def __len__(self) -> int:
        """Get number of subtitles in block.

        Returns:
            number of subtitles in block
        """
        return self.end_idx - self.start_idx

    def __repr__(self) -> str:
        """Get string representation."""
        return (
            f"{self.__class__.__name__}("
            f"series={self._series!r}, "
            f"start_idx={self.start_idx}, "
            f"end_idx={self.end_idx})"
        )

    @property
    def end(self) -> int:
        """End time of block."""
        return self._series[self.end_idx - 1].end

    @property
    def events(self) -> list[Subtitle]:
        """List of subtitles in the block."""
        return self._series.slice(self.start_idx, self.end_idx).events

    @property
    def start(self) -> int:
        """Start time of block."""
        return self._series[self.start_idx].start

    def to_series(self):
        """Convert block to a Series.

        Returns:
            Series containing the subtitles in the block
        """
        return self._series.slice(self.start_idx, self.end_idx)
