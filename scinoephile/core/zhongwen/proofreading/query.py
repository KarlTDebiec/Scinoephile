#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 中文 proofreading queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core.abcs import Query

from .llm_text import ZhongwenProofreadingLLMText

__all__ = ["ZhongwenProofreadingQuery"]


class ZhongwenProofreadingQuery(Query, ABC):
    """Abstract base class for 中文 proofreading queries."""

    text: ClassVar[type[ZhongwenProofreadingLLMText]]
    """Text strings to be used for corresponding with LLM."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        text: type[ZhongwenProofreadingLLMText] = ZhongwenProofreadingLLMText,
    ) -> type[Self]:
        """Get concrete query class with provided size and text.

        Arguments:
            size: number of subtitles
            text: LLMText providing descriptions and messages
        Returns:
            Query type with appropriate fields and text
        """
        fields = {}
        for idx in range(size):
            fields[f"zimu_{idx + 1}"] = (
                str,
                Field(..., description=text.zimu_description.format(idx=idx + 1)),
            )
        return create_model(
            f"{cls.__name__}_{size}_{text.__name__}",
            __base__=cls,
            __module__=cls.__module__,
            text=(ClassVar[type[ZhongwenProofreadingLLMText]], text),
            **fields,
        )
