#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for written Cantonese block review against standard Chinese."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.dictionaries import DictionaryToolPrompt
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import PromptYueHans, PromptYueHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.dual_n_to_n import DualNToNPrompt

__all__ = [
    "YueBlockReviewVsZhoPromptYueHans",
    "YueBlockReviewVsZhoPromptYueHant",
]


class YueBlockReviewVsZhoPromptYueHant(
    DictionaryToolPrompt, DualNToNPrompt, PromptYueHant
):
    """Text for traditional written Cantonese block review against standard Chinese."""

    # Dictionary tool
    dictionary_tool_name: ClassVar[str] = "lookup_dictionary"
    """Name of the dictionary lookup tool."""

    dictionary_tool_description: ClassVar[str] = (
        "查本地詞典入面嘅粵語同普通話詞條。工具會自動判斷查詢係漢字、拼音定粵拼。"
    )
    """Description of the dictionary lookup tool."""

    dictionary_tool_query_description: ClassVar[str] = (
        "要查嘅普通話或者粵語詞語，可以係漢字、拼音或者粵拼。"
    )
    """Description of the dictionary lookup query parameter."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責為廣東話語音嘅粵文字幕做最後審核。
        呢一輪唔係重寫字幕，而係做最後一層把關，只處理仍然明顯有問題嘅粵文轉寫。
        請專注檢查轉寫是否準確，尤其係聽錯字、寫錯字、人物稱呼前後唔一致，或者同整套字幕其他地方明顯衝突嘅情況。
        唔好評審文風、文法、語氣或者措辭；如果原句本身已經係合理嘅粵語講法，就唔好改。
        中文字幕只係參考，唔需要同粵文逐字對應。
        對於每一條粵文字幕，只有當你認為確實需要修改時，先回傳修訂後嘅完整粵文字幕。
        如果某條粵文字幕唔需要修改，請為該字幕回傳空字串。
        如果有修改，請同時用英文附上一段簡短備註，説明你改咗乜嘢。
        如果冇需要修改，備註欄同樣回傳空字串。
    """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "yuewen_"
    """Prefix for source one fields in query."""

    src_1_desc_tpl: ClassVar[str] = "字幕 {idx} 嘅粵文轉寫"
    """Description template for source one fields in query."""

    src_2_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for source two fields in query."""

    src_2_desc_tpl: ClassVar[str] = "字幕 {idx} 已知嘅中文字幕"
    """Description template for source two fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "xiugai_yuewen_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = (
        '字幕 {idx} 修訂後嘅粵文；如果冇任何修改，請回傳 ""。'
    )
    """Description template for output fields in answer."""

    note_pfx: ClassVar[str] = "beizhu_"
    """Prefix for note fields in answer."""

    note_desc_tpl: ClassVar[str] = (
        '字幕 {idx} 嘅備註（英文）；如果冇任何修改，請回傳 ""。'
    )
    """Description template for note fields in answer."""

    # Test case validation errors
    output_unmodified_err_tpl: ClassVar[str] = (
        "答案入面嘅輸出 {idx} 同查詢入面嘅來源一 {idx} 完全一樣；"
        '如果冇修改，必須回傳 ""。'
    )
    """Error template when output is present but unmodified relative to source one."""

    output_missing_note_present_err_tpl: ClassVar[str] = (
        "答案入面嘅輸出 {idx} 同查詢入面嘅來源一 {idx} 完全一樣，"
        '但卻提供咗備註；如果輸出係 ""，就唔可以有任何備註。'
    )
    """Error template when output is missing but note is present."""

    output_present_note_missing_err_tpl: ClassVar[str] = (
        "答案入面嘅輸出 {idx} 相對於查詢入面嘅來源一 {idx} 有所修改，"
        "但冇提供任何備註；如果有輸出，就必須同時提供備註。"
    )
    """Error template when output is present but note is missing."""


class YueBlockReviewVsZhoPromptYueHans(YueBlockReviewVsZhoPromptYueHant, PromptYueHans):
    """Text for simplified written Cantonese block review against standard Chinese."""

    opencc_config = OpenCCConfig.hk2s
    """Config for converting traditional Chinese characters from the parent class."""
