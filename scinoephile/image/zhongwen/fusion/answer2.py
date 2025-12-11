#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for Zhongwen OCR fusion answers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import Answer2
from scinoephile.core.models import get_cls_name

from .prompt2 import ZhongwenFusionPrompt2

__all__ = ["ZhongwenFusionAnswer2"]


class ZhongwenFusionAnswer2(Answer2, ABC):
    """Abstract base class for Zhongwen OCR fusion answers."""

    prompt_cls: ClassVar[type[ZhongwenFusionPrompt2]]  # type:ignore
    """Text strings to be used for corresponding with LLM."""

    @model_validator(mode="after")
    def validate_answer(self) -> Self:
        """Ensure answer is internally valid."""
        ronghe = getattr(self, "ronghe", None)
        beizhu = getattr(self, "beizhu", None)
        if not ronghe:
            raise ValueError(self.prompt_cls.ronghe_missing_error)
        if not beizhu:
            raise ValueError(self.prompt_cls.beizhu_missing_error)
        return self

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt_cls: type[ZhongwenFusionPrompt2] = ZhongwenFusionPrompt2,
    ) -> type[Self]:
        """Get concrete answer class with provided configuartion.

        Arguments:
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            Answer type with appropriate fields and text
        """
        name = get_cls_name(cls.__name__, prompt_cls.__name__)
        fields: dict[str, Any] = {
            "ronghe": (str, Field(..., description=prompt_cls.ronghe_description)),
            "beizhu": (str, Field(..., description=prompt_cls.beizhu_description)),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        return model
