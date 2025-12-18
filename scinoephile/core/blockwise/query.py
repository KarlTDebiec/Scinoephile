#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for blockwise review queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core.llms import Query
from scinoephile.core.llms.models import get_model_name

from .prompt import BlockwisePrompt

__all__ = ["BlockwiseQuery"]


class BlockwiseQuery(Query, ABC):
    """ABC for blockwise review queries."""

    prompt_cls: ClassVar[type[BlockwisePrompt]]
    """Text for LLM correspondence."""

    size: ClassVar[int]
    """Number of items."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        prompt_cls: type[BlockwisePrompt],
    ) -> type[Self]:
        """Get concrete query class with provided configuration.

        Arguments:
            size: number of items
            prompt_cls: text for LLM correspondence
        Returns:
            Query type with appropriate configuration
        """
        name = get_model_name(cls.__name__, f"{size}_{prompt_cls.__name__}")
        fields: dict[str, Any] = {}
        for idx in range(size):
            key = prompt_cls.input_field(idx + 1)
            desc = prompt_cls.input_description(idx + 1)
            fields[key] = (str, Field(..., description=desc, max_length=1000))

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        model.size = size
        return model
