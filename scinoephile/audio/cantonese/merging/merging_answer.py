#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for 粤文 merging."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.audio.cantonese.merging.merging_llm_text import MergingLLMText
from scinoephile.core.abcs import Answer


class MergingAnswer(Answer, ABC):
    """Answer for 粤文 merging."""

    text: ClassVar[type[MergingLLMText]]
    """Text strings to be used for corresponding with LLM."""

    @model_validator(mode="after")
    def validate_answer(self) -> Self:
        """Ensure answer is internally valid."""
        if not self.yuewen_merged:
            raise ValueError(self.text.yuewen_merged_missing_error)
        return self

    @classmethod
    @cache
    def get_answer_cls(cls, text: type[MergingLLMText] = MergingLLMText) -> type[Self]:
        """Get concrete answer class with provided text.

        Arguments:
            text: LLMText providing descriptions and messages
        Returns:
            Answer type with appropriate fields and text
        """
        fields = {
            "yuewen_merged": (
                str,
                Field(..., description=text.yuewen_merged_description),
            ),
        }
        return create_model(
            f"{cls.__name__}_{text.__name__}",
            __base__=cls,
            __module__=cls.__module__,
            text=(ClassVar[type[MergingLLMText]], text),
            **fields,
        )
