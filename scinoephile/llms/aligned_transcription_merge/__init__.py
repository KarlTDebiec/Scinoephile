#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reference-free merging of column-aligned ASR evidence.

Package hierarchy (modules may import from any above):
* prompt / validation
* models
* manager
* splitting
* processor
"""

from __future__ import annotations

from .manager import AlignedTranscriptionMergeManager
from .models import (
    AlignedTranscriptionMergeAnswer,
    AlignedTranscriptionMergeQuery,
    AlignedTranscriptionMergeSource,
    AlignedTranscriptionMergeSubtitle,
    AlignedTranscriptionMergeTestCase,
)
from .processor import AlignedTranscriptionMergeProcessor
from .prompt import AlignedTranscriptionMergePrompt
from .validation import (
    AlignedTranscriptionMergeCharacterSupport,
    AlignedTranscriptionMergeValidation,
    get_aligned_transcription_merge_support_row,
    get_aligned_transcription_merge_validation,
)

__all__ = [
    "AlignedTranscriptionMergeAnswer",
    "AlignedTranscriptionMergeCharacterSupport",
    "AlignedTranscriptionMergeManager",
    "AlignedTranscriptionMergeProcessor",
    "AlignedTranscriptionMergePrompt",
    "AlignedTranscriptionMergeQuery",
    "AlignedTranscriptionMergeSource",
    "AlignedTranscriptionMergeSubtitle",
    "AlignedTranscriptionMergeTestCase",
    "AlignedTranscriptionMergeValidation",
    "get_aligned_transcription_merge_support_row",
    "get_aligned_transcription_merge_validation",
]
