#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Translates 粤文 text based on corresponding 中文."""

from __future__ import annotations

from scinoephile.audio.cantonese.translation.translation_test_case import (
    TranslationTestCase,
)
from scinoephile.core.abcs import DynamicLLMQueryer
from scinoephile.documentation.translation import TranslateAnswer, TranslateQuery


class TranslationLLMQueryer[
    TQuery: TranslateQuery,
    TAnswer: TranslateAnswer,
    TTestCase: TranslationTestCase,
](DynamicLLMQueryer[TranslateQuery, TranslateAnswer, TranslationTestCase]):
    """Translates 粤文 text based on corresponding 中文."""

    @property
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return (
            "Translate the missing 粤文 subtitles based on the corresponding 中文 "
            "subtitles."
        )

    @staticmethod
    def get_answer_example(answer_cls: type[TAnswer]) -> TAnswer:
        """Example answer."""
        answer_values = {}
        for key in answer_cls.model_fields.keys():
            idx = key.split("_")[1]
            answer_values[key] = (
                f"粤文 subtitle {idx} translated from query's 中文 subtitle {idx}"
            )
        return answer_cls(**answer_values)
