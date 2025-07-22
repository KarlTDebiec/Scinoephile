#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Merges transcribed 粤文 text to match 中文 text punctuation and spacing."""

from __future__ import annotations

from typing import override

from scinoephile.audio.cantonese.models import MergeAnswer, MergeQuery, MergeTestCase
from scinoephile.core.abcs import LLMQueryer


class CantoneseMerger(LLMQueryer[MergeQuery, MergeAnswer, MergeTestCase]):
    """Merges transcribed 粤文 texts to match 中文 text punctuation and spacing."""

    @property
    @override
    def answer_cls(self) -> type[MergeAnswer]:
        """Answer class."""
        return MergeAnswer

    @property
    @override
    def answer_example(self) -> MergeAnswer:
        """Example answer."""
        return MergeAnswer(yuewen_merged="粤文 merged")

    @property
    @override
    def answer_template(self) -> str:
        """Answer template."""
        return "粤文 merged:\n{yuewen_merged}\n"

    @property
    @override
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are a helpful assistant that merges multi-line 粤文 subtitles of
        spoken Cantonese to match the spacing and punctuation of a single-line
        中文 subtitle.
        Include all 粤文 characters and merge them into one line.
        All 汉字 in the output must come from the 粤文 input.
        No 汉字 in the output may come from the 中文 input.
        Adjust punctuation and spacing to match the 中文 input.
        Your response must be a JSON object with the following structure:
        """

    @property
    @override
    def query_cls(self) -> type[MergeQuery]:
        """Query class."""
        return MergeQuery

    @property
    @override
    def query_template(self) -> str:
        """Query template."""
        return "中文:\n{zhongwen}\n粤文 to merge:\n{yuewen_to_merge}\n"

    @property
    @override
    def test_case_cls(self) -> type[MergeTestCase]:
        """Test case class."""
        return MergeTestCase

    @override
    def _format_query_prompt(self, query: MergeQuery) -> str:
        """Format query prompt based on query.

        Arguments:
            query: Query to format
        Returns:
            Formatted query prompt
        """
        return self.query_template.format(
            zhongwen=query.zhongwen, yuewen_to_merge="\n".join(query.yuewen_to_merge)
        )
