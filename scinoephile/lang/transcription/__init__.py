#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code for transcribing audio using guide-language subtitles.

Package hierarchy (modules may import from any above):
* alignment
* aligner / block_aligner
* transcriber
* guided
"""

from __future__ import annotations

from .aligner import TranscriptionAligner
from .alignment import TranscriptionAlignment
from .block_aligner import BlockTranscriptionAligner
from .guided import GuidedTranscriptionSpec, TranscriptionLanguageSpec
from .transcriber import (
    BlockDelineationMode,
    BlockPunctuationMode,
    GuidedTranscriber,
    MlxAudioTimingMode,
    TranscriptionAlignmentMode,
    TranscriptionBackend,
)

__all__ = [
    "BlockDelineationMode",
    "BlockPunctuationMode",
    "BlockTranscriptionAligner",
    "GuidedTranscriber",
    "GuidedTranscriptionSpec",
    "MlxAudioTimingMode",
    "TranscriptionAligner",
    "TranscriptionAlignment",
    "TranscriptionAlignmentMode",
    "TranscriptionBackend",
    "TranscriptionLanguageSpec",
]
