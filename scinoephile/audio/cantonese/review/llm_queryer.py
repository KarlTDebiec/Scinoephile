#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reviews 粤文 text based on corresponding 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.abcs import LLMQueryer

from .answer import ReviewAnswer
from .llm_text import ReviewLLMText
from .query import ReviewQuery
from .test_case import ReviewTestCase

__all__ = ["ReviewLLMQueryer"]


class ReviewLLMQueryer(LLMQueryer[ReviewQuery, ReviewAnswer, ReviewTestCase]):
    """Reviews 粤文 text based on corresponding 中文."""

    text: ClassVar[type[ReviewLLMText]] = ReviewLLMText
    """Text strings to be used for corresponding with LLM."""
