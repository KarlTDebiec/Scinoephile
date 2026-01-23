#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series of subtitles."""

from __future__ import annotations

from logging import info
from pathlib import Path
from typing import Any, Self, cast, override

from pysubs2 import SSAFile
from pysubs2.time import ms_to_str

from scinoephile.common.validation import val_input_path, val_output_path

from .block import Block
from .subtitle import Subtitle

__all__ = ["Series"]


class Series(SSAFile):
    """Series of subtitles."""

    event_class = Subtitle
    """Class of individual subtitle events."""
    events: list[Subtitle]
    """Individual subtitle events."""

    @override
    def __init__(self, events: list[Subtitle] | None = None):
        """Initialize.

        Arguments:
            events: individual subtitle events
        """
        super().__init__()

        if events is not None:
            self.events = events
        self._blocks: list[Block] | None = None

    def __eq__(self, other: object) -> bool:
        """Whether this series is equal to another.

        Arguments:
            other: Series to which to compare
        Returns:
            whether this series is equal to another
        """
        if not isinstance(other, SSAFile):
            return NotImplemented

        if len(self) != len(other):
            return False

        for self_event, other_event in zip(self, other):
            if self_event.start != other_event.start:
                return False
            if self_event.end != other_event.end:
                return False
            if self_event.text.replace("\n", "\\N") != other_event.text.replace(
                "\n", "\\N"
            ):
                return False

        return True

    def __ne__(self, other: object) -> bool:
        """Whether this series is not equal to another.

        Arguments:
            other: Series to which to compare
        Returns:
            whether this series is not equal to another
        """
        return not self == other

    __hash__ = None

    @override
    def __repr__(self) -> str:
        """Representation."""
        if self.events:
            max_time = max(ev.end for ev in self)
            return (
                f"<{self.__class__.__name__} with {len(self)} events and "
                f"{len(self.styles)} styles, last timestamp {ms_to_str(max_time)}>"
            )
        return (
            f"<{self.__class__.__name__} with 0 events and {len(self.styles)} styles>"
        )

    @property
    def blocks(self) -> list[Block]:
        """List of blocks in the series."""
        if self._blocks is None:
            self._init_blocks()
        assert self._blocks is not None
        return self._blocks

    @blocks.setter
    def blocks(self, blocks: list[Block]):
        """Set blocks of the series.

        Arguments:
            blocks: List of blocks in the series
        """
        self._blocks = blocks

    @override
    def save(
        self,
        path: Path | str,
        encoding: str = "utf-8",
        format_: str | None = None,
        fps: float | None = None,
        errors: str | None = None,
        **kwargs: Any,
    ):
        """Save series to an output file.

        Arguments:
            path: output file path
            encoding: output file encoding
            format_: output file format
            fps: frames per second
            errors: encoding error handling
            **kwargs: additional keyword arguments
        """
        path = val_output_path(path, exist_ok=True)
        SSAFile.save(
            self,
            str(path),
            encoding=encoding,
            format_=format_,
            fps=fps,
            errors=errors,
            **kwargs,
        )
        info(f"Saved series to {path}")

    def slice(self, start: int, end: int) -> Self:
        """Slice series.

        Arguments:
            start: start index
            end: end index
        Returns:
            sliced series
        """
        sliced = type(self)()
        sliced.events = [
            self.event_class(series=sliced, **event.as_dict())
            for event in self[start:end]
        ]
        return sliced

    def to_simple_string(self, start: int | None = None, duration: int | None = None):
        """Convert series to a simple string representation.

        Arguments:
            start: start time (default is the start of the first event)
            duration: duration (default is the duration from the first to last event)
        Returns:
            string representation of series
        """
        if not self.events:
            return ""

        if start is None:
            start = self[0].start
        if duration is None:
            duration = self[-1].end - self[0].start

        string = ""
        for i, event in enumerate(self, 1):
            text = event.text_with_newline.replace("\n", " ")
            string += (
                f"{i:2d} | "
                f"{round(100 * (event.start - start) / duration):3d}-"
                f"{round(100 * (event.end - start) / duration):<3d} | "
                f"{text}\n"
            )
        return string.rstrip()

    @classmethod
    @override
    def from_string(
        cls,
        string: str,
        format_: str | None = None,
        fps: float | None = None,
        **kwargs: Any,
    ) -> Self:
        """Parse series from string.

        Arguments:
            string: string to parse
            format_: input file format
            fps: frames per second
            **kwargs: additional keyword arguments
        Returns:
            parsed series
        """
        series = cast(
            Self,
            super().from_string(string, format_=format_, fps=fps, **kwargs),
        )
        series.events = [
            cls.event_class(series=series, **ssaevent.as_dict()) for ssaevent in series
        ]

        return series

    @classmethod
    @override
    def load(
        cls,
        path: Path | str,
        encoding: str = "utf-8",
        format_: str | None = None,
        fps: float | None = None,
        errors: str | None = None,
        **kwargs: Any,
    ) -> Self:
        """Load series from an input file.

        Arguments:
            path : input file path
            encoding: input file encoding
            format_: input file format
            fps: frames per second
            errors: encoding error handling
            **kwargs: additional keyword arguments
        Returns:
            loaded series
        """
        validated_path = val_input_path(path)

        with open(str(validated_path), encoding=encoding, errors=errors) as input_file:
            series = cast(
                Self,
                cls.from_file(input_file, format_=format_, fps=fps, **kwargs),
            )
            series.events = [
                cls.event_class(series=series, **ssaevent.as_dict())
                for ssaevent in series
            ]

        info(f"Loaded series from {validated_path}")
        return series

    def _init_blocks(self):
        """Initialize blocks."""
        self._blocks = [
            Block(self, start_idx, end_idx)
            for start_idx, end_idx in self.get_block_indexes_by_pause(self)
        ]

    @staticmethod
    def get_block_indexes_by_pause(
        series: Series, pause_length: int = 3000
    ) -> list[tuple[int, int]]:
        """Get indexes of blocks in a Series split by pauses without text.

        Arguments:
            series: Series to split into blocks
            pause_length: split whenever a pause of this length is encountered
        Returns:
            start and end indexes of each block
        """
        if not series.events:
            return []
        block_indexes = []
        start = 0
        prev_end = None

        for i, event in enumerate(series):
            if prev_end is not None and event.start - prev_end >= pause_length:
                block_indexes.append((start, i))
                start = i
            prev_end = event.end
        block_indexes.append((start, len(series)))

        return block_indexes
