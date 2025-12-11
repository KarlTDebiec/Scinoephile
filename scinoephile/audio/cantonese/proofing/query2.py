#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription proofing queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import Query2
from scinoephile.core.models import get_cls_name

from .prompt2 import ProofingPrompt2

__all__ = ["ProofingQuery2"]


class ProofingQuery2(Query2, ABC):
    """Abstract base class for 粤文 transcription proofing queries."""

    prompt_cls: ClassVar[type[ProofingPrompt2]]
    """Text strings to be used for corresponding with LLM."""

    @model_validator(mode="after")
    def validate_query(self) -> Self:
        """Ensure query is internally valid."""
        zhongwen = getattr(self, "zhongwen", None)
        yuewen = getattr(self, "yuewen", None)
        if not zhongwen:
            raise ValueError(self.prompt_cls.zhongwen_missing_error)
        if not yuewen:
            raise ValueError(self.prompt_cls.yuewen_missing_error)
        return self

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt_cls: type[ProofingPrompt2] = ProofingPrompt2,
    ) -> type[Self]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            Query type with appropriate configuration
        """
        name = get_cls_name(cls.__name__, prompt_cls.__name__)
        fields = {
            "zhongwen": (str, Field(..., description=prompt_cls.zhongwen_description)),
            "yuewen": (str, Field(..., description=prompt_cls.yuewen_description)),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        return model
