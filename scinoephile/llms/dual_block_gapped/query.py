#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for dual block gapped queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core import ScinoephileError
from scinoephile.llms.base import Query
from scinoephile.llms.base.models import get_model_name

from .prompt import DualBlockGappedPrompt

__all__ = ["DualBlockGappedQuery"]


class DualBlockGappedQuery(Query, ABC):
    """ABC for dual block gapped queries."""

    prompt_cls: ClassVar[type[DualBlockGappedPrompt]]
    """Text for LLM correspondence."""

    size: ClassVar[int]
    """Number of subtitles."""
    gaps: ClassVar[tuple[int, ...]]
    """Indexes of subtitles missing from the primary series (0-indexed)."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        gaps: tuple[int, ...],
        prompt_cls: type[DualBlockGappedPrompt] = DualBlockGappedPrompt,
    ) -> type[Self]:
        """Get concrete query class with provided configuration.

        Arguments:
            size: number of subtitles
            gaps: indexes of subtitles missing from the primary series
            prompt_cls: text for LLM correspondence
        Returns:
            Query type with appropriate configuration
        """
        if any(gap < 0 or gap >= size for gap in gaps):
            raise ScinoephileError(
                f"Gap indices must be in range 0 to {size - 1}, got {gaps}."
            )

        name = get_model_name(
            cls.__name__,
            f"{size}_"
            f"{'-'.join(map(str, [gap + 1 for gap in gaps]))}_"
            f"{prompt_cls.__name__}",
        )
        fields: dict[str, Any] = {}
        for idx in range(size):
            if idx not in gaps:
                key = prompt_cls.source_one(idx + 1)
                description = prompt_cls.source_one_desc(idx + 1)
                fields[key] = (str, Field(..., description=description))
            key = prompt_cls.source_two(idx + 1)
            description = prompt_cls.source_two_desc(idx + 1)
            fields[key] = (str, Field(..., description=description))

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        model.size = size
        model.gaps = gaps
        return model
