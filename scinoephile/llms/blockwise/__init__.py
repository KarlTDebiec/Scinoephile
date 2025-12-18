#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to blockwise subtitle review using LLMs.

Blockwise review takes in one series, processes it blockwise, and yields a single
revised series.
"""

from __future__ import annotations

from .answer import BlockwiseAnswer
from .prompt import BlockwisePrompt
from .query import BlockwiseQuery
from .reviewer import BlockwiseReviewer
from .test_case import BlockwiseTestCase

__all__ = [
    "BlockwiseAnswer",
    "BlockwisePrompt",
    "BlockwiseQuery",
    "BlockwiseReviewer",
    "BlockwiseTestCase",
]
