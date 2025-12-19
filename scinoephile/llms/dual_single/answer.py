#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for dual track / single subtitle answers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.llms.base import Answer
from scinoephile.llms.base.models import get_model_name

from .prompt import DualSinglePrompt

__all__ = ["DualSingleAnswer"]


class DualSingleAnswer(Answer, ABC):
    """ABC for dual track / single subtitle answers."""

    prompt_cls: ClassVar[type[DualSinglePrompt]]
    """Text for LLM correspondence."""

    @model_validator(mode="after")
    def validate_answer(self) -> Self:
        """Ensure answer is internally valid."""
        if getattr(self, self.prompt_cls.output_field, None) is None:
            raise ValueError(self.prompt_cls.output_missing_error)
        if getattr(self, self.prompt_cls.note_field, None) is None:
            raise ValueError(self.prompt_cls.note_missing_error)
        return self

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt_cls: type[DualSinglePrompt],
    ) -> type[Self]:
        """Get concrete answer class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            Answer type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        fields: dict[str, Any] = {
            prompt_cls.output_field: (
                str,
                Field(..., description=prompt_cls.output_description),
            ),
            prompt_cls.note_field: (
                str,
                Field("", description=prompt_cls.note_description),
            ),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        return model
