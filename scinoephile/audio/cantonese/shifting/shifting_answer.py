#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription shifting answers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model

from scinoephile.audio.cantonese.shifting.shifting_llm_text import ShiftingLLMText
from scinoephile.core.abcs import Answer


class ShiftingAnswer(Answer, ABC):
    """Abstract base class for 粤文 transcription shifting answers."""

    text: ClassVar[type[ShiftingLLMText]]
    """Text strings to be used for corresponding with LLM."""

    @classmethod
    @cache
    def get_answer_cls(
        cls, text: type[ShiftingLLMText] = ShiftingLLMText
    ) -> type[Self]:
        """Get concrete answer class with provided text.

        Arguments:
            text: LLMText providing descriptions and messages
        Returns:
            Answer type with appropriate fields and text
        """
        fields = {
            "yuewen_1_shifted": (
                str,
                Field(..., description=text.yuewen_1_shifted_description),
            ),
            "yuewen_2_shifted": (
                str,
                Field(..., description=text.yuewen_2_shifted_description),
            ),
        }
        return create_model(
            f"{cls.__name__}_{text.__name__}",
            __base__=cls,
            __module__=cls.__module__,
            text=(ClassVar[type[ShiftingLLMText]], text),
            **fields,
        )
