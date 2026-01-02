#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for 粤文."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.lang.zho.prompts import ZhoHansPrompt

__all__ = [
    "YueHansPrompt",
]


class YueHansPrompt(ZhoHansPrompt, ABC):
    """LLM correspondence text for 粤文."""

    # Prompt
    schema_intro: ClassVar[str] = "你嘅回覆一定要系一个有以下结构嘅 JSON 物件："
    """Text preceding schema description."""

    few_shot_intro: ClassVar[str] = "下面系一啲查询同埋佢哋预期答案嘅例子："
    """Text preceding few-shot examples."""

    few_shot_query_intro: ClassVar[str] = "例子查询："
    """Text preceding each few-shot example query."""

    few_shot_answer_intro: ClassVar[str] = "预期答案："
    """Text preceding each few-shot expected answer."""

    # Answer validation errors
    answer_invalid_pre: ClassVar[str] = (
        "你之前嘅回覆唔系有效嘅 JSON，或者未符合预期嘅模式要求。错误详情："
    )
    """Text preceding answer validation errors."""

    answer_invalid_post: ClassVar[str] = (
        "请你再试一次，并且净系返返一个符合该模式要求嘅有效 JSON 物件。"
    )
    """Text following answer validation errors."""

    # Test case validation errors
    test_case_invalid_pre: ClassVar[str] = (
        "你之前嘅回覆系符合答案模式嘅有效 JSON，但唔适用于而家呢个特定查询。错误详情："
    )
    """Text preceding test case validation errors."""

    test_case_invalid_post: ClassVar[str] = "请你根据错误信息对你嘅回覆作相应修改。"
    """Text following test case validation errors."""
