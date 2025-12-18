#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to dual track / single subtitle matters using LLMs."""

from __future__ import annotations

from .answer import DualSingleAnswer
from .prompt import DualSinglePrompt
from .query import DualSingleQuery
from .reviewer import DualSingleReviewer
from .test_case import DualSingleTestCase

__all__ = [
    "DualSingleAnswer",
    "DualSinglePrompt",
    "DualSingleQuery",
    "DualSingleReviewer",
    "DualSingleTestCase",
]
