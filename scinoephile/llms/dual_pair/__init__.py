#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to dual pair matters using LLMs."""

from __future__ import annotations

from .answer import DualPairAnswer
from .prompt import DualPairPrompt
from .query import DualPairQuery
from .test_case import DualPairTestCase

__all__ = [
    "DualPairAnswer",
    "DualPairPrompt",
    "DualPairQuery",
    "DualPairTestCase",
]
