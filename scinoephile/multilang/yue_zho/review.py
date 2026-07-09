#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prompts for reviewing written Cantonese using standard Chinese."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.dictionaries import DictionaryToolPrompt
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import PromptYueHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.guided_review import GuidedReviewPrompt
from scinoephile.llms.pairwise_review import PairwiseReviewPrompt

__all__ = [
    "YueZhoGuidedReviewPromptYueHans",
    "YueZhoGuidedReviewPromptYueHant",
    "YueZhoPairwiseReviewPromptYueHans",
    "YueZhoPairwiseReviewPromptYueHant",
]


class YueZhoGuidedReviewPromptYueHant(
    DictionaryToolPrompt, GuidedReviewPrompt, PromptYueHant
):
    """Prompt for guided review of traditional written Cantonese using Chinese."""

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

    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責為廣東話語音嘅粵文字幕做最後審核。
        作為指引，你會見到同一段內容嘅中文字幕；兩邊字幕數量未必相同。
        呢一輪唔係重寫字幕，而係做最後一層把關，只處理仍然明顯有問題嘅粵文轉寫。
        請專注檢查轉寫是否準確，尤其係聽錯字、寫錯字、人物稱呼前後唔一致，
        或者同整套字幕其他地方明顯衝突嘅情況。
        唔好評審文風、文法、語氣或者措辭；如果原句本身已經係合理嘅粵語講法，就唔好改。
        中文字幕只係參考，唔需要同粵文逐字對應。
        對於每一條粵文字幕，只有當你認為確實需要修改時，先回傳修訂後嘅完整粵文字幕。
        如果某條粵文字幕唔需要修改，請為該字幕回傳空字串。
        如果有修改，請同時用英文附上一段簡短備註，説明你改咗乜嘢。
        如果冇需要修改，備註欄同樣回傳空字串。""")
    """Base system prompt."""

    target_pfx: ClassVar[str] = "yuewen_"
    """Prefix for target fields in query."""

    target_desc_tpl: ClassVar[str] = "字幕 {idx} 嘅粵文轉寫"
    """Description template for target fields in query."""

    guide_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for guide fields in query."""

    guide_desc_tpl: ClassVar[str] = "中文字幕指引 {idx}"
    """Description template for guide fields in query."""

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

    note_missing_err_tpl: ClassVar[str] = (
        "答案入面嘅輸出 {idx} 有所修改，但冇提供任何備註。"
    )
    """Error template when note is missing for a revision."""

    output_missing_err_tpl: ClassVar[str] = (
        "答案入面嘅輸出 {idx} 冇修改，但卻提供咗備註。"
    )
    """Error template when output is missing for a note."""


class YueZhoGuidedReviewPromptYueHans(YueZhoGuidedReviewPromptYueHant):
    """Prompt for guided review of simplified written Cantonese using Chinese."""

    opencc_config = OpenCCConfig.hk2s
    """Config for converting traditional Chinese characters from the parent class."""


class YueZhoPairwiseReviewPromptYueHant(
    DictionaryToolPrompt, PairwiseReviewPrompt, PromptYueHant
):
    """Prompt for pairwise review of traditional written Cantonese using Chinese."""

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

    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責為廣東話語音嘅粵文字幕做校對。
        作為參考，你會見到一條對應嘅中文字幕。
        你嘅目標係糾正明顯嘅轉寫錯誤，主要係聽錯字、寫錯字，同其他一眼可見嘅轉寫問題。
        唔好為了貼近中文字幕而改寫本來已經正確嘅粵文。
        唔好調整語氣、語法、助詞、量詞或者措辭，除非嗰啲地方本身就係轉寫錯誤。
        只有當你認為原句明顯有誤時，先作修改。
        如果發現粵文同中文字幕完全對唔上，請回傳字符 "�"，並喺備註説明無對應。
        如果需要修改，回傳完整嘅修訂後粵文，並用英文一句話説明改動。
        如果冇修改，修訂後粵文同備註都回傳空字串。""")
    """Base system prompt."""

    target: ClassVar[str] = "yuewen"
    """Name of target field in query."""

    target_desc: ClassVar[str] = "要校對嘅粵文字幕轉寫"
    """Description of target field in query."""

    reference: ClassVar[str] = "zhongwen"
    """Name of reference field in query."""

    reference_desc: ClassVar[str] = "對應嘅中文字幕"
    """Description of reference field in query."""

    output: ClassVar[str] = "xiugai"
    """Name of output field in answer."""

    output_desc: ClassVar[str] = (
        '修訂後嘅粵文字幕；如果冇修改請回傳 ""，如需刪掉請回傳 "�"'
    )
    """Description of output field in answer."""

    note: ClassVar[str] = "beizhu"
    """Name of note field in answer."""

    note_desc: ClassVar[str] = "改動説明（英文）；如果冇修改請回傳空字串"
    """Description of note field in answer."""

    note_missing_err: ClassVar[str] = "修訂後嘅粵文有改動，但答案冇提供改動説明。"
    """Error when note is missing for a revision."""

    output_missing_err: ClassVar[str] = "修訂後嘅粵文冇改動，但答案提供咗改動説明。"
    """Error when output is missing for a note."""


class YueZhoPairwiseReviewPromptYueHans(YueZhoPairwiseReviewPromptYueHant):
    """Prompt for pairwise review of simplified written Cantonese using Chinese."""

    opencc_config = OpenCCConfig.hk2s
    """Config for converting traditional Chinese characters from the parent class."""
