#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to proofread 中文 subtitles."""

from __future__ import annotations

from typing import Any, ClassVar

from scinoephile.core.abcs import LLMQueryer
from scinoephile.core.abcs.llm_provider import LLMProvider
from scinoephile.core.zhongwen.proofreading import (
    zhongwen_proofreading_simplified_llm_text as _simplified_llm_text,
)
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreading_answer import (
    ZhongwenProofreadingAnswer,
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


class ZhongwenProofreadingLLMQueryer(
    LLMQueryer[
        ZhongwenProofreadingQuery,
        ZhongwenProofreadingAnswer,
        ZhongwenProofreadingTestCase,
    ],
):
    """Queries LLM to proofread 中文 subtitles."""

    text: ClassVar[type[ZhongwenProofreadingLLMText]] = (
        _simplified_llm_text.ZhongwenProofreadingSimplifiedLLMText
    )
    """Text strings to be used for corresponding with LLM."""

    def __init__(
        self,
        prompt_test_cases: list[ZhongwenProofreadingTestCase] | None = None,
        verified_test_cases: list[ZhongwenProofreadingTestCase] | None = None,
        provider: LLMProvider | None = None,
        *,
        text: type[ZhongwenProofreadingLLMText] = (
            _simplified_llm_text.ZhongwenProofreadingSimplifiedLLMText
        ),
        **kwargs: Any,
    ):
        """Initialize.

        Arguments:
            prompt_test_cases: test cases included in the prompt for few-shot learning
            verified_test_cases: test cases whose answers are verified and for which
              LLM need not be queried
            provider: provider to use for queries
            text: LLM text class specifying the language variant for prompts
            **kwargs: additional keyword arguments forwarded to the
              base queryer (for example, cache_dir_path, max_attempts, auto_verify)
        """
        super().__init__(
            prompt_test_cases=prompt_test_cases,
            verified_test_cases=verified_test_cases,
            provider=provider,
            **kwargs,
        )
        self.text = text
