#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Aggregate video offset result."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["VideoOffsetAggregate"]


@dataclass(frozen=True)
class VideoOffsetAggregate:
    """Aggregate result across multiple sampled windows."""

    offset: float
    """Aggregate target timestamp minus reference timestamp in seconds."""

    offset_frames: int
    """Aggregate target timestamp minus reference timestamp in reference frames."""

    mean_frames: float
    """Mean window offset in reference frames."""

    median_frames: int
    """Median window offset in reference frames."""

    stdev_frames: float
    """Population standard deviation of window offsets in reference frames."""

    min_frames: int
    """Minimum window offset in reference frames."""

    max_frames: int
    """Maximum window offset in reference frames."""

    agreeing_count: int
    """Number of windows that agree with the aggregate frame offset."""

    total_count: int
    """Number of valid windows in the aggregate."""
