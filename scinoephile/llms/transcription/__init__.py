#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reference-free transcription from column-aligned ASR evidence.

Package hierarchy (modules may import from any above):
* prompt / validation
* models
* manager
* processor
"""

from __future__ import annotations

from .manager import TranscriptionManager
from .models import (
    TranscriptionAnswer,
    TranscriptionQuery,
    TranscriptionSource,
    TranscriptionSubtitle,
    TranscriptionTestCase,
)
from .processor import TranscriptionProcessor, TranscriptionRequestResult
from .prompt import TranscriptionPrompt
from .validation import (
    TranscriptionAlignmentScorer,
    TranscriptionCharacterRelationship,
    TranscriptionValidation,
)

__all__ = [
    "TranscriptionAlignmentScorer",
    "TranscriptionAnswer",
    "TranscriptionCharacterRelationship",
    "TranscriptionManager",
    "TranscriptionProcessor",
    "TranscriptionPrompt",
    "TranscriptionQuery",
    "TranscriptionRequestResult",
    "TranscriptionSource",
    "TranscriptionSubtitle",
    "TranscriptionTestCase",
    "TranscriptionValidation",
]
