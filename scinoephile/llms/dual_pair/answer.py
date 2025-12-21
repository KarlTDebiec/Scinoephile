#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for dual pair answers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model

from scinoephile.llms.base import Answer
from scinoephile.llms.base.models import get_model_name

from .prompt import DualPairPrompt

__all__ = ["DualPairAnswer"]


class DualPairAnswer(Answer, ABC):
    """ABC for dual pair answers."""

    prompt_cls: ClassVar[type[DualPairPrompt]]
    """Text for LLM correspondence."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt_cls: type[DualPairPrompt] = DualPairPrompt,
    ) -> type[Self]:
        """Get concrete answer class with provided configuartion.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            Answer type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        fields: dict[str, Any] = {
            prompt_cls.source_two_sub_one_shifted_field: (
                str,
                Field("", description=prompt_cls.source_two_sub_one_shifted_desc),
            ),
            prompt_cls.source_two_sub_two_shifted_field: (
                str,
                Field("", description=prompt_cls.source_two_sub_two_shifted_desc),
            ),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        return model
