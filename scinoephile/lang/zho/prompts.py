#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for standard Chinese."""

from __future__ import annotations

from typing import Final

from scinoephile.core.llms import PromptLocalizationFields

__all__ = ["ZHO_HANT_PROMPT_FIELDS"]


ZHO_HANT_PROMPT_FIELDS: Final[PromptLocalizationFields] = {
    "few_shot_intro": "下面是一些查詢及其預期答案的示例：",
    "few_shot_query_intro": "示例查詢：",
    "few_shot_answer_intro": "預期答案：",
    "answer_invalid_pre": "你之前的回覆不是有效的 JSON，或未符合預期的模式要求。",
    "answer_invalid_post": "請重新嘗試，並僅返回一個符合該模式要求的有效 JSON 對象。",
    "test_case_invalid_pre": (
        "你之前的回覆是符合答案模式的有效 JSON，但不適用於當前的特定查詢。錯誤詳情："
    ),
    "test_case_invalid_post": "請根據錯誤信息對你的回覆進行相應修改。",
}
"""Shared traditional standard Chinese LLM correspondence fields."""
