#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for 粤文 transcription merging queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import Query
from scinoephile.core.llms.models import get_model_name

from .prompt import MergingPrompt

__all__ = ["MergingQuery"]


class MergingQuery(Query, ABC):
    """ABC for 粤文 transcription merging queries."""

    prompt_cls: ClassVar[type[MergingPrompt]]
    """Text for LLM correspondence."""

    @model_validator(mode="after")
    def validate_query(self) -> Self:
        """Ensure query is internally valid."""
        zhongwen = getattr(self, self.prompt_cls.zhongwen_field, None)
        yuewen_to_merge = getattr(self, self.prompt_cls.yuewen_to_merge_field, None)
        if not zhongwen:
            raise ValueError(self.prompt_cls.zhongwen_missing_error)
        if not yuewen_to_merge:
            raise ValueError(self.prompt_cls.yuewen_to_merge_missing_error)
        return self

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt_cls: type[MergingPrompt] = MergingPrompt,
    ) -> type[Self]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            Query type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        fields: dict[str, Any] = {
            prompt_cls.zhongwen_field: (
                str,
                Field(..., description=prompt_cls.zhongwen_description),
            ),
            prompt_cls.yuewen_to_merge_field: (
                list[str],
                Field(..., description=prompt_cls.yuewen_to_merge_description),
            ),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        return model
