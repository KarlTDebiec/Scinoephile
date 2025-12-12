#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text strings to be used for corresponding with an LLM in 中文."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.llms import Prompt

__all__ = ["ZhongwenPrompt"]


class ZhongwenPrompt(Prompt, ABC):
    """Text strings to be used for corresponding with an LLM in 中文."""

    schema_intro: ClassVar[str] = "你的回复必须是一个具有以下结构的 JSON 对象："
    """Text preceding schema description."""

    few_shot_intro: ClassVar[str] = "下面是一些查询及其预期答案的示例："
    """Text preceding few-shot examples."""

    few_shot_query_intro: ClassVar[str] = "示例查询："
    """Text preceding each few-shot example query."""

    few_shot_answer_intro: ClassVar[str] = "预期答案："
    """Text preceding each few-shot expected answer."""

    answer_invalid_pre: ClassVar[str] = (
        "你之前的回复不是有效的 JSON，或未符合预期的模式要求。错误详情："
    )
    """Text preceding answer validation errors."""

    answer_invalid_post: ClassVar[str] = (
        "请重新尝试，并仅返回一个符合该模式要求的有效 JSON 对象。"
    )
    """Text following answer validation errors."""

    test_case_invalid_pre: ClassVar[str] = (
        "你之前的回复是符合答案模式的有效 JSON，但不适用于当前的特定查询。错误详情："
    )
    """Text preceding test case validation errors."""

    test_case_invalid_post: ClassVar[str] = "请根据错误信息对你的回复进行相应修改。"
    """Text following test case validation errors."""
