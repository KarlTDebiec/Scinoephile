#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for OCR fusion queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self, cast

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import Prompt, Query
from scinoephile.core.models import get_model_name

from .prompt import FusionPrompt

__all__ = ["FusionQuery"]


class FusionQuery(Query, ABC):
    """ABC for OCR fusion queries."""

    prompt_cls: ClassVar[type[Prompt]]
    """Text strings to be used for corresponding with LLM."""

    @model_validator(mode="after")
    def validate_query(self) -> Self:
        """Ensure query is internally valid."""
        prompt_cls = cast(type[FusionPrompt], self.prompt_cls)
        source_one_field = prompt_cls.source_one_field
        source_two_field = prompt_cls.source_two_field
        source_one = getattr(self, source_one_field, None)
        source_two = getattr(self, source_two_field, None)
        if not source_one:
            raise ValueError(prompt_cls.source_one_missing_error)
        if not source_two:
            raise ValueError(prompt_cls.source_two_missing_error)
        if source_one == source_two:
            raise ValueError(prompt_cls.sources_equal_error)
        return self

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt_cls: type[FusionPrompt],
    ) -> type[Self]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            Query type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        fields: dict[str, Any] = {
            prompt_cls.source_one_field: (
                str,
                Field(..., description=prompt_cls.source_one_description),
            ),
            prompt_cls.source_two_field: (
                str,
                Field(..., description=prompt_cls.source_two_description),
            ),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        return model
