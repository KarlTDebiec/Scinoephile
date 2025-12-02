#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese audio transcription translation."""

from __future__ import annotations

from scinoephile.audio.cantonese.translation.translation_answer import TranslationAnswer
from scinoephile.audio.cantonese.translation.translation_llm_queryer import (
    TranslationLLMQueryer,
)
from scinoephile.audio.cantonese.translation.translation_llm_text import (
    TranslationLLMText,
)
from scinoephile.audio.cantonese.translation.translation_query import TranslationQuery
from scinoephile.audio.cantonese.translation.translation_test_case import (
    TranslationTestCase,
)

__all__ = [
    "TranslationAnswer",
    "TranslationLLMQueryer",
    "TranslationLLMText",
    "TranslationQuery",
    "TranslationTestCase",
]
