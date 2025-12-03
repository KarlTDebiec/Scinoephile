#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to proofread 中文 subtitles."""

from __future__ import annotations

from typing import Any, ClassVar

from scinoephile.core.abcs import LLMQueryer, Prompt

from .answer import ZhongwenProofreadingAnswer
from .prompt import (
    ZhongwenProofreadingPromptBase,
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

    text: ClassVar[type[Prompt]] = ZhongwenProofreadingSimplifiedPrompt
    """Text strings to be used for corresponding with LLM."""

    def __init__(
        self,
        *,
        text: type[ZhongwenProofreadingPromptBase] | None = None,
        **kwargs: Any,
    ):
        """Initialize.

        Arguments:
            text: prompt text to use for LLM correspondence
            kwargs: Additional keyword arguments forwarded to LLMQueryer.
        """
        if text is not None:
            type(self).text = text

        super().__init__(**kwargs)
