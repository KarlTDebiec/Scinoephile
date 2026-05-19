#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Video offset result for one sampled window."""

from __future__ import annotations

from dataclasses import dataclass

from .video_offset_candidate import VideoOffsetCandidate

__all__ = ["VideoOffsetWindowResult"]


@dataclass(frozen=True)
class VideoOffsetWindowResult:
    """Visual offset estimate for one sampled window."""

    start_time: float
    """Window start time in seconds."""

    offset: float
    """Estimated target timestamp minus reference timestamp in seconds."""

    confidence: str
    """Confidence label for the estimate."""

    best: VideoOffsetCandidate
    """Best-scoring candidate offset."""

    second_best: VideoOffsetCandidate | None
    """Second-best candidate offset, if available."""

    offset_frames: int
    """Target timestamp minus reference timestamp in reference frames."""
