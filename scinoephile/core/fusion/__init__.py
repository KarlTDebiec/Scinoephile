#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to subtitle fusion using LLMs.

Fusion takes two series with 1:1 correspondence, processes them pairwise, and yields a
single revised series.
"""

from __future__ import annotations

from .answer import FusionAnswer
from .fuser import Fuser
from .prompt import FusionPrompt
from .query import FusionQuery
from .test_case import FusionTestCase

__all__ = [
    "Fuser",
    "FusionAnswer",
    "FusionPrompt",
    "FusionQuery",
    "FusionTestCase",
]
