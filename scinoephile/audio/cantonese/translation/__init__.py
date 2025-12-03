#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese audio transcription translation."""

from __future__ import annotations

from .answer import TranslationAnswer
from .llm_queryer import TranslationLLMQueryer
from .prompt import TranslationPrompt
from .query import TranslationQuery
from .test_case import TranslationTestCase

__all__ = [
    "TranslationAnswer",
    "TranslationLLMQueryer",
    "TranslationPrompt",
    "TranslationQuery",
    "TranslationTestCase",
]
