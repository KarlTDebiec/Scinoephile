#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 中文 OCR fusion queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.abcs import Query

from .prompt import ZhongwenFusionPrompt

__all__ = ["ZhongwenFusionQuery"]


class ZhongwenFusionQuery(Query, ABC):
    """Abstract base class for 中文 OCR fusion queries."""

    text: ClassVar[type[ZhongwenFusionPrompt]]
    """Text strings to be used for corresponding with LLM."""

    @model_validator(mode="after")
    def validate_query(self) -> Self:
        """Ensure query is internally valid."""
        if not self.lens:
            raise ValueError(self.text.lens_missing_error)
        if not self.paddle:
            raise ValueError(self.text.paddle_missing_error)
        if self.lens == self.paddle:
            raise ValueError(self.text.lens_paddle_equal_error)
        return self

    @classmethod
    @cache
    def get_query_cls(
        cls, text: type[ZhongwenFusionPrompt] = ZhongwenFusionPrompt
    ) -> type[Self]:
        """Get concrete query class with provided text.

        Arguments:
            text: Prompt providing descriptions and messages
        Returns:
            Query type with appropriate fields and text
        """
        fields = {
            "lens": (str, Field(..., description=text.lens_description)),
            "paddle": (str, Field(..., description=text.paddle_description)),
        }
        return create_model(
            f"{cls.__name__}_{text.__name__}",
            __base__=cls,
            __module__=cls.__module__,
            text=(ClassVar[type[ZhongwenFusionPrompt]], text),
            **fields,
        )
