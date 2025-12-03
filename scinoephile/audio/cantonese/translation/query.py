#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription translation queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core import ScinoephileError
from scinoephile.core.abcs import Query

from .prompt import TranslationPrompt

__all__ = ["TranslationQuery"]


class TranslationQuery(Query, ABC):
    """Abstract base class for 粤文 transcription translation queries."""

    text: ClassVar[type[TranslationPrompt]]
    """Text strings to be used for corresponding with LLM."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        missing: tuple[int, ...],
        text: type[TranslationPrompt] = TranslationPrompt,
    ) -> type[Self]:
        """Get concrete query class with provided size, missing, and text.

        Arguments:
            size: number of subtitles
            missing: indexes of missing subtitles
            text: Prompt providing descriptions and messages
        Returns:
            Query type with appropriate fields and text
        """
        if any(m < 0 or m > size for m in missing):
            raise ScinoephileError(
                f"Missing indices must be in range 1 to {size}, got {missing}."
            )
        fields = {}
        for idx in range(size):
            fields[f"zhongwen_{idx + 1}"] = (
                str,
                Field(..., description=text.zhongwen_description),
            )
            if idx not in missing:
                fields[f"yuewen_{idx + 1}"] = (
                    str,
                    Field(
                        ...,
                        description=text.yuewen_query_description.format(idx=idx + 1),
                    ),
                )
        name = (
            f"{cls.__name__}_{size}_{'-'.join(map(str, [m + 1 for m in missing]))}"
            f"_{text.__name__}"
        )
        return create_model(
            name[:64],
            __base__=cls,
            __module__=cls.__module__,
            text=(ClassVar[type[TranslationPrompt]], text),
            **fields,
        )
