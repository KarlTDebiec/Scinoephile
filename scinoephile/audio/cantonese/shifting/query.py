#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription shifting queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import Query
from scinoephile.core.models import get_model_name

from .prompt import ShiftingPrompt

__all__ = ["ShiftingQuery"]


class ShiftingQuery(Query, ABC):
    """Abstract base class for 粤文 transcription shifting queries."""

    prompt_cls: ClassVar[type[ShiftingPrompt]]
    """Text strings to be used for corresponding with LLM."""

    @model_validator(mode="after")
    def validate_query(self) -> Self:
        """Ensure query is internally valid."""
        yuewen_1 = getattr(self, "yuewen_1", None)
        yuewen_2 = getattr(self, "yuewen_2", None)
        if not yuewen_1 and not yuewen_2:
            raise ValueError(self.prompt_cls.yuewen_1_yuewen_2_missing_error)
        return self

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt_cls: type[ShiftingPrompt] = ShiftingPrompt,
    ) -> type[Self]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            Query type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        fields: dict[str, Any] = {
            "zhongwen_1": (
                str,
                Field(..., description=prompt_cls.zhongwen_1_description),
            ),
            "zhongwen_2": (
                str,
                Field(..., description=prompt_cls.zhongwen_2_description),
            ),
            "yuewen_1": (str, Field("", description=prompt_cls.yuewen_1_description)),
            "yuewen_2": (str, Field("", description=prompt_cls.yuewen_2_description)),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        return model
