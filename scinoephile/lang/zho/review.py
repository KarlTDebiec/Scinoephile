#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for standard Chinese review."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.dictionaries import DictionaryToolPrompt
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.prompts import PromptZhoHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.guided_review import GuidedReviewPrompt
from scinoephile.llms.pairwise_review import PairwiseReviewPrompt
from scinoephile.llms.review import ReviewPrompt

__all__ = [
    "GuidedReviewPromptZhoHans",
    "GuidedReviewPromptZhoHant",
    "PairwiseReviewPromptZhoHans",
    "PairwiseReviewPromptZhoHant",
    "ReviewPromptZhoHans",
    "ReviewPromptZhoHant",
]


class GuidedReviewPromptZhoHant(
    DictionaryToolPrompt, GuidedReviewPrompt, PromptZhoHant
):
    """LLM correspondence text for guided review of traditional Chinese."""

    dictionary_tool_name: ClassVar[str] = "lookup_dictionary"
    """Name of the dictionary lookup tool."""

    dictionary_tool_description: ClassVar[str] = (
        "查詢本地詞典中的粵語與普通話詞條；工具會自動判斷漢字、拼音或粵拼。"
    )
    """Description of the dictionary lookup tool."""

    dictionary_tool_query_description: ClassVar[str] = (
        "要查詢的普通話或粵語詞語，可以是漢字、拼音或粵拼。"
    )
    """Description of the dictionary lookup query parameter."""

    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責對中文字幕進行最後審核。
        你還會看到涵蓋同一段內容的參考字幕；參考字幕可以使用另一種語言，數量也可能不同。
        請利用參考字幕判斷中文字幕是否有明顯的聽寫、用字、名稱或前後一致性錯誤。
        不要翻譯參考字幕，也不要為了貼近參考字幕而改寫原本正確的中文。
        不要潤色或改動語氣、文法與措辭。
        只有確實需要修改時才返回完整修訂字幕與簡短備註，否則兩者均返回空字符串。""")
    """Base system prompt."""

    target_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for target fields in query."""

    target_desc_tpl: ClassVar[str] = "第 {idx} 條中文字幕"
    """Description template for target fields in query."""

    guide_pfx: ClassVar[str] = "cankao_"
    """Prefix for guide fields in query."""

    guide_desc_tpl: ClassVar[str] = "第 {idx} 條參考字幕"
    """Description template for guide fields in query."""

    output_pfx: ClassVar[str] = "xiugai_zhongwen_"
    """Prefix for output fields in answer."""


class GuidedReviewPromptZhoHans(GuidedReviewPromptZhoHant):
    """LLM correspondence text for guided review of simplified Chinese."""

    opencc_config = OpenCCConfig.t2s
    """Config for converting traditional Chinese characters from the parent class."""


class PairwiseReviewPromptZhoHant(
    DictionaryToolPrompt, PairwiseReviewPrompt, PromptZhoHant
):
    """LLM correspondence text for pairwise review of traditional Chinese."""

    dictionary_tool_name: ClassVar[str] = "lookup_dictionary"
    """Name of the dictionary lookup tool."""

    dictionary_tool_description: ClassVar[str] = (
        "查詢本地詞典中的粵語與普通話詞條；工具會自動判斷漢字、拼音或粵拼。"
    )
    """Description of the dictionary lookup tool."""

    dictionary_tool_query_description: ClassVar[str] = (
        "要查詢的普通話或粵語詞語，可以是漢字、拼音或粵拼。"
    )
    """Description of the dictionary lookup query parameter."""

    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        將一條中文字幕與一條對應的參考字幕逐條比較校對；參考字幕可以使用另一種語言。
        僅修正參考字幕足以證實的明顯聽寫、用字或名稱錯誤。
        不要翻譯參考字幕，也不要改寫原本正確的中文來配合參考字幕的措辭。
        如需修改，返回完整修訂後中文字幕與簡短備註；如無需修改，兩者均返回空字符串。
        只有當中文字幕完全沒有對應內容且應刪除時，才返回 "�"。""")
    """Base system prompt."""

    target: ClassVar[str] = "zhongwen"
    """Name of target field in query."""

    target_desc: ClassVar[str] = "要校對的中文字幕"
    """Description of target field in query."""

    reference: ClassVar[str] = "cankao"
    """Name of reference field in query."""

    reference_desc: ClassVar[str] = "對應的參考字幕"
    """Description of reference field in query."""

    output: ClassVar[str] = "xiugai"
    """Name of output field in answer."""

    note: ClassVar[str] = "beizhu"
    """Name of note field in answer."""


class PairwiseReviewPromptZhoHans(PairwiseReviewPromptZhoHant):
    """LLM correspondence text for pairwise review of simplified Chinese."""

    opencc_config = OpenCCConfig.t2s
    """Config for converting traditional Chinese characters from the parent class."""


class ReviewPromptZhoHant(ReviewPrompt, PromptZhoHant):
    """LLM correspondence text for traditional standard Chinese review."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責校對中文字幕。
        僅修正排版與錯別字等排版性/輸入性錯誤。
        不要潤色、改寫、改動語氣或用詞，也不要根據上下文改劇情。
        如果沒有明顯的錯別字或排版錯誤，請保持原文不變。
        對每條字幕，只有在需要修改時才提供修訂後的字幕。
        若需要修改，請返回完整的修訂後字幕，並給出說明修改內容的備註。
        若不需要修改，修訂後字幕與備註均返回空字符串。""")
    """Base system prompt."""

    # Query fields
    input_pfx: ClassVar[str] = "zimu_"
    """Prefix for input fields in query."""

    input_desc_tpl: ClassVar[str] = "第 {idx} 條字幕"
    """Description template for input fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "xiugai_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = "第 {idx} 條修改後的字幕"
    """Description template for output fields in answer."""

    note_pfx: ClassVar[str] = "beizhu_"
    """Prefix for note fields in answer."""

    note_desc_tpl: ClassVar[str] = "關於第 {idx} 條字幕修改的備註說明"
    """Description template for note fields in answer."""

    # Test case errors
    output_unmodified_err_tpl: ClassVar[str] = (
        "第 {idx} 條答案的修改文本與查詢文本相同。如果不需要修改，應提供空字符串。"
    )
    """Error template when output is present but unmodified."""

    note_missing_err_tpl: ClassVar[str] = (
        "第 {idx} 條答案的文本已被修改，但未提供備註。如需修改，必須附帶備註說明。"
    )
    """Error template when note is missing for a change."""

    output_missing_err_tpl: ClassVar[str] = (
        "第 {idx} 條答案的文本未修改，但提供了備註。如果不需要修改，應提供空字符串。"
    )
    """Error template when output is missing for a note."""


class ReviewPromptZhoHans(ReviewPromptZhoHant):
    """LLM correspondence text for simplified standard Chinese review."""

    opencc_config = OpenCCConfig.t2s
    """Config for converting traditional Chinese characters from the parent class."""
