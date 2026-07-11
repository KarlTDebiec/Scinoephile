#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to pairwise review using LLMs.

Package hierarchy (modules may import from any above):
* prompt
* models
* manager
* processor
"""

from __future__ import annotations

from .manager import PairwiseReviewManager
from .models import (
    PairwiseReviewAnswer,
    PairwiseReviewQuery,
    PairwiseReviewTestCase,
)
from .processor import PairwiseReviewProcessor
from .prompt import PairwiseReviewPrompt

__all__ = [
    "PairwiseReviewAnswer",
    "PairwiseReviewManager",
    "PairwiseReviewProcessor",
    "PairwiseReviewPrompt",
    "PairwiseReviewQuery",
    "PairwiseReviewTestCase",
]
