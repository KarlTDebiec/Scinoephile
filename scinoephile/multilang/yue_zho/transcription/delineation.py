#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Written Cantonese/standard Chinese transcription delineation."""

from __future__ import annotations

from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.eng.prompts import PromptEng
from scinoephile.lang.zho.script.conversion import (
    OpenCCConfig,
    get_zho_text_converted,
)
from scinoephile.llms.delineation import DelineationPrompt

__all__ = [
    "YueDelineationVsZhoPromptYueHans",
    "YueDelineationVsZhoPromptYueHant",
]


YueDelineationVsZhoPromptYueHant = DelineationPrompt(
    language=Language.yue_hant,
    **PromptEng.localization_kwargs,
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
    src_1_sub_1="zhongwen_1",
    src_1_sub_1_desc="已知字幕1嘅中文",
    src_1_sub_2="zhongwen_2",
    src_1_sub_2_desc="已知字幕2嘅中文",
    src_2_sub_1="yuewen_1",
    src_2_sub_1_desc="初步字幕1嘅粵文",
    src_2_sub_2="yuewen_2",
    src_2_sub_2_desc="初步字幕2嘅粵文",
    src_2_sub_1_sub_2_missing_err="查詢要有 yuewen_1、yuewen_2，或者兩個都有。",
    src_2_sub_1_shifted="yuewen_1_yidong",
    src_2_sub_1_shifted_desc="調整後字幕1嘅粵文",
    src_2_sub_2_shifted="yuewen_2_yidong",
    src_2_sub_2_shifted_desc="調整後字幕2嘅粵文",
    src_2_sub_1_sub_2_unchanged_err=(
        "回答嘅 yuewen_1_yidong 同 yuewen_2_yidong 同查詢嘅 yuewen_1、yuewen_2 "
        "一樣；如果唔需要調整，yuewen_1_yidong 同 yuewen_2_yidong 要返空字串。"
    ),
    src_2_chars_changed_err_tpl=(
        "回答裏拼埋嘅 yuewen_1_yidong 同 yuewen_2_yidong 同查詢拼埋嘅 "
        "yuewen_1 同 yuewen_2 唔一致：\n"
        "期望: {expected}\n"
        "收到: {received}"
    ),
)
"""Text for LLM correspondence for traditional written Cantonese delineation."""

YueDelineationVsZhoPromptYueHans = YueDelineationVsZhoPromptYueHant.transformed(
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""Text for LLM correspondence for simplified written Cantonese delineation."""
