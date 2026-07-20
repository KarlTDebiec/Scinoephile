#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for written Cantonese review."""

from __future__ import annotations

from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_text_converted
from scinoephile.llms.guided_review import GuidedReviewPrompt
from scinoephile.llms.review import ReviewPrompt

from .prompts import YUE_HANT_PROMPT_FIELDS

__all__ = [
    "GuidedReviewPromptYueHans",
    "GuidedReviewPromptYueHant",
    "ReviewPromptYueHans",
    "ReviewPromptYueHant",
]


GuidedReviewPromptYueHant = GuidedReviewPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責為粵文字幕做最後審核。
        你亦會見到同一段內容嘅參考字幕；參考字幕可以係另一種語言，字幕數量亦未必相同。
        請利用參考字幕判斷粵文有冇明顯嘅聽錯字、寫錯字、名稱錯誤或者前後矛盾。
        唔好翻譯參考字幕，亦唔好為咗貼近參考字幕而改寫本來正確嘅粵文。
        唔好潤色或者改動語氣、文法、助詞、量詞同措辭。
        只有確實需要修改嘅粵文字幕先加入修改列表。每項修改必須包含字幕序號、
        完整修訂後文本同粵文備註。如果要刪除多餘嘅目標字幕，修訂文本只填「�」。
        如果全部字幕都唔需要修改，請返回空嘅修改列表。"""),
    targets="yuewen",
    targets_desc="按順序排列、需要審核嘅粵文字幕",
    guides="cankao",
    guides_desc="按順序排列、涵蓋同一段內容嘅參考字幕",
    revisions="xiugai_yuewen",
    revisions_desc="需要修改嘅粵文字幕；唔需要修改嘅字幕唔好包括喺內",
    index="xuhao",
    index_desc="由 1 開始嘅字幕序號",
    text="wenben",
    target_text_desc="需要審核嘅粵文字幕文本",
    guide_text_desc="參考字幕文本",
    revision_text_desc="修改後嘅完整粵文字幕文本；如果要刪除字幕就只填「�」",
    note="beizhu",
    note_desc="關於粵文字幕修改嘅粵文備註",
    target_indices_err="查詢目標字幕序號必須由 1 開始、連續並按順序排列。",
    guide_indices_err="查詢參考字幕序號必須由 1 開始、連續並按順序排列。",
    revision_indices_err="答案修改序號必須唯一並按升序排列。",
    revision_index_missing_err_tpl="答案修改序號 {idx} 喺查詢目標字幕中不存在。",
    revision_unmodified_err_tpl=(
        "答案修改 {idx} 同查詢目標字幕 {idx} 相同；唔需要修改嘅字幕必須從修改列表省略。"
    ),
)
"""LLM correspondence text for guided review of traditional Cantonese."""

GuidedReviewPromptYueHans = GuidedReviewPromptYueHant.transformed(
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""LLM correspondence text for guided review of simplified Cantonese."""

ReviewPromptYueHant = ReviewPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責校對粵文字幕。
        只修正排版、錯別字、OCR 或轉寫造成嘅明顯錯誤。
        唔好潤色、改寫、改動語氣或用詞，亦唔好根據上下文改劇情。
        如果原句本身已經係合理嘅粵語講法，請保持原文不變。
        只有喺字幕需要修改時先加入一項修改。每項修改必須包含字幕序號、
        修訂後嘅完整文本，同埋說明修改內容嘅粵文備註。
        如果全部字幕都唔需要修改，請返回空嘅修改列表。"""),
    subtitles="zimu",
    subtitles_desc="按順序排列、需要校對嘅粵文字幕",
    revisions="xiugai",
    revisions_desc="需要修改嘅粵文字幕；唔需要修改嘅字幕唔好包括喺內",
    index="xuhao",
    index_desc="由 1 開始嘅字幕序號",
    text="wenben",
    subtitle_text_desc="需要校對嘅粵文字幕文本",
    revision_text_desc="修改後嘅完整粵文字幕文本",
    note="beizhu",
    note_desc="關於粵文字幕修改嘅粵文備註說明",
    subtitle_indices_err="查詢字幕序號必須由 1 開始、連續並按順序排列。",
    revision_indices_err="答案修改序號必須唯一並按升序排列。",
    revision_index_missing_err_tpl="答案修改序號 {idx} 喺查詢字幕中不存在。",
    revision_unmodified_err_tpl=(
        "答案修改 {idx} 同查詢字幕 {idx} 相同；唔需要修改嘅字幕必須從修改列表省略。"
    ),
)
"""LLM correspondence text for traditional written Cantonese review."""

ReviewPromptYueHans = ReviewPromptYueHant.transformed(
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""LLM correspondence text for simplified written Cantonese review."""
