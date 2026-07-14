#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code for transcribing audio using reference-language subtitles.

Package hierarchy (modules may import from any above):
* alignment
* aligner
* processor
* guided
"""

from __future__ import annotations

from .aligner import TranscriptionAligner
from .alignment import TranscriptionAlignment
from .guided import GuidedTranscriptionSpec, TranscriptionLanguageSpec
from .processor import DemucsMode, GuidedTranscriptionProcessor, VADMode

__all__ = [
    "DemucsMode",
    "GuidedTranscriptionProcessor",
    "GuidedTranscriptionSpec",
    "TranscriptionAligner",
    "TranscriptionAlignment",
    "TranscriptionLanguageSpec",
    "VADMode",
]
