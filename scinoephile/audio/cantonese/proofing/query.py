#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription proofing queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.abcs import Query

from .llm_text import ProofingLLMText

__all__ = ["ProofingQuery"]


class ProofingQuery(Query, ABC):
    """Abstract base class for 粤文 transcription proofing queries."""

    text: ClassVar[type[ProofingLLMText]]
    """Text strings to be used for corresponding with LLM."""

    @model_validator(mode="after")
    def validate_query(self) -> Self:
        """Ensure query is internally valid."""
        if not self.zhongwen:
            raise ValueError(self.text.zhongwen_missing_error)
        if not self.yuewen:
            raise ValueError(self.text.yuewen_missing_error)
        return self

    @classmethod
    @cache
    def get_query_cls(cls, text: type[ProofingLLMText] = ProofingLLMText) -> type[Self]:
        """Get concrete query class with provided text.

        Arguments:
            text: LLMText providing descriptions and messages
        Returns:
            Query type with appropriate fields and text
        """
        fields = {
            "zhongwen": (str, Field(..., description=text.zhongwen_description)),
            "yuewen": (str, Field(..., description=text.yuewen_description)),
        }
        return create_model(
            f"{cls.__name__}_{text.__name__}",
            __base__=cls,
            __module__=cls.__module__,
            text=(ClassVar[type[ProofingLLMText]], text),
            **fields,
        )
