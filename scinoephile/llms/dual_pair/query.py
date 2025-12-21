#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for dual pair queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.llms.base import Query
from scinoephile.llms.base.models import get_model_name

from .prompt import DualPairPrompt

__all__ = ["DualPairQuery"]


class DualPairQuery(Query, ABC):
    """ABC for dual pair queries."""

    prompt_cls: ClassVar[type[DualPairPrompt]]
    """Text for LLM correspondence."""

    @model_validator(mode="after")
    def validate_query(self) -> Self:
        """Ensure query is internally valid."""
        target_1 = getattr(self, self.prompt_cls.source_two_sub_one_field, None)
        target_2 = getattr(self, self.prompt_cls.source_two_sub_two_field, None)
        if not target_1 and not target_2:
            raise ValueError(self.prompt_cls.source_two_sub_one_sub_two_missing_error)
        return self

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt_cls: type[DualPairPrompt] = DualPairPrompt,
    ) -> type[Self]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            Query type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        fields: dict[str, Any] = {
            prompt_cls.source_one_sub_one_field: (
                str,
                Field(..., description=prompt_cls.source_one_sub_one_desc),
            ),
            prompt_cls.source_one_sub_two_field: (
                str,
                Field(..., description=prompt_cls.source_one_sub_two_desc),
            ),
            prompt_cls.source_two_sub_one_field: (
                str,
                Field("", description=prompt_cls.source_two_sub_one_desc),
            ),
            prompt_cls.source_two_sub_two_field: (
                str,
                Field("", description=prompt_cls.source_two_sub_two_desc),
            ),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        return model
