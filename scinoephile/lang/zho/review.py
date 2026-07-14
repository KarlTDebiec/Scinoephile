#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for standard Chinese review."""

from __future__ import annotations

from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.llms.guided_review import GuidedReviewPrompt
from scinoephile.llms.pairwise_review import PairwiseReviewPrompt
from scinoephile.llms.review import ReviewPrompt

from .prompts import ZHO_HANT_PROMPT_FIELDS
from .script.conversion import OpenCCConfig, get_zho_text_converted

__all__ = [
    "GuidedReviewPromptZhoHans",
    "GuidedReviewPromptZhoHant",
    "PairwiseReviewPromptZhoHans",
    "PairwiseReviewPromptZhoHant",
    "ReviewPromptZhoHans",
    "ReviewPromptZhoHant",
]


GuidedReviewPromptZhoHant = GuidedReviewPrompt(
    language=Language.zho_hant,
    **ZHO_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責對中文字幕進行最後審核。
        你還會看到涵蓋同一段內容的參考字幕；參考字幕可以使用另一種語言，數量也可能不同。
        請利用參考字幕判斷中文字幕是否有明顯的聽寫、用字、名稱或前後一致性錯誤。
        不要翻譯參考字幕，也不要為了貼近參考字幕而改寫原本正確的中文。
        不要潤色或改動語氣、文法與措辭。
        只有確實需要修改的中文字幕才加入修改列表。每項修改必須包含字幕序號、
        完整修訂後文本與簡短備註。如果全部字幕都不需要修改，請返回空的修改列表。"""),
    targets="zhongwen",
    targets_desc="按順序排列、需要審核的中文字幕",
    guides="cankao",
    guides_desc="按順序排列、涵蓋同一段內容的參考字幕",
    revisions="xiugai_zhongwen",
    revisions_desc="需要修改的中文字幕；不需要修改的字幕不要包含在內",
    index="xuhao",
    index_desc="從 1 開始的字幕序號",
    text="wenben",
    target_text_desc="需要審核的中文字幕文本",
    guide_text_desc="參考字幕文本",
    revision_text_desc="修改後的完整中文字幕文本",
    note="beizhu",
    note_desc="關於中文字幕修改的簡短備註",
    target_indices_err="查詢目標字幕序號必須從 1 開始、連續並按順序排列。",
    guide_indices_err="查詢參考字幕序號必須從 1 開始、連續並按順序排列。",
    revision_indices_err="答案修改序號必須唯一並按升序排列。",
    revision_index_missing_err_tpl="答案修改序號 {idx} 在查詢目標字幕中不存在。",
    revision_unmodified_err_tpl=(
        "答案修改 {idx} 與查詢目標字幕 {idx} 相同；不需要修改的字幕必須從修改列表省略。"
    ),
)
"""LLM correspondence text for guided review of traditional Chinese."""

GuidedReviewPromptZhoHans = GuidedReviewPromptZhoHant.transformed(
    Language.zho_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.t2s),
)
"""LLM correspondence text for guided review of simplified Chinese."""

PairwiseReviewPromptZhoHant = PairwiseReviewPrompt(
    language=Language.zho_hant,
    **ZHO_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        將一條中文字幕與一條對應的參考字幕逐條比較校對；參考字幕可以使用另一種語言。
        僅修正參考字幕足以證實的明顯聽寫、用字或名稱錯誤。
        不要翻譯參考字幕，也不要改寫原本正確的中文來配合參考字幕的措辭。
        如需修改，返回完整修訂後中文字幕與簡短備註；如無需修改，兩者均返回空字符串。
        只有當中文字幕完全沒有對應內容且應刪除時，才返回 "�"。"""),
    target="zhongwen",
    target_desc="要校對的中文字幕",
    reference="cankao",
    reference_desc="對應的參考字幕",
    output="xiugai",
    note="beizhu",
)
"""LLM correspondence text for pairwise review of traditional Chinese."""

PairwiseReviewPromptZhoHans = PairwiseReviewPromptZhoHant.transformed(
    Language.zho_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.t2s),
)
"""LLM correspondence text for pairwise review of simplified Chinese."""

ReviewPromptZhoHant = ReviewPrompt(
    language=Language.zho_hant,
    **ZHO_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責校對中文字幕。
        僅修正排版與錯別字等排版性/輸入性錯誤。
        不要潤色、改寫、改動語氣或用詞，也不要根據上下文改劇情。
        如果沒有明顯的錯別字或排版錯誤，請保持原文不變。
        只有在字幕需要修改時才加入一項修改。每項修改必須包含字幕序號、
        修訂後的完整文本，以及說明修改內容的備註。
        如果全部字幕都不需要修改，請返回空的修改列表。"""),
    subtitles="zimu",
    subtitles_desc="按順序排列、需要校對的中文字幕",
    revisions="xiugai",
    revisions_desc="需要修改的中文字幕；不需要修改的字幕不要包含在內",
    index="xuhao",
    index_desc="從 1 開始的字幕序號",
    text="wenben",
    subtitle_text_desc="需要校對的中文字幕文本",
    revision_text_desc="修改後的完整中文字幕文本",
    note="beizhu",
    note_desc="關於中文字幕修改的備註說明",
    subtitle_indices_err="查詢字幕序號必須從 1 開始、連續並按順序排列。",
    revision_indices_err="答案修改序號必須唯一並按升序排列。",
    revision_index_missing_err_tpl="答案修改序號 {idx} 在查詢字幕中不存在。",
    revision_unmodified_err_tpl=(
        "答案修改 {idx} 與查詢字幕 {idx} 相同；不需要修改的字幕必須從修改列表省略。"
    ),
)
"""LLM correspondence text for traditional standard Chinese review."""

ReviewPromptZhoHans = ReviewPromptZhoHant.transformed(
    Language.zho_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.t2s),
)
"""LLM correspondence text for simplified standard Chinese review."""
