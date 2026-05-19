#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Video metadata for offset detection."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

__all__ = ["VideoMetadata"]


@dataclass(frozen=True)
class VideoMetadata:
    """Video metadata needed for frame-grid offset detection."""

    duration: float
    """Video duration in seconds."""

    frame_rate: Fraction | None
    """Video frame rate, when needed and available."""
