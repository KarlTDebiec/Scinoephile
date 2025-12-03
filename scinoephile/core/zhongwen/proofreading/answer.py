#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 中文 proofreading answers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core.abcs import Answer

from .llm_text import ZhongwenProofreadingLLMText

__all__ = ["ZhongwenProofreadingAnswer"]


class ZhongwenProofreadingAnswer(Answer, ABC):
    """Abstract base class for 中文 proofreading answers."""

    text: ClassVar[type[ZhongwenProofreadingLLMText]]
    """Text strings to be used for corresponding with LLM."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        size: int,
        text: type[ZhongwenProofreadingLLMText] = ZhongwenProofreadingLLMText,
    ) -> type[Self]:
        """Get concrete answer class with provided size and text.

        Arguments:
            size: number of subtitles
            text: LLMText providing descriptions and messages
        Returns:
            Answer type with appropriate fields and text
        """
        fields = {}
        for idx in range(size):
            fields[f"xiugai_{idx + 1}"] = (
                str,
                Field("", description=text.beizhu_description.format(idx=idx + 1)),
            )
            fields[f"beizhu_{idx + 1}"] = (
                str,
                Field(
                    "",
                    description=text.beizhu_description.format(idx=idx + 1),
                    max_length=1000,
                ),
            )
        return create_model(
            f"{cls.__name__}_{size}_{text.__name__}",
            __base__=cls,
            __module__=cls.__module__,
            text=(ClassVar[type[ZhongwenProofreadingLLMText]], text),
            **fields,
        )
