#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 中文 proofreading answers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core.llms import Answer2
from scinoephile.core.models import get_model_name

from .prompt import ZhongwenProofreadingPrompt

__all__ = ["ZhongwenProofreadingAnswer"]


class ZhongwenProofreadingAnswer(Answer2, ABC):
    """Abstract base class for 中文 proofreading answers."""

    prompt_cls: ClassVar[type[ZhongwenProofreadingPrompt]]  # type: ignore
    """Text strings to be used for corresponding with LLM."""

    size: ClassVar[int]
    """Number of subtitles."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        size: int,
        prompt_cls: type[ZhongwenProofreadingPrompt] = ZhongwenProofreadingPrompt,
    ) -> type[Self]:
        """Get concrete answer class with provided configuration.

        Arguments:
            size: number of subtitles
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            Answer type with appropriate configuration
        """
        name = get_model_name(cls.__name__, f"{size}_{prompt_cls.__name__}")
        fields: dict[str, Any] = {}
        for idx in range(size):
            key = f"xiugai_{idx + 1}"
            description = prompt_cls.revised_description.format(idx=idx + 1)
            fields[key] = (str, Field("", description=description, max_length=1000))
            key = f"beizhu_{idx + 1}"
            description = prompt_cls.note_description.format(idx=idx + 1)
            fields[key] = (str, Field("", description=description, max_length=1000))

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        model.size = size
        return model
