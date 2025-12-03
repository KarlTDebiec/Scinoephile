#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 中文 OCR fusion answers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.abcs import Answer

from .llm_text import ZhongwenFusionLLMText

__all__ = ["ZhongwenFusionAnswer"]


class ZhongwenFusionAnswer(Answer, ABC):
    """Abstract base class for 中文 OCR fusion answers."""

    text: ClassVar[type[ZhongwenFusionLLMText]]
    """Text strings to be used for corresponding with LLM."""

    @model_validator(mode="after")
    def validate_answer(self) -> Self:
        """Ensure answer is internally valid."""
        if not self.ronghe:
            raise ValueError(self.text.ronghe_missing_error)
        if not self.beizhu:
            raise ValueError(self.text.beizhu_missing_error)
        return self

    @classmethod
    @cache
    def get_answer_cls(
        cls, text: type[ZhongwenFusionLLMText] = ZhongwenFusionLLMText
    ) -> type[Self]:
        """Get concrete answer class with provided text.

        Arguments:
            text: LLMText providing descriptions and messages
        Returns:
            Answer type with appropriate fields and text
        """
        fields = {
            "ronghe": (str, Field(..., description=text.ronghe_description)),
            "beizhu": (str, Field(..., description=text.beizhu_description)),
        }
        return create_model(
            f"{cls.__name__}_{text.__name__}",
            __base__=cls,
            __module__=cls.__module__,
            text=(ClassVar[type[ZhongwenFusionLLMText]], text),
            **fields,
        )
