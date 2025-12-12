#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription translation queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import Query
from scinoephile.core.models import get_model_name

from .prompt import TranslationPrompt

__all__ = ["TranslationQuery"]


class TranslationQuery(Query, ABC):
    """Abstract base class for 粤文 transcription translation queries."""

    prompt_cls: ClassVar[type[TranslationPrompt]]
    """Text strings to be used for corresponding with LLM."""

    size: ClassVar[int]
    """Number of subtitles."""
    missing: ClassVar[tuple[int, ...]]
    """Indexes of missing subtitles (1-indexed)."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        missing: tuple[int, ...],
        prompt_cls: type[TranslationPrompt] = TranslationPrompt,
    ) -> type[Self]:
        """Get concrete query class with provided configuration.

        Arguments:
            size: number of subtitles
            missing: indexes of missing subtitles
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            Query type with appropriate configuration
        """
        if any(m < 0 or m > size for m in missing):
            raise ScinoephileError(
                f"Missing indices must be in range 1 to {size}, got {missing}."
            )

        name = get_model_name(
            cls.__name__,
            f"{size}_"
            f"{'-'.join(map(str, [m + 1 for m in missing]))}_"
            f"{prompt_cls.__name__}",
        )
        fields: dict[str, Any] = {}
        for idx in range(size):
            key = f"zhongwen_{idx + 1}"
            description = prompt_cls.zhongwen_description.format(idx=idx + 1)
            fields[key] = (str, Field(..., description=description))
            if idx not in missing:
                key = f"yuewen_{idx + 1}"
                description = prompt_cls.yuewen_query_description.format(idx=idx + 1)
                fields[key] = (str, Field(..., description=description))

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        model.size = size
        model.missing = missing
        return model
