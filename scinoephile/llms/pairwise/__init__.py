#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to pairwise subtitle review using LLMs.

Pairwise review takes two series with 1:1 correspondence, processes them pairwise, and
yields a single revised series.
"""

from __future__ import annotations

from .answer import PairwiseAnswer
from .prompt import PairwisePrompt
from .query import PairwiseQuery
from .reviewer import PairwiseReviewer
from .test_case import PairwiseTestCase

__all__ = [
    "PairwiseAnswer",
    "PairwisePrompt",
    "PairwiseQuery",
    "PairwiseReviewer",
    "PairwiseTestCase",
]
