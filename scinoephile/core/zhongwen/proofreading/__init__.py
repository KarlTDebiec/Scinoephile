#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 proofreading."""

from __future__ import annotations

from typing import Any

from scinoephile.core.series import Series
from scinoephile.core.zhongwen.proofreading import (
    zhongwen_proofreading_simplified_llm_text,
    zhongwen_proofreading_traditional_llm_text,
)
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreader import (
    ZhongwenProofreader,
)
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreading_answer import (
    ZhongwenProofreadingAnswer,
)
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreading_llm_queryer import (
    ZhongwenProofreadingLLMQueryer,
)
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreading_llm_text import (
    ZhongwenProofreadingLLMText,
)
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreading_query import (
    ZhongwenProofreadingQuery,
)
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreading_test_case import (
    ZhongwenProofreadingTestCase,
)

ZhongwenProofreadingSimplifiedLLMText = (
    zhongwen_proofreading_simplified_llm_text.ZhongwenProofreadingSimplifiedLLMText
)
ZhongwenProofreadingTraditionalLLMText = (
    zhongwen_proofreading_traditional_llm_text.ZhongwenProofreadingTraditionalLLMText
)


def get_zhongwen_proofread(
    series: Series,
    proofreader: ZhongwenProofreader | None = None,
    text: type[ZhongwenProofreadingLLMText] = ZhongwenProofreadingSimplifiedLLMText,
    **kwargs: Any,
) -> Series:
    """Get 中文 series proofread.

    Arguments:
        series: Series to proofread
        proofreader: ZhongwenProofreader to use
        text: LLM text class specifying the language variant for prompts
        kwargs: additional keyword arguments for ZhongwenProofreader.proofread
    Returns:
        proofread Series
    """
    if proofreader is None:
        proofreader = ZhongwenProofreader(text=text)

    proofread = proofreader.proofread(series, **kwargs)

    return proofread


__all__ = [
    "ZhongwenProofreader",
    "ZhongwenProofreadingAnswer",
    "ZhongwenProofreadingLLMQueryer",
    "ZhongwenProofreadingLLMText",
    "ZhongwenProofreadingSimplifiedLLMText",
    "ZhongwenProofreadingTraditionalLLMText",
    "ZhongwenProofreadingQuery",
    "ZhongwenProofreadingTestCase",
    "get_zhongwen_proofread",
]
