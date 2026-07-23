#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Overall video offset result."""

from __future__ import annotations

from dataclasses import dataclass

from .video_offset_aggregate import VideoOffsetAggregate
from .video_offset_candidate import VideoOffsetCandidate
from .video_offset_window_result import VideoOffsetWindowResult

__all__ = ["VideoOffsetResult"]


@dataclass(frozen=True)
class VideoOffsetResult:
    """Best visual offset estimate between two videos."""

    offset: float
    """Estimated target timestamp minus reference timestamp in seconds."""

    confidence: str
    """Confidence label for the estimate."""

    best: VideoOffsetCandidate
    """Best-scoring candidate offset."""

    second_best: VideoOffsetCandidate | None
    """Second-best candidate offset, if available."""

    offset_frames: int
    """Estimated target timestamp minus reference timestamp in reference frames."""

    windows: tuple[VideoOffsetWindowResult, ...] = ()
    """Per-window results when multiple windows were sampled."""

    aggregate: VideoOffsetAggregate | None = None
    """Aggregate result when multiple windows were sampled."""
