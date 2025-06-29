#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series of subtitles."""

from __future__ import annotations

from logging import info
from typing import Any

from pysubs2 import SSAFile

from scinoephile.common.validation import validate_input_file, validate_output_file
from scinoephile.core.block import Block
from scinoephile.core.blocks import get_block_indexes_by_pause
from scinoephile.core.subtitle import Subtitle


class Series(SSAFile):
    """Series of subtitles."""

    event_class = Subtitle
    """Class of individual subtitle events."""
    events: list[Subtitle]
    """Individual subtitle events."""

    def __init__(self):
        """Initialize."""
        super().__init__()

        self._blocks = None

    def __eq__(self, other: SSAFile) -> bool:
        """Whether this series is equal to another.

        Arguments:
            other: Series to which to compare
        Returns:
            Whether this series is equal to another
        """
        if len(self.events) != len(other.events):
            return False

        for self_event, other_event in zip(self.events, other.events):
            if self_event != other_event:
                return False

        return True

    def __ne__(self, other: SSAFile) -> bool:
        """Whether this series is not equal to another.

        Arguments:
            other: Series to which to compare
        Returns:
            Whether this series is not equal to another
        """
        return not self == other

    @property
    def blocks(self) -> list[Block]:
        """List of blocks in the series."""
        if self._blocks is None:
            self._init_blocks()
        return self._blocks

    @blocks.setter
    def blocks(self, blocks: list[Block]) -> None:
        """Set blocks of the series.

        Arguments:
            blocks: List of blocks in the series
        """
        self._blocks = blocks

    def save(self, path: str, format_: str | None = None, **kwargs: Any) -> None:
        """Save series to an output file.

        Arguments:
            path: Output file path
            format_: Output file format
            **kwargs: Additional keyword arguments
        """
        path = validate_output_file(path)
        SSAFile.save(self, path, format_=format_, **kwargs)
        info(f"Saved series to {path}")

    def slice(self, start: int, end: int) -> Series:
        """Slice series.

        Arguments:
            start: Start index
            end: End index
        Returns:
            Sliced series
        """
        sliced = type(self)()
        sliced.events = self.events[start:end]
        return sliced

    def to_simple_string(self, start: int | None = None, duration: int | None = None):
        """Convert series to a simple string representation.

        Arguments:
            start: Start time (default is the start of the first event)
            duration: Duration (default is the duration from the first to last event)
        Returns:
            String representation of series
        """
        if not self.events:
            return ""

        if start is None:
            start = self.events[0].start
        if duration is None:
            duration = self.events[-1].end - self.events[0].start

        string = ""
        for i, event in enumerate(self.events, 1):
            text = event.text.replace("\n", " ")
            string += (
                f"{i:2d} | "
                f"{round(100 * (event.start - start) / duration):3d}-"
                f"{round(100 * (event.end - start) / duration):<3d} | "
                f"{text}\n"
            )
        return string.rstrip()

    @classmethod
    def from_string(
        cls,
        string: str,
        format_: str | None = None,
        fps: float | None = None,
        **kwargs: Any,
    ) -> Series:
        """Parse series from string.

        Arguments:
            string: String to parse
            format_: Input file format
            fps: Frames per second
        Returns:
            Parsed series
        """
        series = super().from_string(string, format_=format_, fps=fps, **kwargs)
        events = []
        for ssaevent in series.events:
            events.append(cls.event_class(series=series, **ssaevent.as_dict()))
        series.events = events

        return series

    @classmethod
    def load(
        cls,
        path: str,
        encoding: str = "utf-8",
        format_: str | None = None,
        **kwargs: Any,
    ) -> Series:
        """Load series from an input file.

        Arguments:
            path : Input file path
            encoding: Input file encoding
            format_: Input file format
            **kwargs: Additional keyword arguments
        Returns:
            Loaded series
        """
        validated_path = validate_input_file(path)

        with open(validated_path, encoding=encoding) as fp:
            series = cls.from_file(fp, format_=format_, **kwargs)
            events = []
            for ssaevent in series.events:
                events.append(cls.event_class(series=series, **ssaevent.as_dict()))
            series.events = events

        info(f"Loaded series from {validated_path}")
        return series

    def _init_blocks(self) -> None:
        """Initialize blocks."""
        self._blocks = [
            Block(self, start_idx, end_idx)
            for start_idx, end_idx in get_block_indexes_by_pause(self)
        ]
