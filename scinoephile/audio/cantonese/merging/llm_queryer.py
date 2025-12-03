#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Merges transcribed 粤文 text based on corresponding 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.abcs.llm_queryer import LLMQueryer

from .answer import MergingAnswer
from .prompt import MergingPrompt
from .query import MergingQuery
from .test_case import MergingTestCase

__all__ = ["MergingLLMQueryer"]


class MergingLLMQueryer(LLMQueryer[MergingQuery, MergingAnswer, MergingTestCase]):
    """Merges transcribed 粤文 text based on corresponding 中文."""

    text: ClassVar[type[MergingPrompt]] = MergingPrompt
    """Text strings to be used for corresponding with LLM."""
