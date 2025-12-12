#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription translation answers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import Answer2
from scinoephile.core.models import get_model_name

from .prompt import TranslationPrompt

__all__ = ["TranslationAnswer"]


class TranslationAnswer(Answer2, ABC):
    """Abstract base class for 粤文 transcription translation answers."""

    prompt_cls: ClassVar[type[TranslationPrompt]]
    """Text strings to be used for corresponding with LLM."""

    size: ClassVar[int]
    """Number of subtitles."""
    missing: ClassVar[tuple[int, ...]]
    """Indexes of missing subtitles (1-indexed)."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        size: int,
        missing: tuple[int, ...],
        prompt_cls: type[TranslationPrompt] = TranslationPrompt,
    ) -> type[Self]:
        """Get concrete answer class with provided configuration.

        Arguments:
            size: number of subtitles
            missing: indexes of missing subtitles
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            Answer type with appropriate configuration
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
            if idx in missing:
                key = f"yuewen_{idx + 1}"
                description = prompt_cls.yuewen_answer_description.format(idx=idx + 1)
                fields[key] = (str, Field(..., description=description))

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        model.size = size
        model.missing = missing
        return model
