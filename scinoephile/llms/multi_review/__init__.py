#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to reviewing multiple subtitle sources using an LLM.

Package hierarchy (modules may import from any above):
* prompt
* models
* manager
* processor
"""

from __future__ import annotations

from .manager import MultiReviewManager
from .models import (
    MultiReviewAnswer,
    MultiReviewQuery,
    MultiReviewSource,
    MultiReviewSubtitle,
    MultiReviewTestCase,
)
from .processor import MultiReviewProcessor
from .prompt import MultiReviewPrompt

__all__ = [
    "MultiReviewAnswer",
    "MultiReviewManager",
    "MultiReviewProcessor",
    "MultiReviewPrompt",
    "MultiReviewQuery",
    "MultiReviewSource",
    "MultiReviewSubtitle",
    "MultiReviewTestCase",
]
