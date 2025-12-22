#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for dual track / single subtitle queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model

from scinoephile.llms.base import Query
from scinoephile.llms.base.models import get_model_name

from .prompt import DualSinglePrompt

__all__ = ["DualSingleQuery"]


class DualSingleQuery(Query, ABC):
    """ABC for dual track / single subtitle queries."""

    prompt_cls: ClassVar[type[DualSinglePrompt]]
    """Text for LLM correspondence."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt_cls: type[DualSinglePrompt],
    ) -> type[Self]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            Query type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        fields: dict[str, Any] = {
            prompt_cls.src_1: (str, Field(..., description=prompt_cls.src_1_desc)),
            prompt_cls.src_2: (str, Field(..., description=prompt_cls.src_2_desc)),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        return model
