#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Models for timestamped multiple-sequence alignment."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median

__all__ = ["Alignment", "Column", "Sequence", "Token"]


@dataclass(frozen=True, slots=True)
class Token:
    """One display token with a source-local time interval."""

    text: str
    """Original source text represented by this token."""
    start_seconds: float
    """Inclusive token start relative to the aligned audio."""
    end_seconds: float
    """Exclusive token end relative to the aligned audio."""

    def __post_init__(self):
        """Validate token text and timing."""
        if len(self.text) != 1:
            raise ValueError("Timed alignment tokens must contain one character.")
        if self.start_seconds < 0.0:
            raise ValueError("Timed alignment token start must be non-negative.")
        if self.end_seconds < self.start_seconds:
            raise ValueError("Timed alignment token end must not precede its start.")


@dataclass(frozen=True, slots=True)
class Sequence:
    """Named ordered sequence of timestamped characters."""

    name: str
    """Stable source name."""
    tokens: tuple[Token, ...]
    """Timestamped source characters in transcription order."""

    def __post_init__(self):
        """Validate the source name and chronological token order."""
        if not self.name.strip():
            raise ValueError("Timed alignment sequence name must be nonblank.")
        previous_start = -1.0
        for token in self.tokens:
            if token.start_seconds < previous_start:
                raise ValueError(
                    "Timed alignment tokens must be chronologically ordered."
                )
            previous_start = token.start_seconds


@dataclass(frozen=True, slots=True)
class Column:
    """One multiple-alignment column containing source tokens or gaps."""

    tokens: tuple[Token | None, ...]
    """Source-ordered token cells; None represents an alignment gap."""
    pause_interval_seconds: tuple[float, float] | None = None
    """Explicit local interval for a shared timed-pause column."""
    marker: str | None = None
    """Character displayed across every row for a timed annotation column."""
    marker_time_seconds: float | None = None
    """Local source time of a shared annotation marker."""

    def __post_init__(self):
        """Validate token cells and optional annotation timing."""
        if not self.tokens:
            raise ValueError("Timed alignment columns must contain source cells.")
        contains_token = any(token is not None for token in self.tokens)
        if contains_token and (
            self.pause_interval_seconds is not None or self.marker is not None
        ):
            raise ValueError("Lexical alignment columns cannot be annotations.")
        if self.pause_interval_seconds is not None and self.marker is not None:
            raise ValueError("Alignment columns cannot be both pauses and markers.")
        if (
            not contains_token
            and self.pause_interval_seconds is None
            and self.marker is None
        ):
            raise ValueError("Shared alignment gaps require a timed annotation.")
        if self.pause_interval_seconds is not None:
            start_seconds, end_seconds = self.pause_interval_seconds
            if start_seconds < 0.0:
                raise ValueError("Timed alignment pause start must be non-negative.")
            if end_seconds <= start_seconds:
                raise ValueError("Timed alignment pause duration must be positive.")
        if self.marker is None and self.marker_time_seconds is not None:
            raise ValueError("Alignment marker timing requires a marker character.")
        if self.marker is not None:
            if len(self.marker) != 1:
                raise ValueError("Alignment markers must contain one character.")
            if self.marker_time_seconds is None or self.marker_time_seconds < 0.0:
                raise ValueError("Alignment markers require non-negative timing.")

    @property
    def end_seconds(self) -> float:
        """Get the robust column end time."""
        if self.pause_interval_seconds is not None:
            return self.pause_interval_seconds[1]
        if self.marker_time_seconds is not None:
            return self.marker_time_seconds
        ends = [token.end_seconds for token in self.tokens if token is not None]
        return float(median(ends))

    @property
    def is_marker(self) -> bool:
        """Whether this is a shared timed-marker column."""
        return self.marker is not None

    @property
    def is_pause(self) -> bool:
        """Whether this is a shared timed-pause column."""
        return self.pause_interval_seconds is not None

    @property
    def start_seconds(self) -> float:
        """Get the robust column start time."""
        if self.pause_interval_seconds is not None:
            return self.pause_interval_seconds[0]
        if self.marker_time_seconds is not None:
            return self.marker_time_seconds
        starts = [token.start_seconds for token in self.tokens if token is not None]
        return float(median(starts))


@dataclass(frozen=True, slots=True)
class Alignment:
    """Multiple alignment of named timestamped character sequences."""

    source_names: tuple[str, ...]
    """Source names in row order."""
    columns: tuple[Column, ...]
    """Alignment columns in reading order."""

    def __post_init__(self):
        """Validate row names and column widths."""
        if not self.source_names:
            raise ValueError("Timed alignment requires at least one source.")
        if len(set(self.source_names)) != len(self.source_names):
            raise ValueError("Multiple alignment source names must be unique.")
        if any(len(column.tokens) != len(self.source_names) for column in self.columns):
            raise ValueError(
                "Multiple alignment column width does not match its sources."
            )

    def get_sequence_text(self, source_name: str) -> str:
        """Reconstruct one ungapped source sequence.

        Arguments:
            source_name: source row to reconstruct
        Returns:
            original source characters without alignment gaps
        """
        source_idx = self.source_names.index(source_name)
        return "".join(
            token.text
            for column in self.columns
            if (token := column.tokens[source_idx]) is not None
        )
