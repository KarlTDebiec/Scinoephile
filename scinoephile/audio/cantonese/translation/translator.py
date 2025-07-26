#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Translates 粤文 text based on corresponding 中文."""

from __future__ import annotations

from scinoephile.audio.cantonese.shifting.shift_answer import ShiftAnswer
from scinoephile.audio.cantonese.shifting.shift_query import ShiftQuery
from scinoephile.audio.cantonese.shifting.shift_test_case import ShiftTestCase
from scinoephile.core.abcs import LLMQueryer


class Translator(LLMQueryer[ShiftQuery, ShiftAnswer, ShiftTestCase]):
    """Translates 粤文 text based on corresponding 中文."""

    def __init__(self, model, provider, max_attempts: int = 3) -> None:
        self.model = model
        self.provider = provider
        self.max_attempts = max_attempts

    def __call__(self, alignment, zhongwen: str, yuewen: str) -> ShiftAnswer:
        QueryModel, AnswerModel = self.get_translate_models(alignment)
        query = QueryModel(
            one_zhongwen=zhongwen[0],
            two_zhongwen=zhongwen[1],
            one_yuewen=yuewen[0],
            two_yuewen=yuewen[1],
        )
        prompt = self.construct_prompt(query)
        answer = self.provider.chat_completion(
            model=self.model,
            prompt=prompt,
            response_format=AnswerModel,
            max_attempts=self.max_attempts,
        )
        answer.validate()
        return answer

    def answer_example(self) -> ShiftAnswer:
        """Example answer."""
        return ShiftAnswer(
            one_yuewen_shifted="粤文 one shifted",
            two_yuewen_shifted="粤文 two shifted",
        )

    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return (
            "Read the two consecutive 中文 texts and two consecutive 粤文 texts, and adjust "
            "the breakpoint between the first and second 粤文 texts so that they align with "
            "the two corresponding 中文 texts. "
            "This is, either shift characters from the end of the first 粤文 text to the "
            "beginning of the second 粤文 text, or shift characters from the beginning of "
            "the second 粤文 text to the end of the first 粤文 text. "
            "If no changes are needed, return the original 粤文 texts. "
            "Include all 粤文 characters from the inputs in the same order in the outputs. "
            "Do not copy punctuation or whitespace from the 中文 texts."
        )
