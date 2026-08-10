#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cantonese transcription prompts and validation.

Package hierarchy (modules may import from any above):
* prompts / validation
"""

from __future__ import annotations

from .prompts import YueTranscriptionPromptYueHans, YueTranscriptionPromptYueHant
from .validation import CantoneseTranscriptionAlignmentScorer

__all__ = [
    "CantoneseTranscriptionAlignmentScorer",
    "YueTranscriptionPromptYueHans",
    "YueTranscriptionPromptYueHant",
]
