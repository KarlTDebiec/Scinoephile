#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for written Cantonese review."""

from __future__ import annotations

from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import PromptYueHant
from scinoephile.lang.zho.script.conversion import (
    OpenCCConfig,
    get_zho_text_converted,
)
from scinoephile.llms.guided_review import GuidedReviewPrompt
from scinoephile.llms.pairwise_review import PairwiseReviewPrompt
from scinoephile.llms.review import ReviewPrompt

__all__ = [
    "GuidedReviewPromptYueHans",
    "GuidedReviewPromptYueHant",
    "PairwiseReviewPromptYueHans",
    "PairwiseReviewPromptYueHant",
    "ReviewPromptYueHans",
    "ReviewPromptYueHant",
]


GuidedReviewPromptYueHant = GuidedReviewPrompt(
    language=Language.yue_hant,
    **PromptYueHant.localization_kwargs,
    base_system_prompt=dedent_and_compact("""
        你負責為粵文字幕做最後審核。
        你亦會見到同一段內容嘅參考字幕；參考字幕可以係另一種語言，字幕數量亦未必相同。
        請利用參考字幕判斷粵文有冇明顯嘅聽錯字、寫錯字、名稱錯誤或者前後矛盾。
        唔好翻譯參考字幕，亦唔好為咗貼近參考字幕而改寫本來正確嘅粵文。
        唔好潤色或者改動語氣、文法、助詞、量詞同措辭。
        只有確實需要修改時先回傳完整修訂後字幕同英文備註，否則兩者都回傳空字串。"""),
    target_pfx="yuewen_",
    target_desc_tpl="第 {idx} 條粵文字幕",
    guide_pfx="cankao_",
    guide_desc_tpl="第 {idx} 條參考字幕",
    output_pfx="xiugai_yuewen_",
)
"""LLM correspondence text for guided review of traditional Cantonese."""

GuidedReviewPromptYueHans = GuidedReviewPromptYueHant.transformed(
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""LLM correspondence text for guided review of simplified Cantonese."""

PairwiseReviewPromptYueHant = PairwiseReviewPrompt(
    language=Language.yue_hant,
    **PromptYueHant.localization_kwargs,
    base_system_prompt=dedent_and_compact("""
        將一條粵文字幕同一條對應嘅參考字幕作比較校對；參考字幕可以係另一種語言。
        只修正參考字幕足以證實嘅明顯聽錯字、寫錯字或者名稱錯誤。
        唔好翻譯參考字幕，亦唔好改寫本來正確嘅粵文去配合參考字幕嘅措辭。
        如果需要修改，回傳完整修訂後粵文同英文備註；如果唔需要修改，兩者都回傳空字串。
        只有當粵文完全冇對應內容而且應該刪除時，先回傳 "�"。"""),
    target="yuewen",
    target_desc="要校對嘅粵文字幕",
    reference="cankao",
    reference_desc="對應嘅參考字幕",
    output="xiugai",
    note="beizhu",
)
"""LLM correspondence text for pairwise review of traditional Cantonese."""

PairwiseReviewPromptYueHans = PairwiseReviewPromptYueHant.transformed(
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""LLM correspondence text for pairwise review of simplified Cantonese."""

ReviewPromptYueHant = ReviewPrompt(
    language=Language.yue_hant,
    **PromptYueHant.localization_kwargs,
    base_system_prompt=dedent_and_compact("""
        你負責校對粵文字幕。
        只修正排版、錯別字、OCR 或轉寫造成嘅明顯錯誤。
        唔好潤色、改寫、改動語氣或用詞，亦唔好根據上下文改劇情。
        如果原句本身已經係合理嘅粵語講法，請保持原文不變。
        對每條字幕，只有喺需要修改時先提供修訂後嘅完整字幕。
        若需要修改，請返回完整修訂後字幕，並給出說明修改內容嘅備註。
        若唔需要修改，修訂後字幕同備註都返回空字符串。"""),
    input_pfx="zimu_",
    input_desc_tpl="第 {idx} 條粵文字幕",
    output_pfx="xiugai_",
    output_desc_tpl="第 {idx} 條修改後嘅粵文字幕",
    note_pfx="beizhu_",
    note_desc_tpl="關於第 {idx} 條粵文字幕修改嘅備註說明",
    output_unmodified_err_tpl=(
        "第 {idx} 條答案嘅修改文本同查詢文本相同。如果唔需要修改，應提供空字符串。"
    ),
    note_missing_err_tpl=(
        "第 {idx} 條答案嘅文本已被修改，但未提供備註。如需修改，必須附帶備註說明。"
    ),
    output_missing_err_tpl=(
        "第 {idx} 條答案嘅文本未修改，但提供咗備註。如果唔需要修改，應提供空字符串。"
    ),
)
"""LLM correspondence text for traditional written Cantonese review."""

ReviewPromptYueHans = ReviewPromptYueHant.transformed(
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""LLM correspondence text for simplified written Cantonese review."""
