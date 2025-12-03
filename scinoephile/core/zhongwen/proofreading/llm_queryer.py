#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to proofread 中文 subtitles."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.abcs import LLMQueryer

from .answer import ZhongwenProofreadingAnswer
from .prompt import ZhongwenProofreadingPrompt
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

    text: ClassVar[type[ZhongwenProofreadingPrompt]] = ZhongwenProofreadingPrompt
    """Text strings to be used for corresponding with LLM."""
