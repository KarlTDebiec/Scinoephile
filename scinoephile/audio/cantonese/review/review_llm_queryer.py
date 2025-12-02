#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reviews 粤文 text based on corresponding 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.audio.cantonese.review.review_answer import ReviewAnswer
from scinoephile.audio.cantonese.review.review_llm_text import ReviewLLMText
from scinoephile.audio.cantonese.review.review_query import ReviewQuery
from scinoephile.audio.cantonese.review.review_test_case import ReviewTestCase
from scinoephile.core.abcs import LLMQueryer


class ReviewLLMQueryer(LLMQueryer[ReviewQuery, ReviewAnswer, ReviewTestCase]):
    """Reviews 粤文 text based on corresponding 中文."""

    text: ClassVar[type[ReviewLLMText]] = ReviewLLMText
    """Text strings to be used for corresponding with LLM."""

    def get_answer_example(self, answer_cls: type[ReviewAnswer]) -> ReviewAnswer:
        """Example answer.

        Arguments:
            answer_cls: Answer class
        Returns:
            example answer
        """
        answer_values = {}
        for key in answer_cls.model_fields.keys():
            kind, idx = key.rsplit("_", 1)
            if kind == "yuewen":
                answer_values[key] = (
                    f"粤文 subtitle {idx} revised based on query's 中文 "
                    f"subtitle {idx}, or an empty string if no revision is necessary."
                )
            else:
                answer_values[key] = (
                    f"Note concerning revisions to 粤文 subtitle {idx}, "
                    f"or an empty string if no revision is necessary."
                )
        return answer_cls(**answer_values)
