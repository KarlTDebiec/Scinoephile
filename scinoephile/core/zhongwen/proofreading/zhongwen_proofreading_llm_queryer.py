#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to proofread 中文 subtitles."""

from __future__ import annotations

from scinoephile.core.abcs import DynamicLLMQueryer
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreading_answer import (
    ZhongwenProofreadingAnswer,
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

    @property
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        你负责校对由 OCR 识别生成的中文字幕。
        你的任务仅限于纠正 OCR 识别错误（例如错字、漏字、字符混淆等），
        不得进行任何风格或语法上的润色，也不要添加或修改标点符号。
        对于每一条字幕，如有需要修改，请提供修改后的完整字幕，并附上一条说明所作修改的备注。
        如果不需要修改，请将修改后的字幕和备注都留空字符串。
        """

    @property
    def encountered_test_cases_source_str(self) -> str:
        """String representation of all test cases in the log."""
        test_case_log_str = "[\n"
        for test_case in self._encountered_test_cases.values():
            source_str: str = test_case.source_str
            test_case_log_str += f"{source_str},\n"
        test_case_log_str += "]"
        return test_case_log_str

    @staticmethod
    def get_answer_example(answer_cls: type[TAnswer]) -> TAnswer:
        """Example answer."""
        answer_values = {}
        for key in answer_cls.model_fields.keys():
            kind, idx = key.rsplit("_", 1)
            if kind == "xiugai":
                answer_values[key] = f"字幕 {idx} 的修改结果，如无需修改则为空字符串。"
            else:
                answer_values[key] = (
                    f"关于字幕 {idx} 修改的备注说明，如无需修改则为空字符串。"
                )
        return answer_cls(**answer_values)
