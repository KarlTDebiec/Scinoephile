#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcription alignment artifacts, reference adapters, and timing evaluation.

Package hierarchy (modules may import from any above):
* alignment_sequence / artifact
* manifest / timing
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
from .manifest import ProcessorIdentity, RunBlock, RunManifest
from .timing import TimingMetrics, TimingPair

__all__ = [
    "AlignmentArtifact",
    "AlignmentBlock",
    "AlignmentColumn",
    "AlignmentRow",
    "AlignmentSource",
    "AlignmentSubtitle",
    "ProcessorIdentity",
    "RunBlock",
    "RunManifest",
    "TimingMetrics",
    "TimingPair",
    "TimingSettings",
]
