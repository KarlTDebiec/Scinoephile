#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription review queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core.abcs import Query

from .prompt import ReviewPrompt

__all__ = ["ReviewQuery"]


class ReviewQuery(Query, ABC):
    """Abstract base class for 粤文 transcription review queries."""

    text: ClassVar[type[ReviewPrompt]]
    """Text strings to be used for corresponding with LLM."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        text: type[ReviewPrompt] = ReviewPrompt,
    ) -> type[Self]:
        """Get concrete query class with provided configuration.

        Arguments:
            size: number of subtitles
            text: Prompt providing descriptions and messages
        Returns:
            Query type with appropriate configuration
        """
        fields = {}
        for idx in range(size):
            fields[f"zhongwen_{idx + 1}"] = (
                str,
                Field(..., description=text.zhongwen_description.format(idx=idx + 1)),
            )
            fields[f"yuewen_{idx + 1}"] = (
                str,
                Field(..., description=text.yuewen_description.format(idx=idx + 1)),
            )
        return create_model(
            f"{cls.__name__}_{size}_{text.__name__}",
            __base__=cls,
            __module__=cls.__module__,
            text=(ClassVar[type[ReviewPrompt]], text),
            **fields,
        )
