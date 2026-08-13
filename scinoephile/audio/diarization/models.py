#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Typed speaker diarization results."""

from __future__ import annotations

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field, model_validator

__all__ = ["DiarizationMode", "SpeakerDiarizationResult", "SpeakerTurn"]


class DiarizationMode(StrEnum):
    """Speaker diarization behavior."""

    AUTO = "auto"
    """Use diarization when available and continue without it after failure."""
    ON = "on"
    """Require successful speaker diarization."""
    OFF = "off"
    """Do not run speaker diarization."""


class SpeakerTurn(BaseModel):
    """One source-timeline interval assigned to an anonymous speaker."""

    start: float = Field(ge=0.0)
    """Turn start time relative to the complete source audio, in seconds."""
    end: float = Field(gt=0.0)
    """Turn end time relative to the complete source audio, in seconds."""
    speaker: str = Field(min_length=1)
    """Anonymous source-wide speaker label."""

    @model_validator(mode="after")
    def _validate_duration(self) -> Self:
        """Ensure the turn has positive duration."""
        if self.end <= self.start:
            raise ValueError("Speaker turn end must be after its start.")
        return self


class SpeakerDiarizationResult(BaseModel):
    """Regular and exclusive source-timeline speaker turns."""

    turns: list[SpeakerTurn]
    """Regular overlap-preserving speaker diarization turns."""
    exclusive_turns: list[SpeakerTurn]
    """Non-overlapping turns intended for downstream interval lookup."""

    def get_exclusive_speaker(self, start: float, end: float) -> str | None:
        """Get the exclusive speaker with greatest overlap with an interval.

        Arguments:
            start: interval start relative to the complete source, in seconds
            end: interval end relative to the complete source, in seconds
        Returns:
            anonymous speaker label, or None when the interval contains no speech
        Raises:
            ValueError: if the interval is invalid
        """
        if start < 0.0 or end < start:
            raise ValueError("Speaker-assignment interval is invalid.")
        interval_end = end
        if interval_end == start:
            interval_end = start + 1e-9

        best_turn = None
        best_overlap = 0.0
        midpoint = (start + interval_end) / 2
        for turn in self.exclusive_turns:
            if turn.start >= interval_end:
                break
            overlap = min(interval_end, turn.end) - max(start, turn.start)
            if overlap <= 0.0:
                continue
            if overlap > best_overlap:
                best_turn = turn
                best_overlap = overlap
                continue
            if overlap == best_overlap and best_turn is not None:
                current_contains_midpoint = turn.start <= midpoint < turn.end
                best_contains_midpoint = best_turn.start <= midpoint < best_turn.end
                if current_contains_midpoint and not best_contains_midpoint:
                    best_turn = turn
        if best_turn is None:
            return None
        return best_turn.speaker

    @model_validator(mode="after")
    def _validate_turn_order(self) -> Self:
        """Ensure timelines are ordered and exclusive turns do not overlap."""
        for name, turns in (
            ("regular", self.turns),
            ("exclusive", self.exclusive_turns),
        ):
            if turns != sorted(
                turns, key=lambda turn: (turn.start, turn.end, turn.speaker)
            ):
                raise ValueError(f"{name.title()} speaker turns must be ordered.")
        for previous, current in zip(
            self.exclusive_turns, self.exclusive_turns[1:], strict=False
        ):
            if current.start < previous.end:
                raise ValueError("Exclusive speaker turns must not overlap.")
        return self
