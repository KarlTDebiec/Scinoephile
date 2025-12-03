#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to shift 粤文 text between adjacent subtitles based on 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.audio.cantonese.shifting.shifting_answer import ShiftingAnswer
from scinoephile.audio.cantonese.shifting.shifting_llm_text import ShiftingLLMText
from scinoephile.audio.cantonese.shifting.shifting_query import ShiftingQuery
from scinoephile.audio.cantonese.shifting.shifting_test_case import ShiftingTestCase
from scinoephile.core.abcs import LLMQueryer


class ShiftingLLMQueryer(LLMQueryer[ShiftingQuery, ShiftingAnswer, ShiftingTestCase]):
    """Queries LLM to shift 粤文 text between adjacent subtitles based on 中文."""

    text: ClassVar[type[ShiftingLLMText]] = ShiftingLLMText
    """Text strings to be used for corresponding with LLM."""
