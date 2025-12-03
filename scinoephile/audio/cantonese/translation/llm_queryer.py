#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Translates 粤文 text based on corresponding 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.abcs import LLMQueryer

from .answer import TranslationAnswer
from .prompt import TranslationPrompt
from .query import TranslationQuery
from .test_case import TranslationTestCase

__all__ = ["TranslationLLMQueryer"]


class TranslationLLMQueryer(
    LLMQueryer[TranslationQuery, TranslationAnswer, TranslationTestCase]
):
    """Translates 粤文 text based on corresponding 中文."""

    text: ClassVar[type[TranslationPrompt]] = TranslationPrompt
    """Text strings to be used for corresponding with LLM."""
