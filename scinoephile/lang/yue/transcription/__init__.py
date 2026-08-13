#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Yue transcription prompts and validation.

Package hierarchy (modules may import from any above):
* prompts / timed_token_similarity / validation
"""

from __future__ import annotations

from .prompts import YueTranscriptionPromptYueHans, YueTranscriptionPromptYueHant
from .timed_token_similarity import YueTimedTokenSimilarity
from .validation import YueTranscriptionAlignmentScorer

__all__ = [
    "YueTranscriptionAlignmentScorer",
    "YueTranscriptionPromptYueHans",
    "YueTranscriptionPromptYueHant",
    "YueTimedTokenSimilarity",
]
