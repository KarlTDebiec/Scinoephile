#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Candidate video offset score."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["VideoOffsetCandidate"]


@dataclass(frozen=True)
class VideoOffsetCandidate:
    """Score for one candidate video offset."""

    offset: float
    """Target timestamp minus reference timestamp in seconds."""

    matched_count: int
    """Number of reference samples matched against target samples."""

    score: float
    """Aggregate frame difference score; lower values are better."""

    offset_frames: int | None = None
    """Target timestamp minus reference timestamp in reference frames."""
