#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for English proofreading queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core.llms import Query
from scinoephile.core.models import get_model_name

from .prompt import EnglishProofreadingPrompt

__all__ = ["EnglishProofreadingQuery"]


class EnglishProofreadingQuery(Query, ABC):
    """Abstract base class for English proofreading queries."""

    prompt_cls: ClassVar[type[EnglishProofreadingPrompt]]  # type: ignore
    """Text strings to be used for corresponding with LLM."""

    size: ClassVar[int]
    """Number of subtitles."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        prompt_cls: type[EnglishProofreadingPrompt] = EnglishProofreadingPrompt,
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
            key = prompt_cls.subtitle_field(idx + 1)
            description = prompt_cls.subtitle_description(idx + 1)
            fields[key] = (str, Field(..., description=description, max_length=1000))

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        model.size = size
        return model
