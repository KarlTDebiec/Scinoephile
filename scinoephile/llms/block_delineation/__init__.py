#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Block-level subtitle delineation using sparse LLM changes.

Package hierarchy (modules may import from any above):
* prompt
* models
* manager
* processor
"""

from __future__ import annotations

from .manager import BlockDelineationManager
from .models import (
    BlockDelineationAnswer,
    BlockDelineationBoundaryChange,
    BlockDelineationQuery,
    BlockDelineationSubtitle,
    BlockDelineationTestCase,
)
from .processor import BlockDelineationProcessor
from .prompt import BlockDelineationPrompt

__all__ = [
    "BlockDelineationAnswer",
    "BlockDelineationBoundaryChange",
    "BlockDelineationManager",
    "BlockDelineationProcessor",
    "BlockDelineationPrompt",
    "BlockDelineationQuery",
    "BlockDelineationSubtitle",
    "BlockDelineationTestCase",
]
