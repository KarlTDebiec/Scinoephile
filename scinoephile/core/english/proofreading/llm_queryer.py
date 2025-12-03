#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to proofread English subtitles."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.abcs import LLMQueryer

from .answer import EnglishProofreadingAnswer
from .prompt import EnglishProofreadingPrompt
from .query import EnglishProofreadingQuery
from .test_case import EnglishProofreadingTestCase

__all__ = ["EnglishProofreadingLLMQueryer"]


class EnglishProofreadingLLMQueryer(
    LLMQueryer[
        EnglishProofreadingQuery, EnglishProofreadingAnswer, EnglishProofreadingTestCase
    ]
):
    """Queries LLM to proofread English subtitles."""

    text: ClassVar[type[EnglishProofreadingPrompt]] = EnglishProofreadingPrompt
    """Text strings to be used for corresponding with LLM."""
