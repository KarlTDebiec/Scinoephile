#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to proofread 中文 subtitles."""

from __future__ import annotations

from functools import cache
from typing import ClassVar

from scinoephile.core.abcs import LLMQueryer, Prompt

from .answer import ZhongwenProofreadingAnswer
from .prompts import (
    ZhongwenProofreadingPrompt,
    ZhongwenProofreadingSimplifiedPrompt,
)
from .query import ZhongwenProofreadingQuery
from .test_case import ZhongwenProofreadingTestCase

__all__ = ["ZhongwenProofreadingLLMQueryer"]


class ZhongwenProofreadingLLMQueryer(
    LLMQueryer[
        ZhongwenProofreadingQuery,
        ZhongwenProofreadingAnswer,
        ZhongwenProofreadingTestCase,
    ],
):
    """Queries LLM to proofread 中文 subtitles."""

    prompt_text: ClassVar[type[ZhongwenProofreadingPrompt]] = (
        ZhongwenProofreadingSimplifiedPrompt
    )
    """Text strings specialized for 中文 proofreading."""
    text: ClassVar[type[Prompt]] = prompt_text
    """Text strings to be used for corresponding with LLM."""

    @classmethod
    @cache
    def get_llm_queryer_cls(
        cls,
        text: type[ZhongwenProofreadingPrompt] = ZhongwenProofreadingSimplifiedPrompt,
    ) -> type[LLMQueryer]:
        """Get LLM queryer subclass with provided prompt text.

        Arguments:
            text: prompt text to use for LLM correspondence
        Returns:
            LLM queryer type with appropriate prompt text
        """
        return type(
            f"{cls.__name__}_{text.__name__}",
            (cls,),
            {
                "prompt_text": text,
                "text": text,
                "__module__": cls.__module__,
            },
        )
