#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcription alignment artifacts and lexical and timing evaluation.

Package hierarchy (modules may import from any above):
* alignment_sequence / artifact
* manifest / timing
* evaluation
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
from .evaluation import CharacterErrorMetrics, TranscriptionEvaluation
from .manifest import ProcessorIdentity, RunBlock, RunManifest
from .timing import TimingMetrics, TimingPair

__all__ = [
    "AlignmentArtifact",
    "AlignmentBlock",
    "AlignmentColumn",
    "AlignmentRow",
    "AlignmentSource",
    "AlignmentSubtitle",
    "CharacterErrorMetrics",
    "ProcessorIdentity",
    "RunBlock",
    "RunManifest",
    "TimingMetrics",
    "TimingPair",
    "TimingSettings",
    "TranscriptionEvaluation",
]
