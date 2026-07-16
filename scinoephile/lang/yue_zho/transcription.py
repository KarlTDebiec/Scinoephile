#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prompts for transcribing written Cantonese using standard Chinese references."""

from __future__ import annotations

from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import YUE_HANT_PROMPT_FIELDS
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_text_converted
from scinoephile.llms.delineation import DelineationPrompt
from scinoephile.llms.punctuation import PunctuationPrompt

__all__ = [
    "YueZhoDelineationPromptYueHans",
    "YueZhoDelineationPromptYueHant",
    "YueZhoPunctuationPromptYueHans",
    "YueZhoPunctuationPromptYueHant",
]

YueZhoDelineationPromptYueHant = DelineationPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責將廣東話口語嘅粵文字幕同對應嘅中文字幕對齊。
        你會收到一條中文字幕 (zhongwen_1) 同一條初步粵文字幕 (yuewen_1)，
        以及第二條中文字幕 (zhongwen_2) 同第二條初步粵文字幕 (yuewen_2)。
        請閲讀 zhongwen_1、zhongwen_2 同 yuewen_1、yuewen_2，
        調整 yuewen_1 同 yuewen_2 之間嘅分界，使內容同 zhongwen_1 同 zhongwen_2 對齊。
        即係將 yuewen_1 末尾嘅字符移到 yuewen_2 開頭，
        或者將 yuewen_2 開頭嘅字符移到 yuewen_1 末尾。
        請喺 yuewen_1_yidong 同 yuewen_2_yidong 返回調整後嘅粵文字幕。
        如果唔需要調整，請 yuewen_1_yidong 同 yuewen_2_yidong 都返回空字串。"""),
    ref_sub_1="zhongwen_1",
    ref_sub_1_desc="已知字幕1嘅中文",
    ref_sub_2="zhongwen_2",
    ref_sub_2_desc="已知字幕2嘅中文",
    target_sub_1="yuewen_1",
    target_sub_1_desc="初步字幕1嘅粵文",
    target_sub_2="yuewen_2",
    target_sub_2_desc="初步字幕2嘅粵文",
    target_subs_missing_err="查詢要有 yuewen_1、yuewen_2，或者兩個都有。",
    target_sub_1_shifted="yuewen_1_yidong",
    target_sub_1_shifted_desc="調整後字幕1嘅粵文",
    target_sub_2_shifted="yuewen_2_yidong",
    target_sub_2_shifted_desc="調整後字幕2嘅粵文",
    target_subs_unchanged_err=(
        "回答嘅 yuewen_1_yidong 同 yuewen_2_yidong 同查詢嘅 yuewen_1、yuewen_2 "
        "一樣；如果唔需要調整，yuewen_1_yidong 同 yuewen_2_yidong 要返空字串。"
    ),
    target_chars_changed_err_tpl=(
        "回答裏拼埋嘅 yuewen_1_yidong 同 yuewen_2_yidong 同查詢拼埋嘅 "
        "yuewen_1 同 yuewen_2 唔一致：\n"
        "期望: {expected}\n"
        "收到: {received}"
    ),
)
"""Text for LLM correspondence for traditional written Cantonese delineation."""

YueZhoDelineationPromptYueHans = YueZhoDelineationPromptYueHant.transformed(
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""Text for LLM correspondence for simplified written Cantonese delineation."""

YueZhoPunctuationPromptYueHant = PunctuationPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責將廣東話口語嘅粵文字幕同對應嘅中文字幕對齊。
        你會收到一條中文字幕，以及同一條字幕對應嘅多行粵文轉寫。
        多行粵文代表口語停頓拆開嘅行。
        你嘅主要任務係為粵文補上標點同空格。
        請先將所有粵文行整理成一行，再參考中文字幕補上標點同空格。
        必須包含所有粵文字，整理成一行。
        唔好從中文字幕拷貝漢字。
        只可以調整粵文嘅標點同空格以配合中文字幕。
        除咗標點同空格之外唔好改任何粵文內容。"""),
    src_1="yuewen_to_punctuate",
    src_1_desc="要整理同加標點嘅粵文字幕行",
    src_2="zhongwen",
    src_2_desc="對應嘅中文字幕",
    src_1_missing_err="查詢必須包含要整理同加標點嘅粵文字幕行。",
    src_2_missing_err="查詢必須包含對應嘅中文字幕。",
    output="yuewen_punctuated",
    output_desc="整理同加標點後嘅粵文字幕",
    output_missing_err="答案必須包含整理同加標點後嘅粵文字幕。",
    src_1_chars_changed_err_tpl=(
        "回答嘅 yuewen_punctuated 移除標點同空格後，同查詢入面拼埋嘅 "
        "yuewen_to_punctuate 唔一致：\n"
        "期望: {expected}\n"
        "收到: {received}"
    ),
)
"""Text for traditional written Cantonese/standard Chinese punctuation."""

YueZhoPunctuationPromptYueHans = YueZhoPunctuationPromptYueHant.transformed(
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""Text for simplified written Cantonese/standard Chinese punctuation."""
