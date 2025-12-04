#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to fuse OCRed 中文 subtitles from Google Lens and PaddleOCR."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from scinoephile.core.abcs import LLMQueryer

from .answer import ZhongwenFusionAnswer
from .prompts import ZhongwenFusionPrompt, ZhongwenFusionSimplifiedPrompt
from .query import ZhongwenFusionQuery
from .test_case import ZhongwenFusionTestCase

__all__ = ["ZhongwenFusionLLMQueryer"]


class ZhongwenFusionLLMQueryer(
    LLMQueryer[ZhongwenFusionQuery, ZhongwenFusionAnswer, ZhongwenFusionTestCase], ABC
):
    """Queries LLM to fuse OCRed 中文 subtitles from Google Lens and PaddleOCR."""

    text: ClassVar[type[ZhongwenFusionPrompt]]
    """Text strings to be used for corresponding with LLM."""

    @classmethod
    @cache
    def get_queryer_cls(
        cls, text: type[ZhongwenFusionPrompt] = ZhongwenFusionSimplifiedPrompt
    ) -> type[Self]:
        """Get concrete queryer class with provided text.

        Arguments:
            text: Prompt class providing descriptions and messages
        Returns:
            LLMQueryer type with appropriate text
        """
        attrs = {
            "__module__": cls.__module__,
            "text": text,
        }
        return type(
            f"{cls.__name__}_{text.__name__}",
            (cls,),
            attrs,
        )
