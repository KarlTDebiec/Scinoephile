#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for Zhongwen OCR fusion queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import Query
from scinoephile.core.models import get_model_name

from .prompt import ZhongwenFusionPrompt

__all__ = ["ZhongwenFusionQuery"]


class ZhongwenFusionQuery(Query, ABC):
    """Abstract base class for Zhongwen OCR fusion queries."""

    prompt_cls: ClassVar[type[ZhongwenFusionPrompt]]  # type: ignore
    """Text strings to be used for corresponding with LLM."""

    @model_validator(mode="after")
    def validate_query(self) -> Self:
        """Ensure query is internally valid."""
        lens = getattr(self, "lens", None)
        paddle = getattr(self, "paddle", None)
        if not lens:
            raise ValueError(self.prompt_cls.lens_missing_error)
        if not paddle:
            raise ValueError(self.prompt_cls.paddle_missing_error)
        if lens == paddle:
            raise ValueError(self.prompt_cls.lens_paddle_equal_error)
        return self

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt_cls: type[ZhongwenFusionPrompt] = ZhongwenFusionPrompt,
    ) -> type[Self]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            Query type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        fields: dict[str, Any] = {
            "lens": (str, Field(..., description=prompt_cls.lens_description)),
            "paddle": (
                str,
                Field(..., description=prompt_cls.paddle_description),
            ),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        return model
