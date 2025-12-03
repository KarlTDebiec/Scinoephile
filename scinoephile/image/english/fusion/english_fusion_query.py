#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for English OCR fusion queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.abcs import Query
from scinoephile.image.english.fusion.english_fusion_llm_text import (
    EnglishFusionLLMText,
)


class EnglishFusionQuery(Query, ABC):
    """Abstract base class for English OCR fusion queries."""

    text: ClassVar[type[EnglishFusionLLMText]]
    """Text strings to be used for corresponding with LLM."""

    @model_validator(mode="after")
    def validate_query(self) -> Self:
        """Ensure query is internally valid."""
        if not self.lens:
            raise ValueError(self.text.lens_missing_error)
        if not self.tesseract:
            raise ValueError(self.text.tesseract_missing_error)
        if self.lens == self.tesseract:
            raise ValueError(self.text.lens_tesseract_equal_error)
        return self

    @classmethod
    @cache
    def get_query_cls(
        cls, text: type[EnglishFusionLLMText] = EnglishFusionLLMText
    ) -> type[Self]:
        """Get concrete query class with provided text.

        Arguments:
            text: LLMText providing descriptions and messages
        Returns:
            Query type with appropriate fields and text
        """
        fields = {
            "lens": (str, Field(..., description=text.lens_description)),
            "tesseract": (str, Field(..., description=text.tesseract_description)),
        }
        return create_model(
            f"{cls.__name__}_{text.__name__}",
            __base__=cls,
            __module__=cls.__module__,
            text=(ClassVar[type[EnglishFusionLLMText]], text),
            **fields,
        )
