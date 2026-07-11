#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to gap translation matters using LLMs.

Gap translation matters take in two subtitle Series where each reference block
has n subtitles and the corresponding target block has n minus m subtitles
because m target subtitles are missing. They fill the missing target subtitles
and output a single completed Series.

Package hierarchy (modules may import from any above):
* prompt
* models
* manager
* processor
"""

from __future__ import annotations

from .manager import GapTranslationManager
from .models import (
    GapTranslationAnswer,
    GapTranslationQuery,
    GapTranslationSubtitle,
    GapTranslationTestCase,
)
from .processor import GapTranslationProcessor
from .prompt import GapTranslationPrompt

__all__ = [
    "GapTranslationAnswer",
    "GapTranslationManager",
    "GapTranslationProcessor",
    "GapTranslationPrompt",
    "GapTranslationQuery",
    "GapTranslationSubtitle",
    "GapTranslationTestCase",
]
