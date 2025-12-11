#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription shifting queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.abcs import Query

from .prompt import ShiftingPrompt

__all__ = ["ShiftingQuery"]


class ShiftingQuery(Query, ABC):
    """Abstract base class for 粤文 transcription shifting queries."""

    text: ClassVar[type[ShiftingPrompt]]
    """Text strings to be used for corresponding with LLM."""

    @model_validator(mode="after")
    def validate_query(self) -> Self:
        """Ensure query is internally valid."""
        if not self.yuewen_1 and not self.yuewen_2:
            raise ValueError(self.text.yuewen_1_yuewen_2_missing_error)
        return self

    @classmethod
    @cache
    def get_query_cls(cls, text: type[ShiftingPrompt] = ShiftingPrompt) -> type[Self]:
        """Get concrete query class with provided configuration.

        Arguments:
            text: Prompt providing descriptions and messages
        Returns:
            Query type with appropriate configuration
        """
        fields = {
            "zhongwen_1": (str, Field(..., description=text.zhongwen_1_description)),
            "zhongwen_2": (str, Field(..., description=text.zhongwen_2_description)),
            "yuewen_1": (str, Field("", description=text.yuewen_1_description)),
            "yuewen_2": (str, Field("", description=text.yuewen_2_description)),
        }
        return create_model(
            f"{cls.__name__}_{text.__name__}",
            __base__=cls,
            __module__=cls.__module__,
            text=(ClassVar[type[ShiftingPrompt]], text),
            **fields,
        )
