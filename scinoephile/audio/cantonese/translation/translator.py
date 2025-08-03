#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Translates 粤文 text based on corresponding 中文."""

from __future__ import annotations

from functools import cached_property

from scinoephile.audio.cantonese.translation.abcs import TranslateTestCase
from scinoephile.core.abcs import Answer, DynamicLLMQueryer, Query


class Translator[TQuery: Query, TAnswer: Answer, TTestCase: TranslateTestCase](
    DynamicLLMQueryer[Query, Answer, TranslateTestCase]
):
    """Translates 粤文 text based on corresponding 中文."""

    @cached_property
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return "Translate the missing 粤文 texts based on the corresponding 中文."

    @staticmethod
    def get_answer_example(answer_cls: type[TAnswer]) -> TAnswer:
        """Example answer."""
        answer_values = {}
        for key in answer_cls.model_fields.keys():
            idx = key.split("_")[1]
            answer_values[key] = (
                f"粤文 text {idx} translated from query's 中文 text {idx}"
            )
        return answer_cls(**answer_values)
