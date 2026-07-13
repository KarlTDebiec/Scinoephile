#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for written Cantonese."""

from __future__ import annotations

from typing import Final

from scinoephile.core.llms import PromptLocalizationFields

__all__ = ["YUE_HANT_PROMPT_FIELDS"]


YUE_HANT_PROMPT_FIELDS: Final[PromptLocalizationFields] = {
    "few_shot_intro": "下面係一啲查詢同埋佢哋預期答案嘅例子：",
    "few_shot_query_intro": "例子查詢：",
    "few_shot_answer_intro": "預期答案：",
    "answer_invalid_pre": "你之前嘅回覆唔係有效嘅 JSON，或者未符合預期嘅模式要求。",
    "answer_invalid_post": (
        "請你再試一次，並且淨係返返一個符合該模式要求嘅有效 JSON 物件。"
    ),
    "test_case_invalid_pre": (
        "你之前嘅回覆係符合答案模式嘅有效 JSON，但唔適用於而家呢個特定查詢。錯誤詳情："
    ),
    "test_case_invalid_post": "請你根據錯誤信息對你嘅回覆作相應修改。",
}
"""Shared traditional written Cantonese LLM correspondence fields."""
