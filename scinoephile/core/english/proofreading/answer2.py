#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for English proofreading answers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core.abcs.answer2 import Answer2

from .prompt2 import EnglishProofreadingPrompt2

__all__ = ["EnglishProofreadingAnswer2"]


class EnglishProofreadingAnswer2(Answer2, ABC):
    """Abstract base class for English proofreading answers."""

    prompt_cls: ClassVar[type[EnglishProofreadingPrompt2]]  # type: ignore
    """Text strings to be used for corresponding with LLM."""

    size: ClassVar[int]
    """Number of subtitles."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        size: int,
        prompt_cls: type[EnglishProofreadingPrompt2] = EnglishProofreadingPrompt2,
    ) -> type[Self]:
        """Get concrete answer class with provided size and text.

        Arguments:
            size: number of subtitles
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            Answer type with appropriate fields and text
        """
        fields = {}
        for idx in range(size):
            key = f"revised_{idx + 1}"
            description = prompt_cls.revised_description.format(idx=idx + 1)
            fields[key] = (str, Field("", description=description, max_length=1000))
            key = f"note_{idx + 1}"
            description = prompt_cls.note_description.format(idx=idx + 1)
            fields[key] = (str, Field("", description=description, max_length=1000))
        name = f"{cls.__name__}_{size}_{prompt_cls.__name__}"
        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        model.size = size
        return model
