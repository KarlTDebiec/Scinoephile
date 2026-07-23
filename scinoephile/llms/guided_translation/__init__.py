#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to guided translation using LLMs.

Package hierarchy (modules may import from any above):
* prompt
* models
* manager
* processor
"""

from __future__ import annotations

from .manager import GuidedTranslationManager
from .models import (
    GuidedTranslationAnswer,
    GuidedTranslationQuery,
    GuidedTranslationSubtitle,
    GuidedTranslationTestCase,
)
from .processor import GuidedTranslationProcessor
from .prompt import GuidedTranslationPrompt

__all__ = [
    "GuidedTranslationAnswer",
    "GuidedTranslationManager",
    "GuidedTranslationProcessor",
    "GuidedTranslationPrompt",
    "GuidedTranslationQuery",
    "GuidedTranslationSubtitle",
    "GuidedTranslationTestCase",
]
