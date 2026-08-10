#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reference-free merging of column-aligned ASR evidence.

Package hierarchy (modules may import from any above):
* prompt / validation
* models
* manager
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

__all__ = [
    "AlignedTranscriptionMergeAnswer",
    "AlignedTranscriptionMergeManager",
    "AlignedTranscriptionMergeProcessor",
    "AlignedTranscriptionMergePrompt",
    "AlignedTranscriptionMergeQuery",
    "AlignedTranscriptionMergeSource",
    "AlignedTranscriptionMergeSubtitle",
    "AlignedTranscriptionMergeTestCase",
]
