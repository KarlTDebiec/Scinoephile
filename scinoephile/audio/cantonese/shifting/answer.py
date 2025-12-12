#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription shifting answers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core.llms import Answer
from scinoephile.core.models import get_model_name

from .prompt import ShiftingPrompt

__all__ = ["ShiftingAnswer"]


class ShiftingAnswer(Answer, ABC):
    """Abstract base class for 粤文 transcription shifting answers."""

    prompt_cls: ClassVar[type[ShiftingPrompt]]
    """Text strings to be used for corresponding with LLM."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt_cls: type[ShiftingPrompt] = ShiftingPrompt,
    ) -> type[Self]:
        """Get concrete answer class with provided configuartion.

        Arguments:
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            Answer type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        fields: dict[str, Any] = {
            "yuewen_1_shifted": (
                str,
                Field("", description=prompt_cls.yuewen_1_shifted_description),
            ),
            "yuewen_2_shifted": (
                str,
                Field("", description=prompt_cls.yuewen_2_shifted_description),
            ),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        return model
