#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to dual block gapped matters using LLMs.

Dual block gapped matters take in two subtitle Series with 1:1 pairing of subtitles,
where some subtitles are missing from the primary series. They process the paired
blocks and output a single completed Series.
"""

from __future__ import annotations

from .answer import DualBlockGappedAnswer
from .processor import DualBlockGappedProcessor
from .prompt import DualBlockGappedPrompt
from .query import DualBlockGappedQuery
from .test_case import DualBlockGappedTestCase

__all__ = [
    "DualBlockGappedAnswer",
    "DualBlockGappedProcessor",
    "DualBlockGappedPrompt",
    "DualBlockGappedQuery",
    "DualBlockGappedTestCase",
]
