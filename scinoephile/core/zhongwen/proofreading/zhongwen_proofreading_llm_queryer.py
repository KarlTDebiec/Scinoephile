#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to proofread 中文 subtitles."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.abcs import DynamicLLMQueryer
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreading_answer import (
    ZhongwenProofreadingAnswer,
)
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreading_llm_text import (
    ZhongwenProofreadingLLMText,
)
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreading_query import (
    ZhongwenProofreadingQuery,
)
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreading_test_case import (
    ZhongwenProofreadingTestCase,
)


class ZhongwenProofreadingLLMQueryer[
    TQuery: ZhongwenProofreadingQuery,
    TAnswer: ZhongwenProofreadingAnswer,
    TTestCase: ZhongwenProofreadingTestCase,
](
    DynamicLLMQueryer[
        ZhongwenProofreadingQuery,
        ZhongwenProofreadingAnswer,
        ZhongwenProofreadingTestCase,
    ]
):
    """Queries LLM to proofread 中文 subtitles."""

    text: ClassVar[type[ZhongwenProofreadingLLMText]] = ZhongwenProofreadingLLMText
    """Text strings to be used for corresponding with LLM."""

    @property
    def encountered_test_cases_source_str(self) -> str:
        """String representation of all test cases in the log."""
        test_case_log_str = "[\n"
        for test_case in self._encountered_test_cases.values():
            source_str: str = test_case.source_str
            test_case_log_str += f"{source_str},\n"
        test_case_log_str += "]"
        return test_case_log_str

    def get_answer_example(
        self, answer_cls: type[TAnswer]
    ) -> ZhongwenProofreadingAnswer:
        """Example answer.

        Arguments:
            answer_cls: Answer class
        Returns:
            Example answer
        """
        answer_values = {}
        for key in answer_cls.model_fields.keys():
            kind, idx = key.rsplit("_", 1)
            if kind == "xiugai":
                answer_values[key] = self.text.answer_example_xiugai_description.format(
                    idx=idx
                )
            else:
                answer_values[key] = self.text.answer_example_beizhu_description.format(
                    idx=idx
                )
        return answer_cls(**answer_values)
