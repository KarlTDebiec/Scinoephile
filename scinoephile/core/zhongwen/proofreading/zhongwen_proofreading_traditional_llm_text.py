#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 中文 proofreading (Traditional Chinese)."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreading_llm_text import (
    ZhongwenProofreadingLLMText,
)


class ZhongwenProofreadingTraditionalLLMText(ZhongwenProofreadingLLMText):
    """Text for LLM correspondence for 中文 proofreading (Traditional Chinese)."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        你負責校對由 OCR 辨識生成的中文字幕。
        你的任務僅限於糾正 OCR 辨識錯誤（例如錯字、漏字、字符混淆等），
        不得進行任何風格或語法上的潤飾，也不要添加或修改標點符號。
        對於每一條字幕，如有需要修改，請提供修改後的完整字幕，並附上一條說明所作修改的備註。
        如果不需要修改，請將修改後的字幕和備註都留空字串。""")
    """Base system prompt."""

    # Query descriptions
    zimu_description: ClassVar[str] = "第 {idx} 條字幕"
    """Description of 'zimu' field."""

    # Answer descriptions
    xiugai_description: ClassVar[str] = "第 {idx} 條修改後的字幕"
    """Description of 'xiugai' field."""

    beizhu_description: ClassVar[str] = "關於第 {idx} 條字幕修改的備註說明"
    """Description of 'beizhu' field."""

    # Test case validation errors
    zimu_xiugai_equal_error: ClassVar[str] = (
        "第 {idx} 條答案的修改文本與查詢文本相同。如果不需要修改，應提供空字串。"
    )
    """Error message when 'zimu' and 'xiugai' fields are equal."""

    beizhu_missing_error: ClassVar[str] = (
        "第 {idx} 條答案的文本已被修改，但未提供備註。如需修改，必須附帶備註說明。"
    )
    """Error message when 'xiugai' field is present but ''beizhu' field is missing."""

    xiugai_missing_error: ClassVar[str] = (
        "第 {idx} 條答案的文本未修改，但提供了備註。如果不需要修改，應提供空字串。"
    )
    """Error message when 'xiugai' field is missing but 'beizhu' field is present."""

    # Generic LLM text
    schema_intro: ClassVar[str] = "你的回覆必須是一個具有以下結構的 JSON 物件："
    few_shot_intro: ClassVar[str] = "下面是一些查詢及其預期答案的示例："
    few_shot_query_intro: ClassVar[str] = "示例查詢："
    few_shot_answer_intro: ClassVar[str] = "預期答案："
    answer_invalid_pre: ClassVar[str] = (
        "你之前的回覆不是有效的 JSON，或未符合預期的模式要求。錯誤詳情："
    )
    answer_invalid_post: ClassVar[str] = (
        "請重新嘗試，並僅返回一個符合該模式要求的有效 JSON 物件。"
    )
    test_case_invalid_pre: ClassVar[str] = (
        "你之前的回覆是符合答案模式的有效 JSON，但不適用於當前的特定查詢。錯誤詳情："
    )
    test_case_invalid_post: ClassVar[str] = "請根據錯誤資訊對你的回覆進行相應修改。"
