#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for dual track / block queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model

from scinoephile.llms.base import Query
from scinoephile.llms.base.models import get_model_name

from .prompt import DualBlockPrompt

__all__ = [
    "DualBlockQuery",
]


class DualBlockQuery(Query, ABC):
    """ABC for dual track / block queries."""

    prompt_cls: ClassVar[type[DualBlockPrompt]]
    """Text for LLM correspondence."""

    size: ClassVar[int]
    """Number of subtitles."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        prompt_cls: type[DualBlockPrompt] = DualBlockPrompt,
    ) -> type[Self]:
        """Get concrete query class with provided configuration.

        Arguments:
            size: number of subtitles
            prompt_cls: text for LLM correspondence
        Returns:
            Query type with appropriate configuration
        """
        name = get_model_name(cls.__name__, f"{size}_{prompt_cls.__name__}")
        fields: dict[str, Any] = {}
        for idx in range(size):
            key = prompt_cls.source_one(idx + 1)
            description = prompt_cls.source_one_desc(idx + 1)
            fields[key] = (str, Field(..., description=description))
            key = prompt_cls.source_two(idx + 1)
            description = prompt_cls.source_two_desc(idx + 1)
            fields[key] = (str, Field(..., description=description))

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        model.size = size
        return model
