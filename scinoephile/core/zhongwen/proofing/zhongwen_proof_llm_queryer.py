#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreads 中文 subtitles."""

from __future__ import annotations

from functools import cached_property

from scinoephile.core.abcs import DynamicLLMQueryer
from scinoephile.core.zhongwen.proofing.abcs import (
    ZhongwenProofAnswer,
    ZhongwenProofQuery,
    ZhongwenProofTestCase,
)


class ZhongwenProofLLMQueryer[
    TQuery: ZhongwenProofQuery,
    TAnswer: ZhongwenProofAnswer,
    TTestCase: ZhongwenProofTestCase,
](DynamicLLMQueryer[ZhongwenProofQuery, ZhongwenProofAnswer, ZhongwenProofTestCase]):
    """Proofreads 中文 subtitles."""

    @cached_property
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        你负责校对中文字幕。
        对于每一条字幕，如果需要修改，请提供修改后的完整字幕，
        并附上一条说明所作修改的备注。
        如果不需要修改，请将修改后的字幕和备注都留空字符串。
        不要在字幕末尾随意添加句号。
        """

    @staticmethod
    def get_answer_example(answer_cls: type[TAnswer]) -> TAnswer:
        """Example answer."""
        answer_values = {}
        for key in answer_cls.model_fields.keys():
            kind, idx = key.rsplit("_", 1)
            if kind == "xiugai_":
                answer_values[key] = f"字幕 {idx} 的修改结果，如无需修改则为空字符串。"
            else:
                answer_values[key] = (
                    f"关于字幕 {idx} 修改的备注说明，如无需修改则为空字符串。"
                )
        return answer_cls(**answer_values)
