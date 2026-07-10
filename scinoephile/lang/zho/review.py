#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for standard Chinese review."""

from __future__ import annotations

from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.prompts import PromptZhoHant
from scinoephile.lang.zho.script.conversion import (
    OpenCCConfig,
    get_zho_text_converted,
)
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


GuidedReviewPromptZhoHant = GuidedReviewPrompt(
    language=Language.zho_hant,
    schema_intro=PromptZhoHant.schema_intro,
    few_shot_intro=PromptZhoHant.few_shot_intro,
    few_shot_query_intro=PromptZhoHant.few_shot_query_intro,
    few_shot_answer_intro=PromptZhoHant.few_shot_answer_intro,
    answer_invalid_pre=PromptZhoHant.answer_invalid_pre,
    answer_invalid_post=PromptZhoHant.answer_invalid_post,
    difficulty_description=PromptZhoHant.difficulty_description,
    few_shot_description=PromptZhoHant.few_shot_description,
    verified_description=PromptZhoHant.verified_description,
    test_case_invalid_pre=PromptZhoHant.test_case_invalid_pre,
    test_case_invalid_post=PromptZhoHant.test_case_invalid_post,
    base_system_prompt=dedent_and_compact("""
        你負責對中文字幕進行最後審核。
        你還會看到涵蓋同一段內容的參考字幕；參考字幕可以使用另一種語言，數量也可能不同。
        請利用參考字幕判斷中文字幕是否有明顯的聽寫、用字、名稱或前後一致性錯誤。
        不要翻譯參考字幕，也不要為了貼近參考字幕而改寫原本正確的中文。
        不要潤色或改動語氣、文法與措辭。
        只有確實需要修改時才返回完整修訂字幕與簡短備註，否則兩者均返回空字符串。"""),
    target_pfx="zhongwen_",
    target_desc_tpl="第 {idx} 條中文字幕",
    guide_pfx="cankao_",
    guide_desc_tpl="第 {idx} 條參考字幕",
    output_pfx="xiugai_zhongwen_",
)
"""LLM correspondence text for guided review of traditional Chinese."""

GuidedReviewPromptZhoHans = GuidedReviewPromptZhoHant.transformed(
    Language.zho_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.t2s),
)
"""LLM correspondence text for guided review of simplified Chinese."""

PairwiseReviewPromptZhoHant = PairwiseReviewPrompt(
    language=Language.zho_hant,
    schema_intro=PromptZhoHant.schema_intro,
    few_shot_intro=PromptZhoHant.few_shot_intro,
    few_shot_query_intro=PromptZhoHant.few_shot_query_intro,
    few_shot_answer_intro=PromptZhoHant.few_shot_answer_intro,
    answer_invalid_pre=PromptZhoHant.answer_invalid_pre,
    answer_invalid_post=PromptZhoHant.answer_invalid_post,
    difficulty_description=PromptZhoHant.difficulty_description,
    few_shot_description=PromptZhoHant.few_shot_description,
    verified_description=PromptZhoHant.verified_description,
    test_case_invalid_pre=PromptZhoHant.test_case_invalid_pre,
    test_case_invalid_post=PromptZhoHant.test_case_invalid_post,
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
    schema_intro=PromptZhoHant.schema_intro,
    few_shot_intro=PromptZhoHant.few_shot_intro,
    few_shot_query_intro=PromptZhoHant.few_shot_query_intro,
    few_shot_answer_intro=PromptZhoHant.few_shot_answer_intro,
    answer_invalid_pre=PromptZhoHant.answer_invalid_pre,
    answer_invalid_post=PromptZhoHant.answer_invalid_post,
    difficulty_description=PromptZhoHant.difficulty_description,
    few_shot_description=PromptZhoHant.few_shot_description,
    verified_description=PromptZhoHant.verified_description,
    test_case_invalid_pre=PromptZhoHant.test_case_invalid_pre,
    test_case_invalid_post=PromptZhoHant.test_case_invalid_post,
    base_system_prompt=dedent_and_compact("""
        你負責校對中文字幕。
        僅修正排版與錯別字等排版性/輸入性錯誤。
        不要潤色、改寫、改動語氣或用詞，也不要根據上下文改劇情。
        如果沒有明顯的錯別字或排版錯誤，請保持原文不變。
        對每條字幕，只有在需要修改時才提供修訂後的字幕。
        若需要修改，請返回完整的修訂後字幕，並給出說明修改內容的備註。
        若不需要修改，修訂後字幕與備註均返回空字符串。"""),
    input_pfx="zimu_",
    input_desc_tpl="第 {idx} 條字幕",
    output_pfx="xiugai_",
    output_desc_tpl="第 {idx} 條修改後的字幕",
    note_pfx="beizhu_",
    note_desc_tpl="關於第 {idx} 條字幕修改的備註說明",
    output_unmodified_err_tpl=(
        "第 {idx} 條答案的修改文本與查詢文本相同。如果不需要修改，應提供空字符串。"
    ),
    note_missing_err_tpl=(
        "第 {idx} 條答案的文本已被修改，但未提供備註。如需修改，必須附帶備註說明。"
    ),
    output_missing_err_tpl=(
        "第 {idx} 條答案的文本未修改，但提供了備註。如果不需要修改，應提供空字符串。"
    ),
)
"""LLM correspondence text for traditional standard Chinese review."""

ReviewPromptZhoHans = ReviewPromptZhoHant.transformed(
    Language.zho_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.t2s),
)
"""LLM correspondence text for simplified standard Chinese review."""
