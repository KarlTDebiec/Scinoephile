#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reviews 粤文 text based on corresponding 中文."""

from __future__ import annotations

from functools import cached_property

from scinoephile.audio.cantonese.review.abcs import ReviewTestCase
from scinoephile.core.abcs import Answer, DynamicLLMQueryer, Query


class Reviewer[TQuery: Query, TAnswer: Answer, TTestCase: ReviewTestCase](
    DynamicLLMQueryer[Query, Answer, ReviewTestCase]
):
    """Reviews 粤文 text based on corresponding 中文."""

    @cached_property
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return "Review the 粤文 texts based on the corresponding 中文."

    @staticmethod
    def get_answer_example(answer_cls: type[TAnswer]) -> TAnswer:
        """Example answer."""
        answer_values = {}
        for key in answer_cls.model_fields.keys():
            kind, idx = key.rsplit("_", 1)
            if kind == "yuewen":
                answer_values[key] = (
                    f"粤文 text {idx} revised based on query's 中文 text {idx}, "
                    f"or an empty string if no revision is needed."
                )
            else:
                answer_values[key] = (
                    f"Note concerning revisions to 粤文 text {idx}, "
                    f"only if any revisions were made."
                )
        return answer_cls(**answer_values)
