#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Sampled video frame data."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = ["VideoFrameSample"]


@dataclass(frozen=True)
class VideoFrameSample:
    """Sampled video frame at a timestamp."""

    time: float
    """Timestamp of the sampled frame in seconds."""

    frame: np.ndarray
    """Normalized grayscale frame data."""
