#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for written Cantonese."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.lang.zho.prompts import PromptZhoHans, PromptZhoHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig

__all__ = [
    "PromptYueHans",
    "PromptYueHant",
]


class PromptYueHant(PromptZhoHant, ABC):
    """LLM correspondence text for traditional written Cantonese."""

    # Prompt
    schema_intro: ClassVar[str] = "你嘅回覆一定要係一個有以下結構嘅 JSON 物件："
    """Text preceding schema description."""

    few_shot_intro: ClassVar[str] = "下面係一啲查詢同埋佢哋預期答案嘅例子："
    """Text preceding few-shot examples."""

    few_shot_query_intro: ClassVar[str] = "例子查詢："
    """Text preceding each few-shot example query."""

    few_shot_answer_intro: ClassVar[str] = "預期答案："
    """Text preceding each few-shot expected answer."""

    # Answer validation errors
    answer_invalid_pre: ClassVar[str] = (
        "你之前嘅回覆唔係有效嘅 JSON，或者未符合預期嘅模式要求。錯誤詳情："
    )
    """Text preceding answer validation errors."""

    answer_invalid_post: ClassVar[str] = (
        "請你再試一次，並且淨係返返一個符合該模式要求嘅有效 JSON 物件。"
    )
    """Text following answer validation errors."""

    # Test case validation errors
    test_case_invalid_pre: ClassVar[str] = (
        "你之前嘅回覆係符合答案模式嘅有效 JSON，但唔適用於而家呢個特定查詢。錯誤詳情："
    )
    """Text preceding test case validation errors."""

    test_case_invalid_post: ClassVar[str] = "請你根據錯誤信息對你嘅回覆作相應修改。"
    """Text following test case validation errors."""


class PromptYueHans(PromptYueHant, PromptZhoHans, ABC):
    """LLM correspondence text for simplified written Cantonese."""

    opencc_config = OpenCCConfig.hk2s
    """Config for converting traditional Chinese characters from the parent class."""
