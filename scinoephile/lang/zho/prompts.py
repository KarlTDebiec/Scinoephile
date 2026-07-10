#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for standard Chinese."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core import Language
from scinoephile.core.llms import Prompt
from scinoephile.llms.prompt_definition import define_prompt

__all__ = ["PromptZhoHant"]


@define_prompt(Prompt, Language.zho_hant)
class PromptZhoHant:
    """LLM correspondence text for traditional standard Chinese."""

    # Prompt
    schema_intro: ClassVar[str] = "你的回覆必須是一個具有以下結構的 JSON 對象："
    """Text preceding schema description."""

    few_shot_intro: ClassVar[str] = "下面是一些查詢及其預期答案的示例："
    """Text preceding few-shot examples."""

    few_shot_query_intro: ClassVar[str] = "示例查詢："
    """Text preceding each few-shot example query."""

    few_shot_answer_intro: ClassVar[str] = "預期答案："
    """Text preceding each few-shot expected answer."""

    # Answer validation errors
    answer_invalid_pre: ClassVar[str] = (
        "你之前的回覆不是有效的 JSON，或未符合預期的模式要求。錯誤詳情："
    )
    """Text preceding answer validation errors."""

    answer_invalid_post: ClassVar[str] = (
        "請重新嘗試，並僅返回一個符合該模式要求的有效 JSON 對象。"
    )
    """Text following answer validation errors."""

    # Test case validation errors
    test_case_invalid_pre: ClassVar[str] = (
        "你之前的回覆是符合答案模式的有效 JSON，但不適用於當前的特定查詢。錯誤詳情："
    )
    """Text preceding test case validation errors."""

    test_case_invalid_post: ClassVar[str] = "請根據錯誤信息對你的回覆進行相應修改。"
    """Text following test case validation errors."""
