#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcription artifacts and timing evaluation.

Package hierarchy (modules may import from any above):
* artifact / sequence
* timing
"""

from __future__ import annotations

from .artifact import (
    AlignmentArtifact,
    AlignmentBlock,
    AlignmentColumn,
    AlignmentRow,
    AlignmentSource,
    AlignmentSubtitle,
    TimingSettings,
)
from .timing import TimingMetrics, TimingPair

__all__ = [
    "AlignmentArtifact",
    "AlignmentBlock",
    "AlignmentColumn",
    "AlignmentRow",
    "AlignmentSource",
    "AlignmentSubtitle",
    "TimingMetrics",
    "TimingPair",
    "TimingSettings",
]
