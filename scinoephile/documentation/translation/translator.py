#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Translates README from English to Chinese."""

from __future__ import annotations

from scinoephile.core.abcs import FixedLLMQueryer
from scinoephile.documentation.translation.translate_answer import TranslateAnswer
from scinoephile.documentation.translation.translate_query import TranslateQuery
from scinoephile.documentation.translation.translate_test_case import TranslateTestCase


class Translator(FixedLLMQueryer[TranslateQuery, TranslateAnswer, TranslateTestCase]):
    """Translates README from English to Chinese."""

    @property
    def answer_example(self) -> TranslateAnswer:
        """Example answer."""
        return TranslateAnswer(updated_chinese="Updated Chinese README")

    @property
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are a helpful assistant that updates the Chinese version of a README.
        Use the updated English README as the source of truth.
        When appropriate, reference the out-of-date Chinese README to guide style and
        terminology.
        You must respect the Chinese language variant specified in the 'language' field.
        This value may be:
        - "zhongwen": Mandarin Chinese using traditional characters (繁體中文)
        - "yuewen": Cantonese using traditional characters (繁體粵文)
        """
