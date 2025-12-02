#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Merges transcribed 粤文 text based on corresponding 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.audio.cantonese.merging.merging_answer import MergingAnswer
from scinoephile.audio.cantonese.merging.merging_llm_text import MergingLLMText
from scinoephile.audio.cantonese.merging.merging_query import MergingQuery
from scinoephile.audio.cantonese.merging.merging_test_case import MergingTestCase
from scinoephile.core.abcs.llm_queryer import LLMQueryer


class MergingLLMQueryer(LLMQueryer[MergingQuery, MergingAnswer, MergingTestCase]):
    """Merges transcribed 粤文 text based on corresponding 中文."""

    answer_cls: ClassVar[type[MergingAnswer]] = MergingAnswer
    """Answer class."""
    query_cls: ClassVar[type[MergingQuery]] = MergingQuery
    """Query class."""
    test_case_cls: ClassVar[type[MergingTestCase]] = MergingTestCase
    """Test case class."""
    text: ClassVar[type[MergingLLMText]] = MergingLLMText
    """Text strings to be used for corresponding with LLM."""
