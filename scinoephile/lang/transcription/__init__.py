#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Guided and reference-free audio transcription.

Package hierarchy (modules may import from any above):
* alignment / multisource_alignment / standard
* aligner
* transcriber
* guided
"""

from __future__ import annotations

from .aligner import TranscriptionAligner
from .alignment import TranscriptionAlignment
from .guided import GuidedTranscriptionSpec, TranscriptionLanguageSpec
from .transcriber import GuidedTranscriber, MlxAudioTimingMode, TranscriptionModel

__all__ = [
    "GuidedTranscriber",
    "GuidedTranscriptionSpec",
    "MlxAudioTimingMode",
    "TranscriptionAligner",
    "TranscriptionAlignment",
    "TranscriptionLanguageSpec",
    "TranscriptionModel",
]
