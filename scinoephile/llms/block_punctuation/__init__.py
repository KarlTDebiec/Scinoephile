#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Block-level subtitle punctuation using sparse LLM changes.

Package hierarchy (modules may import from any above):
* prompt
* models
* manager
* processor
"""

from __future__ import annotations

from .manager import BlockPunctuationManager
from .models import (
    BlockPunctuationAnswer,
    BlockPunctuationQuery,
    BlockPunctuationSubtitle,
    BlockPunctuationTestCase,
)
from .processor import BlockPunctuationProcessor
from .prompt import BlockPunctuationPrompt

__all__ = [
    "BlockPunctuationAnswer",
    "BlockPunctuationManager",
    "BlockPunctuationProcessor",
    "BlockPunctuationPrompt",
    "BlockPunctuationQuery",
    "BlockPunctuationSubtitle",
    "BlockPunctuationTestCase",
]
