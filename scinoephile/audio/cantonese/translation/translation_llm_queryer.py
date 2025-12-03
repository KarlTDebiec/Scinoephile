#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Translates 粤文 text based on corresponding 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.audio.cantonese.translation.translation_answer import TranslationAnswer
from scinoephile.audio.cantonese.translation.translation_llm_text import (
    TranslationLLMText,
)
from scinoephile.audio.cantonese.translation.translation_query import TranslationQuery
from scinoephile.audio.cantonese.translation.translation_test_case import (
    TranslationTestCase,
)
from scinoephile.core.abcs import LLMQueryer


class TranslationLLMQueryer(
    LLMQueryer[TranslationQuery, TranslationAnswer, TranslationTestCase]
):
    """Translates 粤文 text based on corresponding 中文."""

    text: ClassVar[type[TranslationLLMText]] = TranslationLLMText
    """Text strings to be used for corresponding with LLM."""
