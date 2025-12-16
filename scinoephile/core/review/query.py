#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription review queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core.llms import Query
from scinoephile.core.yue.prompt import ReviewPrompt

__all__ = ["ReviewQuery"]

from scinoephile.core.models import get_model_name


class ReviewQuery(Query, ABC):
    """Abstract base class for 粤文 transcription review queries."""

    prompt_cls: ClassVar[type[ReviewPrompt]]
    """Text strings to be used for corresponding with LLM."""

    size: ClassVar[int]
    """Number of subtitles."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        prompt_cls: type[ReviewPrompt] = ReviewPrompt,
    ) -> type[Self]:
        """Get concrete query class with provided configuration.

        Arguments:
            size: number of subtitles
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            Query type with appropriate configuration
        """
        name = get_model_name(cls.__name__, f"{size}_{prompt_cls.__name__}")
        fields: dict[str, Any] = {}
        for idx in range(size):
            key = prompt_cls.zhongwen_field(idx + 1)
            description = prompt_cls.zhongwen_description(idx + 1)
            fields[key] = (str, Field(..., description=description))
            key = prompt_cls.yuewen_field(idx + 1)
            description = prompt_cls.yuewen_description(idx + 1)
            fields[key] = (str, Field(..., description=description))

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        model.size = size
        return model
